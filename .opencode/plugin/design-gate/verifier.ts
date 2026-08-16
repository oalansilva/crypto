import { DatabaseSync } from "node:sqlite";
import fs from "node:fs";
import path from "node:path";
import { BUILD_ID, PROTOCOL_VERSION, buildPacket, canonicalJson, manifestDigest, normativeDigestFromSources, parseAssessment, parsePacketText, sha256, type RunManifest } from "./contract.js";
import type { Lease } from "./lease-evidence.js";
import { assertGeneratedBlock, synthesizeAssessments } from "./assessments.js";

type JournalEvent = {
  sequence: number;
  event: string;
  data: any;
  previous_hash: string | null;
  hash: string;
};

function checkedBytes(filePath: string): Buffer {
  if (!fs.existsSync(filePath)) throw new Error(`evidence file missing: ${filePath}`);
  return fs.readFileSync(filePath);
}

function verifySidecar(filePath: string): Buffer {
  const bytes = checkedBytes(filePath);
  if (checkedBytes(`${filePath}.sha256`).toString("utf8").trim() !== sha256(bytes)) throw new Error(`sidecar mismatch: ${filePath}`);
  return bytes;
}

function verifyRuntimeDatabase(databasePath: string, lease: Lease, events: JournalEvent[]): void {
  if (!lease.child_session_id || !lease.input_message_id || !lease.assistant_message_id || !lease.output_message_id) throw new Error("runtime binding is incomplete");
  const database = new DatabaseSync(databasePath, { readOnly: true });
  try {
    const session = database.prepare("SELECT parent_id, directory, version, time_created FROM session WHERE id = ?").get(lease.child_session_id) as any;
    if (!session || session.parent_id !== lease.manifest.parent_session_id || path.resolve(session.directory) !== path.resolve(lease.manifest.worktree) || session.version !== lease.manifest.opencode_version) {
      throw new Error("runtime session does not match lease");
    }
    if (session.time_created < Date.parse(lease.process_started_at)) throw new Error("runtime session predates guard process");
    const input = database.prepare("SELECT session_id, data FROM message WHERE id = ?").get(lease.input_message_id) as any;
    const assistant = database.prepare("SELECT session_id, data FROM message WHERE id = ?").get(lease.assistant_message_id) as any;
    const output = database.prepare("SELECT session_id, data FROM message WHERE id = ?").get(lease.output_message_id) as any;
    if (!input || input.session_id !== lease.child_session_id || !assistant || assistant.session_id !== lease.child_session_id || !output || output.session_id !== lease.child_session_id) {
      throw new Error("runtime message session mismatch");
    }
    const inputData = JSON.parse(input.data);
    if (inputData.role !== "user" || inputData.agent !== lease.manifest.expected_agent ||
        inputData.model?.providerID !== lease.manifest.expected_model.providerID || inputData.model?.modelID !== lease.manifest.expected_model.modelID ||
        inputData.model?.variant !== lease.manifest.expected_variant) throw new Error("runtime input route mismatch");
    const inputParts = database.prepare("SELECT data FROM part WHERE message_id = ? AND session_id = ? ORDER BY time_created, id")
      .all(lease.input_message_id, lease.child_session_id) as Array<{ data: string }>;
    const parsedInputParts = inputParts.map((item) => JSON.parse(item.data));
    if (parsedInputParts.length !== 1 || parsedInputParts[0]?.type !== "text" || typeof parsedInputParts[0].text !== "string") {
      throw new Error("runtime input must contain exactly one text part");
    }
    const packet = parsePacketText(parsedInputParts[0].text);
    if (packet.nonce !== lease.manifest.nonce || packet.manifestSha256 !== lease.manifest.manifest_sha256 ||
        packet.packetSha256 !== lease.manifest.packet_sha256 || parsedInputParts[0].text !== buildPacket(lease.manifest, packet.packet)) {
      throw new Error("runtime input packet binding mismatch");
    }
    const assistantData = JSON.parse(assistant.data);
    if (assistantData.role !== "assistant" || assistantData.parentID !== lease.input_message_id || assistantData.agent !== lease.manifest.expected_agent ||
        assistantData.providerID !== lease.manifest.expected_model.providerID || assistantData.modelID !== lease.manifest.expected_model.modelID ||
        assistantData.variant !== lease.manifest.expected_variant) {
      throw new Error("runtime assistant route mismatch");
    }
    const outputData = JSON.parse(output.data);
    if (outputData.role !== "assistant" || outputData.parentID !== lease.input_message_id || outputData.agent !== lease.manifest.expected_agent ||
        outputData.providerID !== lease.manifest.expected_model.providerID || outputData.modelID !== lease.manifest.expected_model.modelID ||
        outputData.variant !== lease.manifest.expected_variant) throw new Error("runtime output route mismatch");
    const writerMessageIDs = lease.writes.map((write) => write.assistant_message_id);
    if (writerMessageIDs.some((messageID) => !messageID) || new Set(writerMessageIDs).size !== lease.writes.length) {
      throw new Error("runtime writer messages are missing or reused");
    }
    for (const write of lease.writes) {
      const messageID = write.assistant_message_id;
      const message = database.prepare("SELECT session_id, data FROM message WHERE id = ?").get(messageID) as any;
      if (!message || message.session_id !== lease.child_session_id) throw new Error("runtime writer message session mismatch");
      const data = JSON.parse(message.data);
      if (data.role !== "assistant" || data.parentID !== lease.input_message_id || data.agent !== lease.manifest.expected_agent ||
          data.providerID !== lease.manifest.expected_model.providerID || data.modelID !== lease.manifest.expected_model.modelID ||
          data.variant !== lease.manifest.expected_variant) throw new Error("runtime writer assistant route mismatch");
      const toolParts = database.prepare("SELECT data FROM part WHERE message_id = ? AND session_id = ? ORDER BY time_created, id")
        .all(messageID, lease.child_session_id!).map((item: any) => JSON.parse(item.data))
        .filter((item: any) => item.type === "tool");
      if (toolParts.length !== 1 || toolParts[0].tool !== "design_artifact_write") throw new Error("runtime writer tool-call count mismatch");
      const part = toolParts[0];
      const registered = events.find((event) => event.event === "writer.call.registered" && event.data?.callID === write.callID && event.data?.operationNonce === write.operation_nonce);
      if (part.callID !== write.callID || part.state?.status !== "completed" || !registered || sha256(canonicalJson(part.state.input)) !== registered.data.argsHash) {
        throw new Error("runtime writer tool-call correlation mismatch");
      }
    }
    const parts = database.prepare("SELECT data FROM part WHERE message_id = ? AND session_id = ? ORDER BY time_created, id")
      .all(lease.output_message_id, lease.child_session_id) as Array<{ data: string }>;
    const textParts = parts.map((item) => JSON.parse(item.data)).filter((item) => item?.type === "text" && typeof item.text === "string").map((item) => ({ type: "text", text: item.text }));
    const outputText = textParts.map((item) => item.text).join("\n");
    if (!textParts.length || sha256(canonicalJson(textParts)) !== lease.output_parts_sha256 || sha256(outputText) !== lease.output_text_sha256 ||
        Buffer.from(outputText, "utf8").toString("base64") !== lease.output_text_base64) throw new Error("runtime output bytes mismatch");
  } finally {
    database.close();
  }
}

type VerifyInput = {
  evidenceRoot: string;
  runID: string;
  deploymentManifestPath: string;
  runtimeDatabasePath: string;
};

export function verifyRunEvidence(input: VerifyInput): { verdict: "PASS" | "BLOCKED"; evidence_sha256: string; events: number } {
  return verifyRunEvidenceInternal(input, new Set(), new Map());
}

function verifyRunEvidenceInternal(
  input: VerifyInput,
  visiting: Set<string>,
  descendantBaselines: Map<string, string | null>,
): { verdict: "PASS" | "BLOCKED"; evidence_sha256: string; events: number } {
  if (!/^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$/.test(input.runID)) throw new Error("unsafe run ID");
  if (visiting.has(input.runID)) throw new Error("cyclic evidence dependency");
  visiting.add(input.runID);
  const runRoot = path.join(path.resolve(input.evidenceRoot), input.runID);
  const leaseBytes = verifySidecar(path.join(runRoot, "lease.json"));
  const lease = JSON.parse(leaseBytes.toString("utf8")) as Lease;
  if (canonicalJson(lease) + "\n" !== leaseBytes.toString("utf8")) throw new Error("lease is not canonical");
  if (lease.run_id !== input.runID || lease.manifest.manifest_sha256 !== manifestDigest(lease.manifest as RunManifest)) throw new Error("lease manifest mismatch");
  if (lease.build_id !== BUILD_ID || lease.protocol_version !== PROTOCOL_VERSION || lease.module_instance_id.length === 0 ||
      !Number.isInteger(lease.owner_pid) || !Number.isInteger(lease.owner_ppid) || !lease.owner_executable || !/^[a-f0-9]{64}$/.test(lease.owner_executable_sha256)) {
    throw new Error("TCB process identity is incomplete");
  }
  const guard = lease.manifest.guard_process;
  if (!guard || guard.pid !== lease.owner_pid || guard.ppid !== lease.owner_ppid || guard.executable !== lease.owner_executable ||
      guard.executable_sha256 !== lease.owner_executable_sha256 || guard.process_started_at !== lease.process_started_at ||
      guard.module_instance_id !== lease.module_instance_id) throw new Error("pre-spawn guard identity mismatch");

  const journalPath = path.join(runRoot, "journal.jsonl");
  const journalBytes = verifySidecar(journalPath);
  const events = journalBytes.toString("utf8").split("\n").filter(Boolean).map((line) => JSON.parse(line) as JournalEvent);
  let previous: string | null = null;
  for (const [index, event] of events.entries()) {
    const { hash, ...unsigned } = event;
    if (event.sequence !== index + 1 || event.previous_hash !== previous || sha256(canonicalJson(unsigned)) !== hash) {
      throw new Error(`journal chain mismatch at ${index + 1}`);
    }
    previous = hash;
  }
  const expectedTerminal = lease.state === "CLOSED" ? "lease.closed" : lease.state === "ABORTED" ? "lease.aborted" : null;
  const terminalIndex = expectedTerminal ? events.findIndex((event) => event.event === expectedTerminal) : -1;
  const observationalAfterTerminal = new Set(["runtime.tool.after", "runtime.assistant.verified"]);
  if (terminalIndex < 0 || events.slice(terminalIndex + 1).some((event) => !observationalAfterTerminal.has(event.event))) {
    throw new Error("evidence is not terminal or has a post-terminal mutation");
  }
  const first = (name: string) => events.findIndex((event) => event.event === name);
  const required = ["lease.created", "runtime.session.created", "child.created", "binding.provisional", "runtime.chat.bound", "runtime.assistant.verified", "binding.final", "stage.output.bound", "stage.output", "lease.finalizing", expectedTerminal!];
  let prior = -1;
  for (const name of required) {
    const index = first(name);
    if (index <= prior) throw new Error(`journal semantic sequence mismatch: ${name}`);
    prior = index;
  }
  const outputEvent = events.find((event) => event.event === "stage.output");
  if (outputEvent?.data?.assistant_message_id !== lease.output_message_id || outputEvent?.data?.output_sha256 !== lease.output_parts_sha256) {
    throw new Error("journal output binding mismatch");
  }

  const deploymentBytes = fs.readFileSync(input.deploymentManifestPath);
  const deploymentDigest = sha256(deploymentBytes);
  const deploymentSidecar = fs.readFileSync(path.join(path.dirname(input.deploymentManifestPath), "deployment-manifest.sha256"), "utf8").trim();
  if (deploymentDigest !== deploymentSidecar || deploymentDigest !== lease.manifest.deployment_manifest_sha256) throw new Error("deployment digest mismatch");
  const deployment = JSON.parse(deploymentBytes.toString("utf8"));
  if (deployment.build_id !== lease.build_id || deployment.protocol_version !== lease.protocol_version) throw new Error("deployment identity mismatch");
  if (sha256(fs.readFileSync(deployment.build_identity.path)) !== deployment.build_identity.sha256 ||
      fs.readFileSync(deployment.build_identity.path, "utf8").trim() !== deployment.build_id) throw new Error("build identity file mismatch");
  const projectRoot = path.resolve(path.dirname(input.deploymentManifestPath), "..", "..", "..", "..");
  for (const [relative, expected] of Object.entries(deployment.files as Record<string, string>)) {
    if (sha256(fs.readFileSync(path.join(projectRoot, relative))) !== expected) throw new Error(`deployed file mismatch: ${relative}`);
  }
  const profilePath = `.opencode/agent/${lease.manifest.expected_agent}.md`;
  if (deployment.files[profilePath] !== lease.manifest.profile_sha256 || deployment.files["opencode.json"] !== lease.manifest.config_sha256 ||
      deployment.files[".opencode/plugin/design-gate/schemas/assessment-v1.json"] !== lease.manifest.schema_sha256) {
    throw new Error("manifest profile/config/schema mismatch");
  }
  for (const component of [deployment.native_writer, deployment.opencode, deployment.openspec]) {
    if (component.unavailable) continue;
    if (sha256(fs.readFileSync(component.path)) !== component.sha256) throw new Error(`deployed executable mismatch: ${component.path}`);
  }
  if (!deployment.openspec.unavailable && sha256(fs.readFileSync(deployment.openspec.interpreter.path)) !== deployment.openspec.interpreter.sha256) {
    throw new Error("deployed OpenSpec interpreter mismatch");
  }
  const openSpecEvents = events.filter((event) => event.event === "openspec.readonly");
  for (const event of openSpecEvents) {
    if (!Number.isInteger(event.data?.pid) || event.data?.ppid !== lease.owner_pid || event.data?.status !== 0 ||
        event.data?.executable !== deployment.openspec.interpreter.path || event.data?.executable_sha256 !== deployment.openspec.interpreter.sha256 ||
        event.data?.entrypoint !== deployment.openspec.path || event.data?.entrypoint_sha256 !== deployment.openspec.sha256 ||
        !/^[a-f0-9]{64}$/.test(event.data?.stdout_sha256) || !/^[a-f0-9]{64}$/.test(event.data?.stderr_sha256)) {
      throw new Error("OpenSpec journal process identity mismatch");
    }
  }
  if (lease.writes.length) {
    const registered = events.filter((event) => event.event === "writer.call.registered");
    const consumed = events.filter((event) => event.event === "writer.call.consumed");
    const recorded = events.filter((event) => event.event === "writer.recorded");
    const completed = events.filter((event) => event.event === "writer.completed");
    if ([registered, consumed, recorded, completed].some((items) => items.length !== lease.writes.length)) throw new Error("writer journal event count mismatch");
    for (const write of lease.writes) {
      const indexes = [
        events.findIndex((event) => event.event === "writer.call.registered" && event.data?.callID === write.callID),
        events.findIndex((event) => event.event === "writer.call.consumed" && event.data?.callID === write.callID),
        events.findIndex((event) => event.event === "writer.recorded" && event.data?.callID === write.callID),
        events.findIndex((event) => event.event === "writer.completed" && event.data?.callID === write.callID),
      ];
      if (indexes.some((index) => index < 0) || indexes.some((index, position) => position > 0 && index <= indexes[position - 1])) {
        throw new Error("writer journal semantic order mismatch");
      }
      const helper = events[indexes[3]].data;
      if (helper.path !== write.path || helper.before_sha256 !== write.before_sha256 || helper.after_sha256 !== write.after_sha256 ||
          helper.executable !== deployment.native_writer.path || helper.executable_sha256 !== deployment.native_writer.sha256 ||
          helper.ppid !== lease.owner_pid || helper.build_id !== lease.build_id || helper.protocol_version !== lease.protocol_version || !Number.isInteger(helper.pid)) {
        throw new Error("native writer journal identity mismatch");
      }
    }
  }

  if (lease.state === "CLOSED") {
    const dependencyBaselines = new Map(descendantBaselines);
    for (const [governedPath, baseline] of Object.entries(lease.baseline)) {
      const resolved = path.resolve(governedPath);
      if (!dependencyBaselines.has(resolved)) dependencyBaselines.set(resolved, baseline);
    }
    for (const dependencyRunID of lease.manifest.dependency_run_ids) {
      const dependency = verifyRunEvidenceInternal({ ...input, runID: dependencyRunID }, visiting, dependencyBaselines);
      if (dependency.verdict !== "PASS") throw new Error(`dependency evidence is not PASS: ${dependencyRunID}`);
    }
    for (const governedPath of lease.manifest.exact_write_paths.map((item) => path.resolve(item))) {
      const writes = lease.writes.filter((item) => item.path === governedPath);
      if (!writes.length) throw new Error(`missing writer chain: ${governedPath}`);
      let digest = lease.baseline[governedPath];
      for (const write of writes) {
        if (write.before_sha256 !== digest) throw new Error(`broken writer chain: ${governedPath}`);
        digest = write.after_sha256;
      }
      if (digest === lease.baseline[governedPath]) throw new Error(`writer chain made no effective artifact change: ${governedPath}`);
      if (descendantBaselines.has(governedPath)) {
        if (descendantBaselines.get(governedPath) !== digest) throw new Error(`historical artifact transition mismatch: ${governedPath}`);
      } else if (sha256(fs.readFileSync(governedPath)) !== digest) throw new Error(`final artifact mismatch: ${governedPath}`);
    }
    if (["critique-a", "critique-b"].includes(lease.manifest.stage)) {
      const assessment = parseAssessment(Buffer.from(lease.output_text_base64!, "base64").toString("utf8"));
      const context = lease.manifest.critique_context!;
      if (assessment.source_digest !== normativeDigestFromSources(lease.manifest) || assessment.source_digest !== context.source_digest ||
          assessment.lineage_id !== context.lineage_id || assessment.round !== context.round) throw new Error("critic output is stale or foreign");
      const inherited = new Map(context.inherited_blocking_findings.map((item) => [item.finding_id, item.prior_source_digest]));
      if (assessment.resolutions.length !== inherited.size || assessment.resolutions.some((item) => inherited.get(item.finding_id) !== item.prior_source_digest)) {
        throw new Error("critic inherited resolution evidence mismatch");
      }
    }
    if (lease.manifest.stage === "critique-synthesis") {
      const dependencies = lease.manifest.dependency_run_ids.map((runID) => JSON.parse(verifySidecar(path.join(path.resolve(input.evidenceRoot), runID, "lease.json")).toString("utf8")) as Lease);
      const output = (stage: RunManifest["stage"]) => Buffer.from(dependencies.find((item) => item.manifest.stage === stage)?.output_text_base64 ?? "", "base64");
      for (const [stage, logicalPath] of [["critique-a", "assessment-a.json"], ["critique-b", "assessment-b.json"]] as const) {
        const dependency = dependencies.find((item) => item.manifest.stage === stage);
        const source = lease.manifest.sources.find((item) => item.logical_path === logicalPath);
        if (!dependency || dependency.state !== "CLOSED" || canonicalJson(dependency.manifest.critique_context) !== canonicalJson(lease.manifest.critique_context) ||
            !source || source.bytes !== dependency.output_text_base64 || source.sha256 !== dependency.output_text_sha256) {
          throw new Error(`synthesis dependency output is not sealed: ${stage}`);
        }
      }
      const synthesis = synthesizeAssessments({
        assessmentABytes: output("critique-a"),
        assessmentBBytes: output("critique-b"),
        inheritedBlockingIds: lease.manifest.critique_context!.inherited_blocking_findings.map((item) => item.finding_id),
      });
      if (synthesis.verdict !== "PASS") throw new Error("verified critique synthesis is BLOCKED");
      for (const artifact of lease.manifest.exact_write_paths) if (path.basename(artifact) === "design.md") assertGeneratedBlock(fs.readFileSync(artifact), synthesis.generatedBlockBytes);
    }
    verifyRuntimeDatabase(input.runtimeDatabasePath, lease, events);
  }

  const evidenceSha = sha256(Buffer.concat([leaseBytes, journalBytes, deploymentBytes]));
  visiting.delete(input.runID);
  return { verdict: lease.state === "CLOSED" ? "PASS" : "BLOCKED", evidence_sha256: evidenceSha, events: events.length };
}
