import type { RunManifest } from "./contract.js";
import { parsePacketText, sha256, SUPPORTED_OPENCODE_VERSION } from "./contract.js";
import type { EvidenceStore } from "./lease-evidence.js";

type SessionInfo = { id: string; parentID?: string; version: string; time?: { created?: number } };
type ChatInput = {
  sessionID: string;
  agent?: string;
  model?: { providerID: string; modelID: string };
  messageID?: string;
  variant?: string;
};

export class RuntimeAdapter {
  private sessions = new Map<string, SessionInfo>();
  private completionWaiters = new Map<string, { resolve: () => void; reject: (error: Error) => void; timer: NodeJS.Timeout }>();
  private completedSessions = new Set<string>();
  private failedSessions = new Set<string>();

  constructor(private readonly store: EvidenceStore) {}

  onEvent(event: any): void {
    if (event?.type === "session.created") {
      this.onSessionCreated(event.properties?.info);
      return;
    }
    const sessionID = event?.properties?.sessionID;
    const waiter = sessionID ? this.completionWaiters.get(sessionID) : undefined;
    if (event.type === "session.idle") {
      this.completedSessions.add(sessionID);
      if (!waiter) return;
      clearTimeout(waiter.timer);
      this.completionWaiters.delete(sessionID);
      waiter.resolve();
    } else if (event.type === "session.error") {
      this.failedSessions.add(sessionID);
      const lease = this.store.findBySession(sessionID);
      if (lease) this.store.abort(lease.run_id, "child session reported a runtime error");
      if (!waiter) return;
      clearTimeout(waiter.timer);
      this.completionWaiters.delete(sessionID);
      waiter.reject(new Error("child session reported a runtime error"));
    }
  }

  waitForCompletion(sessionID: string, deadlineAt: string): Promise<void> {
    if (this.failedSessions.has(sessionID)) return Promise.reject(new Error("child session reported a runtime error"));
    if (this.completedSessions.has(sessionID)) return Promise.resolve();
    if (this.completionWaiters.has(sessionID)) throw new Error("child completion waiter already exists");
    const timeout = Date.parse(deadlineAt) - Date.now();
    if (timeout <= 0) throw new Error("child completion deadline expired");
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        this.completionWaiters.delete(sessionID);
        reject(new Error("child completion deadline expired"));
      }, timeout);
      this.completionWaiters.set(sessionID, { resolve, reject, timer });
    });
  }

  cancelCompletionWait(sessionID: string): void {
    const waiter = this.completionWaiters.get(sessionID);
    if (!waiter) return;
    clearTimeout(waiter.timer);
    this.completionWaiters.delete(sessionID);
  }

  onSessionCreated(info: SessionInfo): void {
    if (info.version !== SUPPORTED_OPENCODE_VERSION) throw new Error(`unsupported OpenCode version: ${info.version}`);
    const existing = this.sessions.get(info.id);
    if (existing) {
      if (existing.parentID !== info.parentID || existing.version !== info.version) throw new Error("conflicting child session identity");
      return;
    }
    this.sessions.set(info.id, info);
    const lease = this.store.active().find(
      (item) => item.state === "CREATED" && item.manifest.parent_session_id === info.parentID && !item.child_session_id,
    );
    if (lease) this.store.append(lease.run_id, "runtime.session.created", info);
  }

  onChatMessage(input: ChatInput, parts: Array<{ type?: string; text?: string }>): void {
    if (parts.length !== 1 || parts[0]?.type !== "text" || typeof parts[0].text !== "string") {
      if (parts.some((part) => part?.text?.includes("<design-gate "))) throw new Error("guard input must contain exactly one text part");
      return;
    }
    const text = parts[0].text;
    if (!text.includes("<design-gate ")) return;
    const packet = parsePacketText(text);
    const lease = this.store.findByNonce(packet.nonce);
    if (!lease) throw new Error("unknown Design manifest nonce");
    const manifest = lease.manifest;
    this.assertRoute(manifest, input);
    if (!input.messageID || input.messageID !== lease.input_message_id) throw new Error("input message ID mismatch");
    if (packet.manifestSha256 !== manifest.manifest_sha256 || packet.packetSha256 !== manifest.packet_sha256) {
      throw new Error("manifest or packet binding mismatch");
    }
    if (packet.stage !== manifest.stage) throw new Error("stage assignment mismatch");
    const session = this.sessions.get(input.sessionID);
    if (!session || session.parentID !== manifest.parent_session_id || session.version !== SUPPORTED_OPENCODE_VERSION) {
      throw new Error("child session binding mismatch");
    }
    this.store.provisionalBind(lease.run_id);
    this.store.append(lease.run_id, "runtime.chat.bound", {
      sessionID: input.sessionID,
      messageID: input.messageID,
      agent: input.agent,
      model: input.model,
      variant: input.variant,
      packet_sha256: sha256(packet.packet),
    });
  }

  assertRoute(manifest: RunManifest, input: ChatInput): void {
    if (input.sessionID !== this.store.get(manifest.run_id).child_session_id) throw new Error("unexpected child session");
    if (input.agent !== manifest.expected_agent) throw new Error("agent mismatch");
    if (input.model?.providerID !== manifest.expected_model.providerID || input.model.modelID !== manifest.expected_model.modelID) {
      throw new Error("model mismatch");
    }
    if (input.variant !== undefined && input.variant !== manifest.expected_variant) throw new Error("variant mismatch");
  }

  async assertAssistantParent(
    client: any,
    leaseRunID: string,
    assistantMessageID: string,
    directory: string,
  ): Promise<void> {
    const lease = this.store.get(leaseRunID);
    const response = await client.session.message({
      path: { id: lease.child_session_id, messageID: assistantMessageID },
      query: { directory },
    });
    const message = response?.data?.info ?? response?.info ?? response?.data ?? response;
    if (!message || message.role !== "assistant") throw new Error("ToolContext.messageID is not an AssistantMessage");
    if (message.id !== assistantMessageID || message.sessionID !== lease.child_session_id || message.parentID !== lease.input_message_id) {
      throw new Error("assistant message parent correlation mismatch");
    }
    if (message.agent !== lease.manifest.expected_agent || message.providerID !== lease.manifest.expected_model.providerID ||
        message.modelID !== lease.manifest.expected_model.modelID || message.variant !== lease.manifest.expected_variant) {
      throw new Error("assistant message route or variant mismatch");
    }
    this.store.append(lease.run_id, "runtime.assistant.verified", {
      assistantMessageID,
      sessionID: message.sessionID,
      parentID: message.parentID,
      role: message.role,
    });
  }
}
