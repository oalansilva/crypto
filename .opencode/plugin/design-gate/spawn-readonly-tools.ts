import { randomUUID } from "node:crypto";
import { spawn } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { tool } from "@opencode-ai/plugin";
import {
  applySafePatch,
  buildCritiquePacket,
  buildPacket,
  canonicalJson,
  decodeBase64,
  normativeDigestFromSources,
  parseAssessment,
  sha256,
  validateManifest,
  type RunManifest,
} from "./contract.js";
import type { EvidenceStore, Lease } from "./lease-evidence.js";
import { runNativeWriter } from "./native-writer.js";
import { assertGeneratedBlock, synthesizeAssessments } from "./assessments.js";
import type { RuntimeAdapter } from "./runtime-adapter.js";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const DEPLOYMENT_MANIFEST = path.join(HERE, "dist", "deployment-manifest.json");
const DEPLOYMENT_SIDECAR = path.join(HERE, "dist", "deployment-manifest.sha256");

function responseData<T>(response: any): T {
  return (response?.data ?? response) as T;
}

function assertSDKSuccess(response: any, operation: string): void {
  if (!response?.error) return;
  const error = response.error;
  const summary = typeof error === "string" ? error : canonicalJson({ name: error.name, message: error.message, data: error.data });
  throw new Error(`SDK ${operation} failed: ${summary.slice(0, 1000)}`);
}

function newMessageID(): string {
  return `msg_00${randomUUID().replaceAll("-", "").slice(0, 24)}`;
}

function textParts(parts: any[]): string {
  return parts.filter((part) => part?.type === "text" && typeof part.text === "string").map((part) => part.text).join("\n");
}

function textPartsDigest(parts: any[]): string {
  return sha256(canonicalJson(parts.filter((part) => part?.type === "text" && typeof part.text === "string").map((part) => ({ type: "text", text: part.text }))));
}

function runReadonlyProcess(executable: string, argv: string[], cwd: string, deadlineAt: string): Promise<{
  pid: number;
  status: number;
  stdout: string;
  stderr: string;
  process_started_at: string;
  executable: string;
  executable_sha256: string;
}> {
  return new Promise((resolve, reject) => {
    const processStartedAt = new Date().toISOString();
    const child = spawn(executable, argv, {
      cwd,
      env: { PATH: "/usr/bin:/bin", LANG: "C.UTF-8", LC_ALL: "C.UTF-8" },
      shell: false,
      stdio: ["ignore", "pipe", "pipe"],
    });
    let actualExecutable: string;
    try {
      actualExecutable = fs.realpathSync(`/proc/${child.pid}/exe`);
    } catch (error) {
      child.kill("SIGKILL");
      reject(new Error(`cannot attest readonly process executable: ${error instanceof Error ? error.message : String(error)}`));
      return;
    }
    const stdout: Buffer[] = [];
    const stderr: Buffer[] = [];
    let bytes = 0;
    let timedOut = false;
    const timeout = Date.parse(deadlineAt) - Date.now();
    if (timeout <= 0) {
      child.kill("SIGKILL");
      reject(new Error("OpenSpec deadline expired before execution"));
      return;
    }
    const deadlineTimer = setTimeout(() => {
      timedOut = true;
      child.kill("SIGKILL");
    }, timeout);
    const collect = (target: Buffer[]) => (chunk: Buffer) => {
      bytes += chunk.length;
      if (bytes > 4 * 1024 * 1024) {
        child.kill("SIGKILL");
        reject(new Error("OpenSpec output exceeded limit"));
        return;
      }
      target.push(chunk);
    };
    child.stdout.on("data", collect(stdout));
    child.stderr.on("data", collect(stderr));
    child.once("error", (error) => {
      clearTimeout(deadlineTimer);
      reject(error);
    });
    child.once("close", (code) => {
      clearTimeout(deadlineTimer);
      if (timedOut) {
        reject(new Error("OpenSpec process exceeded the Design lease deadline"));
        return;
      }
      resolve({
      pid: child.pid!,
      status: code ?? -1,
      stdout: Buffer.concat(stdout).toString("utf8"),
      stderr: Buffer.concat(stderr).toString("utf8"),
      process_started_at: processStartedAt,
      executable: actualExecutable,
      executable_sha256: sha256(fs.readFileSync(actualExecutable)),
      });
    });
  });
}

type DeploymentComponent = { path?: string; sha256?: string; unavailable?: boolean };
type DeploymentManifest = {
  build_id: string;
  protocol_version: string;
  files: Record<string, string>;
  build_identity: { path: string; sha256: string };
  native_writer: DeploymentComponent & { path: string; sha256: string };
  opencode: DeploymentComponent;
  openspec: DeploymentComponent & { interpreter?: { path: string; sha256: string; version: string } };
};

function verifyDeployment(manifest: RunManifest): DeploymentManifest {
  const bytes = fs.readFileSync(DEPLOYMENT_MANIFEST);
  const sidecar = fs.readFileSync(DEPLOYMENT_SIDECAR, "utf8").trim();
  const actual = sha256(bytes);
  if (actual !== sidecar || actual !== manifest.deployment_manifest_sha256) {
    throw new Error("deployment manifest digest mismatch");
  }
  const deployment = JSON.parse(bytes.toString("utf8")) as DeploymentManifest;
  if (deployment.build_id !== manifest.build_id) throw new Error("deployment build_id mismatch");
  if (deployment.protocol_version !== "design-gate.v1") throw new Error("deployment protocol mismatch");
  const projectRoot = path.resolve(HERE, "..", "..", "..");
  for (const [relative, expected] of Object.entries(deployment.files ?? {})) {
    const filePath = path.resolve(projectRoot, relative);
    if (!filePath.startsWith(`${projectRoot}${path.sep}`) || !fs.existsSync(filePath) || sha256(fs.readFileSync(filePath)) !== expected) {
      throw new Error(`deployment file mismatch: ${relative}`);
    }
  }
  if (!deployment.build_identity?.path || sha256(fs.readFileSync(deployment.build_identity.path)) !== deployment.build_identity.sha256 ||
      fs.readFileSync(deployment.build_identity.path, "utf8").trim() !== deployment.build_id) {
    throw new Error("deployment build identity mismatch");
  }
  for (const component of [deployment.native_writer, deployment.opencode, deployment.openspec]) {
    if (component?.unavailable) continue;
    if (!component?.path || !component.sha256 || !fs.existsSync(component.path) || sha256(fs.readFileSync(component.path)) !== component.sha256) {
      throw new Error(`deployment executable mismatch: ${component?.path ?? "missing"}`);
    }
  }
  if (!deployment.openspec.unavailable && (!deployment.openspec.interpreter?.path ||
      sha256(fs.readFileSync(deployment.openspec.interpreter.path)) !== deployment.openspec.interpreter.sha256)) {
    throw new Error("deployment OpenSpec interpreter mismatch");
  }
  const profilePath = `.opencode/agent/${manifest.expected_agent}.md`;
  if (deployment.files[profilePath] !== manifest.profile_sha256 || deployment.files["opencode.json"] !== manifest.config_sha256 ||
      deployment.files[".opencode/plugin/design-gate/schemas/assessment-v1.json"] !== manifest.schema_sha256) {
    throw new Error("manifest config/profile/schema digest mismatch");
  }
  return deployment;
}

function exactPath(lease: Lease, candidate: string): string {
  const resolved = path.resolve(candidate);
  if (!lease.manifest.exact_write_paths.some((item) => path.resolve(item) === resolved)) {
    throw new Error("artifact path is not in exact_write_paths");
  }
  return resolved;
}

export function createDesignGateTools(input: {
  client: any;
  store: EvidenceStore;
  runtime: RuntimeAdapter;
}) {
  const { client, store, runtime } = input;

  function validateCriticOutput(lease: Lease, output: string): void {
    const assessment = parseAssessment(output);
    const context = lease.manifest.critique_context!;
    const expected = lease.manifest.stage === "critique-a" ? "A" : "B";
    if (assessment.assessment !== expected || assessment.lineage_id !== context.lineage_id || assessment.round !== context.round ||
        assessment.source_digest !== context.source_digest || assessment.source_digest !== normativeDigestFromSources(lease.manifest)) {
      throw new Error("assessment identity, lineage, round, or normative digest mismatch");
    }
    const expectedInherited = new Map(context.inherited_blocking_findings.map((item) => [item.finding_id, item.prior_source_digest]));
    if (assessment.resolutions.length !== expectedInherited.size) throw new Error("assessment omitted an inherited blocking finding");
    for (const resolution of assessment.resolutions) {
      if (expectedInherited.get(resolution.finding_id) !== resolution.prior_source_digest) throw new Error("assessment inherited lineage mismatch");
    }
  }

  function expectedSynthesis(lease: Lease): Buffer {
    const dependency = (stage: RunManifest["stage"]) => {
      const item = lease.manifest.dependency_run_ids.map((runID) => store.get(runID)).find((candidate) => candidate.manifest.stage === stage);
      if (!item?.output_text_base64) throw new Error(`missing ${stage} output evidence`);
      return Buffer.from(item.output_text_base64, "base64");
    };
    const synthesis = synthesizeAssessments({
      assessmentABytes: dependency("critique-a"),
      assessmentBBytes: dependency("critique-b"),
      inheritedBlockingIds: lease.manifest.critique_context!.inherited_blocking_findings.map((item) => item.finding_id),
    });
    if (synthesis.verdict !== "PASS") throw new Error(`critique synthesis remains BLOCKED: ${synthesis.digest}`);
    return synthesis.generatedBlockBytes;
  }

  async function completeStage(lease: Lease, directory: string) {
    if (!lease.child_session_id || !lease.input_message_id) throw new Error("child binding is incomplete");
    const messagesResponse = await client.session.messages({ path: { id: lease.child_session_id }, query: { directory } });
    assertSDKSuccess(messagesResponse, "session.messages");
    const messages = responseData<Array<{ info?: { id?: string; parentID?: string; role?: string; finish?: string }; parts?: any[] }>>(messagesResponse);
    const matches = messages.filter((item) => item.info?.role === "assistant" && item.info.parentID === lease.input_message_id);
    const terminal = matches.filter((item) => item.info?.finish && item.info.finish !== "tool-calls");
    const completed = terminal.length === 1 ? terminal[0] : undefined;
    if (!completed) throw new Error("child terminal AssistantMessage is absent or ambiguous");
    const parts = completed.parts ?? [];
    if (!completed.info?.id || parts.length === 0 || !textParts(parts).trim()) throw new Error("child returned no correlatable usable output");

    if (lease.manifest.stage === "critique-a" || lease.manifest.stage === "critique-b") {
      validateCriticOutput(lease, textParts(parts));
      if (!lease.provisional) throw new Error("critic input was not provisionally bound");
      await runtime.assertAssistantParent(client, lease.run_id, completed.info.id, directory);
      store.finalBind(lease.run_id, completed.info.id);
    }

    for (const artifact of lease.manifest.expected_artifacts.filter((item) => item.required)) {
      if (!fs.existsSync(artifact.path) || !fs.lstatSync(artifact.path).isFile() || fs.lstatSync(artifact.path).isSymbolicLink()) {
        throw new Error(`required artifact missing or unsafe: ${artifact.path}`);
      }
    }
    store.setOutput(lease.run_id, completed.info.id, textParts(parts), textPartsDigest(parts));
    store.append(lease.run_id, "stage.output", {
      assistant_message_id: completed.info.id,
      part_count: parts.length,
      output_sha256: textPartsDigest(parts),
    });
    store.finalize(lease.run_id, "PASS", { stage: lease.manifest.stage, artifacts: lease.manifest.expected_artifacts });
    return {
      title: `Design stage ${lease.manifest.stage}`,
      output: canonicalJson({ run_id: lease.run_id, child_session_id: lease.child_session_id, verdict: "PASS" }),
      metadata: { run_id: lease.run_id, child_session_id: lease.child_session_id },
    };
  }

  const designSpawnStage = tool({
    description: "Start or collect one manifest-bound Design author or zero-tool critic stage.",
    args: {
      action: tool.schema.enum(["start", "collect"]).optional(),
      run_id: tool.schema.string().optional(),
      manifest_json: tool.schema.string().optional(),
      packet_base64: tool.schema.string().optional(),
    },
    async execute(args, context) {
      let lease: Lease | undefined;
      try {
        if (args.action === "collect") {
          if (!args.run_id) throw new Error("collect requires run_id");
          lease = store.get(args.run_id);
          if (lease.manifest.parent_session_id !== context.sessionID || path.resolve(lease.manifest.worktree) !== path.resolve(context.worktree)) {
            throw new Error("collect subject or worktree mismatch");
          }
          if (!lease.child_session_id) throw new Error("collect requires a spawned child");
          try {
            return await completeStage(lease, context.directory);
          } catch (error) {
            if (!(error instanceof Error) || !/terminal AssistantMessage is absent/.test(error.message)) throw error;
            await runtime.waitForCompletion(lease.child_session_id, lease.manifest.deadline_at);
            return await completeStage(lease, context.directory);
          }
        }
        if (!args.manifest_json || !args.packet_base64) throw new Error("start requires manifest_json and packet_base64");
        const rawManifest = JSON.parse(args.manifest_json);
        if (rawManifest.parent_session_id === "PARENT_SESSION_IS_BOUND_BY_TOOL_CONTEXT") rawManifest.parent_session_id = context.sessionID;
        const manifest = validateManifest(rawManifest);
        if (context.agent !== "build") {
          throw new Error("design_spawn_stage is orchestrator-only");
        }
        if (manifest.parent_session_id !== context.sessionID) throw new Error("manifest parent does not match orchestrator session");
        if (path.resolve(manifest.worktree) !== path.resolve(context.worktree)) throw new Error("manifest worktree mismatch");
        verifyDeployment(manifest);
        const packet = decodeBase64(args.packet_base64);
        if (sha256(packet) !== manifest.packet_sha256) throw new Error("packet digest mismatch");
        if ((manifest.stage === "critique-a" || manifest.stage === "critique-b") && !packet.equals(buildCritiquePacket(manifest))) {
          throw new Error("critic packet is not the canonical normative packet");
        }
        lease = store.create(manifest);
        const inputMessageID = newMessageID();
        const createdResponse = await client.session.create({
          body: { parentID: context.sessionID, title: `Design ${manifest.stage}: ${manifest.change_id}` },
          query: { directory: context.worktree },
        });
        assertSDKSuccess(createdResponse, "session.create");
        const child = responseData<{ id: string; parentID?: string; version?: string }>(createdResponse);
        if (!child?.id || child.parentID !== context.sessionID) throw new Error("SDK returned an invalid child session");
        runtime.onSessionCreated({ id: child.id, parentID: child.parentID, version: child.version ?? manifest.opencode_version });
        store.setChild(manifest.run_id, child.id, inputMessageID);
        const prompt = buildPacket(manifest, packet);
        const promptRequest = {
          path: { id: child.id },
          query: { directory: context.worktree },
          body: {
            messageID: inputMessageID,
            agent: manifest.expected_agent,
            model: manifest.expected_model,
            parts: [{ type: "text", text: prompt }],
          },
        };
        if (typeof client.session.promptAsync === "function" && typeof client.session.messages === "function") {
          const promptResponse = await client.session.promptAsync(promptRequest);
          assertSDKSuccess(promptResponse, "session.promptAsync");
          return {
            title: `Design stage ${manifest.stage} started`,
            output: canonicalJson({ run_id: manifest.run_id, child_session_id: child.id, verdict: "STARTED", next_action: "collect" }),
            metadata: { run_id: manifest.run_id, child_session_id: child.id },
          };
        }
        const promptResponse = await client.session.prompt(promptRequest);
        assertSDKSuccess(promptResponse, "session.prompt");
        const completed = responseData<{ info?: { id?: string; parentID?: string; finish?: string }; parts?: any[] }>(promptResponse);
        const parts = completed.parts ?? [];
        if (!completed.info?.id || completed.info.parentID !== inputMessageID || completed.info.finish === "tool-calls" || !completed.info.finish || parts.length === 0 || !textParts(parts).trim()) {
          throw new Error("child returned no correlatable usable output");
        }
        if (manifest.stage === "critique-a" || manifest.stage === "critique-b") {
          validateCriticOutput(store.get(manifest.run_id), textParts(parts));
          await runtime.assertAssistantParent(client, manifest.run_id, completed.info.id, context.directory);
          store.finalBind(manifest.run_id, completed.info.id);
        }
        for (const artifact of manifest.expected_artifacts.filter((item) => item.required)) {
          if (!fs.existsSync(artifact.path)) throw new Error(`required artifact missing: ${artifact.path}`);
        }
        store.setOutput(manifest.run_id, completed.info.id, textParts(parts), textPartsDigest(parts));
        store.append(manifest.run_id, "stage.output", { assistant_message_id: completed.info.id, part_count: parts.length, output_sha256: textPartsDigest(parts) });
        store.finalize(manifest.run_id, "PASS", { stage: manifest.stage, artifacts: manifest.expected_artifacts });
        return { title: `Design stage ${manifest.stage}`, output: canonicalJson({ run_id: manifest.run_id, child_session_id: child.id, verdict: "PASS" }), metadata: { run_id: manifest.run_id, child_session_id: child.id } };
      } catch (error) {
        if (lease) store.abort(lease.run_id, error instanceof Error ? error.message : String(error));
        throw error;
      }
    },
  });

  const designOpenSpecReadonly = tool({
    description: "Run an allowlisted read-only OpenSpec status, instructions, or validate command.",
    args: {
      run_id: tool.schema.string(),
      operation: tool.schema.enum(["status", "instructions", "validate"]),
      change: tool.schema.string(),
      artifact: tool.schema.string().optional(),
    },
    async execute(args, context) {
      const lease = store.assertReadonly(args.run_id, context.sessionID);
      if (!["status", "instructions", "validate"].includes(args.operation) || !/^[a-z0-9][a-z0-9-]{0,127}$/.test(args.change)) {
        throw new Error("OpenSpec operation or change is not allowlisted");
      }
      if (path.resolve(context.worktree) !== path.resolve(lease.manifest.worktree)) throw new Error("OpenSpec worktree mismatch");
      const deployment = verifyDeployment(lease.manifest);
      if (!deployment.openspec.path || !path.isAbsolute(deployment.openspec.path) || !deployment.openspec.interpreter?.path) throw new Error("OpenSpec runner is not deployment-approved");
      let argv: string[];
      if (args.operation === "status") argv = ["status", "--change", args.change, "--json"];
      else if (args.operation === "validate") argv = ["validate", args.change];
      else {
        if (!args.artifact || !/^[a-z0-9-]+$/.test(args.artifact)) throw new Error("allowlisted artifact is required");
        argv = ["instructions", args.artifact, "--change", args.change, "--json"];
      }
      if (args.change !== lease.manifest.change_id) throw new Error("OpenSpec change mismatch");
      const result = await runReadonlyProcess(deployment.openspec.interpreter.path, [deployment.openspec.path, ...argv], lease.manifest.worktree, lease.manifest.deadline_at);
      store.assertReadonly(args.run_id, context.sessionID);
      if (result.executable !== fs.realpathSync(deployment.openspec.interpreter.path) || result.executable_sha256 !== deployment.openspec.interpreter.sha256) {
        throw new Error("OpenSpec runtime interpreter identity mismatch");
      }
      store.append(args.run_id, "openspec.readonly", {
        argv,
        pid: result.pid,
        ppid: process.pid,
        executable: result.executable,
        executable_sha256: result.executable_sha256,
        entrypoint: deployment.openspec.path,
        entrypoint_sha256: deployment.openspec.sha256,
        process_started_at: result.process_started_at,
        build_id: lease.build_id,
        module_instance_id: lease.module_instance_id,
        protocol_version: lease.protocol_version,
        status: result.status,
        stdout_sha256: sha256(result.stdout ?? ""),
        stderr_sha256: sha256(result.stderr ?? ""),
      });
      if (result.status !== 0) throw new Error(`OpenSpec failed (${result.status}): ${result.stderr}`);
      return { title: `openspec ${args.operation}`, output: result.stdout, metadata: { status: result.status } };
    },
  });

  const designArtifactWrite = tool({
    description: "Write one exact manifest artifact through the guarded Linux writer.",
    args: {
      run_id: tool.schema.string(),
      manifest_nonce: tool.schema.string(),
      manifest_sha256: tool.schema.string(),
      operation_nonce: tool.schema.string(),
      exact_path: tool.schema.string(),
      base_sha256: tool.schema.string(),
      full_content_base64: tool.schema.string().optional(),
      safe_patch_json: tool.schema.string().optional(),
    },
    async execute(args, context) {
      const lease = store.get(args.run_id);
      try {
        if (lease.manifest.nonce !== args.manifest_nonce) throw new Error("manifest nonce mismatch");
        if (lease.manifest.manifest_sha256 !== args.manifest_sha256) throw new Error("manifest digest mismatch");
        if (lease.child_session_id !== context.sessionID || lease.manifest.expected_agent !== context.agent) {
          throw new Error("writer subject mismatch");
        }
        const resolvedPath = exactPath(lease, args.exact_path);
        const argsHash = sha256(canonicalJson(args));
        await runtime.assertAssistantParent(client, lease.run_id, context.messageID, context.directory);
        if (lease.state === "CREATED") store.finalBind(lease.run_id, context.messageID);
        else if (lease.assistant_message_id !== context.messageID) throw new Error("assistant message changed during stage");
        const call = store.consumeCall(lease.run_id, args.operation_nonce, argsHash);
        const exists = fs.existsSync(resolvedPath);
        const current = exists ? fs.readFileSync(resolvedPath) : Buffer.alloc(0);
        const expectedBase = args.base_sha256 === "-" ? null : args.base_sha256;
        if ((exists ? sha256(current) : null) !== expectedBase) throw new Error("base digest is stale");
        const operationCount = Number(args.full_content_base64 !== undefined) + Number(args.safe_patch_json !== undefined);
        if (operationCount !== 1) throw new Error("exactly one writer operation is required");
        const content = args.full_content_base64 !== undefined
          ? decodeBase64(args.full_content_base64)
          : applySafePatch(current, JSON.parse(args.safe_patch_json!));
        if (content.equals(current)) throw new Error("writer operation must change artifact bytes");
        if (lease.manifest.stage === "critique-synthesis") {
          assertGeneratedBlock(content, expectedSynthesis(lease));
        }
        const deployment = verifyDeployment(lease.manifest);
        const helperStartedAt = new Date().toISOString();
        const result = runNativeWriter({
          worktree: lease.manifest.worktree,
          exactPath: resolvedPath,
          expectedBaseSha256: expectedBase,
          content,
          executable: deployment.native_writer.path,
          expectedExecutableSha256: deployment.native_writer.sha256,
          timeoutMs: Math.min(30_000, Math.max(1, Date.parse(lease.manifest.deadline_at) - Date.now())),
        });
        store.recordWrite(lease.run_id, {
          callID: call.callID,
          operation_nonce: args.operation_nonce,
          path: resolvedPath,
          before_sha256: result.before_sha256,
          after_sha256: result.after_sha256,
        });
        store.append(lease.run_id, "writer.completed", {
          callID: call.callID,
          operation_nonce: args.operation_nonce,
          path: resolvedPath,
          executable: deployment.native_writer.path,
          executable_sha256: deployment.native_writer.sha256,
          process_started_at: helperStartedAt,
          module_instance_id: args.operation_nonce,
          ...result,
        });
        return { title: `Wrote ${path.basename(resolvedPath)}`, output: canonicalJson(result), metadata: result };
      } catch (error) {
        store.abort(lease.run_id, error instanceof Error ? error.message : String(error));
        throw error;
      }
    },
  });

  function beforeTool(toolName: string, sessionID: string, callID: string, args: any): void {
    if (toolName === "design_spawn_stage") {
      if (args?.action === "collect") {
        const lease = store.get(args.run_id);
        if (lease.manifest.parent_session_id !== sessionID) throw new Error("Design collect is not bound to this orchestrator");
        return;
      }
      if (store.active().length) throw new Error("Design gate lease denies concurrent spawn");
      return;
    }
    if (toolName === "design_artifact_write") {
      const lease = store.get(args.run_id);
      const argsHash = sha256(canonicalJson(args));
      store.registerCall(lease.run_id, args.operation_nonce, callID, argsHash, sessionID);
      return;
    }
    const active = store.active();
    if (active.length === 0) return;
    if (toolName === "design_openspec_readonly") {
      const lease = store.get(args.run_id);
      if (lease.manifest.parent_session_id === sessionID) return;
    }
    throw new Error(`Design gate lease denies tool ${toolName}`);
  }

  function afterTool(toolName: string, sessionID: string, callID: string, output: unknown): void {
    const lease = store.findBySession(sessionID);
    if (!lease) return;
    store.append(lease.run_id, "runtime.tool.after", {
      tool: toolName,
      sessionID,
      callID,
      output_sha256: sha256(canonicalJson(output)),
    });
  }

  return {
    tool: {
      design_spawn_stage: designSpawnStage,
      design_openspec_readonly: designOpenSpecReadonly,
      design_artifact_write: designArtifactWrite,
    },
    beforeTool,
    afterTool,
  };
}
