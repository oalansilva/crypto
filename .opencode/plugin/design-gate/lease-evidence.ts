import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { randomUUID } from "node:crypto";
import { BUILD_ID, PROTOCOL_VERSION, canonicalJson, manifestDigest, sha256, type RunManifest } from "./contract.js";

export type LeaseState = "CREATED" | "BOUND" | "FINALIZING" | "CLOSED" | "ABORTED";

export type Lease = {
  run_id: string;
  manifest: RunManifest;
  state: LeaseState;
  owner_pid: number;
  owner_ppid: number;
  owner_executable: string;
  owner_executable_sha256: string;
  process_started_at: string;
  module_instance_id: string;
  build_id: string;
  protocol_version: string;
  created_at: string;
  updated_at: string;
  child_session_id?: string;
  input_message_id?: string;
  assistant_message_id?: string;
  output_message_id?: string;
  output_text_base64?: string;
  output_text_sha256?: string;
  output_parts_sha256?: string;
  provisional?: boolean;
  tombstoned_nonces: string[];
  pending_calls: Record<string, { callID: string; argsHash: string }>;
  baseline: Record<string, string | null>;
  writes: Array<{ path: string; before_sha256: string | null; after_sha256: string; operation_nonce: string; callID: string; assistant_message_id: string }>;
  failure?: string;
};

type JournalEvent = {
  sequence: number;
  at: string;
  run_id: string;
  event: string;
  data: unknown;
  previous_hash: string | null;
  hash: string;
};

function defaultEvidenceRoot(): string {
  const dataHome = process.env.XDG_DATA_HOME || path.join(os.homedir(), ".local", "share");
  return path.join(dataHome, "opencode", "design-gate");
}

const PROCESS_STARTED_AT = new Date().toISOString();

function processIdentity(): { executable: string; digest: string } {
  const executable = fs.realpathSync("/proc/self/exe");
  return { executable, digest: sha256(fs.readFileSync(executable)) };
}

function fileDigest(filePath: string): string | null {
  if (!fs.existsSync(filePath)) return null;
  const stat = fs.lstatSync(filePath);
  if (!stat.isFile() || stat.isSymbolicLink()) throw new Error(`unsafe governed artifact: ${filePath}`);
  return sha256(fs.readFileSync(filePath));
}

function writeDurable(filePath: string, bytes: string): void {
  fs.mkdirSync(path.dirname(filePath), { recursive: true, mode: 0o700 });
  const temp = `${filePath}.${process.pid}.tmp`;
  const fd = fs.openSync(temp, fs.constants.O_CREAT | fs.constants.O_EXCL | fs.constants.O_WRONLY, 0o600);
  try {
    fs.writeFileSync(fd, bytes);
    fs.fsyncSync(fd);
  } finally {
    fs.closeSync(fd);
  }
  fs.renameSync(temp, filePath);
  const dir = fs.openSync(path.dirname(filePath), fs.constants.O_RDONLY);
  try {
    fs.fsyncSync(dir);
  } finally {
    fs.closeSync(dir);
  }
}

export class EvidenceStore {
  readonly root: string;
  readonly moduleInstanceID: string;
  private leases = new Map<string, Lease>();
  private deadlineTimers = new Map<string, NodeJS.Timeout>();

  constructor(root = defaultEvidenceRoot(), moduleInstanceID: string = randomUUID()) {
    this.root = root;
    this.moduleInstanceID = moduleInstanceID;
    fs.mkdirSync(root, { recursive: true, mode: 0o700 });
    this.recoverOrphans();
  }

  private runDir(runID: string): string {
    if (!/^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$/.test(runID)) throw new Error("unsafe run ID");
    return path.join(this.root, runID);
  }

  private leasePath(runID: string): string {
    return path.join(this.runDir(runID), "lease.json");
  }

  private journalPath(runID: string): string {
    return path.join(this.runDir(runID), "journal.jsonl");
  }

  create(manifest: RunManifest): Lease {
    if (Date.parse(manifest.deadline_at) <= Date.now()) throw new Error("Design lease deadline expired");
    if (this.leases.has(manifest.run_id) || fs.existsSync(this.leasePath(manifest.run_id))) throw new Error("run already exists");
    const duplicate = [...this.leases.values()].find(
      (lease) => lease.state !== "CLOSED" && lease.state !== "ABORTED",
    );
    if (duplicate) throw new Error(`active process-scoped Design lease already exists: ${duplicate.run_id}`);
    this.assertDependencies(manifest);
    const now = new Date().toISOString();
    const processInfo = processIdentity();
    manifest.guard_process = this.processFacts();
    manifest.manifest_sha256 = manifestDigest(manifest);
    const baseline = Object.fromEntries(manifest.exact_write_paths.map((item) => [path.resolve(item), fileDigest(path.resolve(item))]));
    const lease: Lease = {
      run_id: manifest.run_id,
      manifest,
      state: "CREATED",
      owner_pid: process.pid,
      owner_ppid: process.ppid,
      owner_executable: processInfo.executable,
      owner_executable_sha256: processInfo.digest,
      process_started_at: PROCESS_STARTED_AT,
      module_instance_id: this.moduleInstanceID,
      build_id: BUILD_ID,
      protocol_version: PROTOCOL_VERSION,
      created_at: now,
      updated_at: now,
      tombstoned_nonces: [],
      pending_calls: {},
      baseline,
      writes: [],
    };
    this.leases.set(lease.run_id, lease);
    this.persist(lease);
    this.append(lease.run_id, "lease.created", {
      manifest_sha256: manifestDigest(manifest),
      state: lease.state,
      owner_pid: lease.owner_pid,
      owner_ppid: lease.owner_ppid,
      owner_executable: lease.owner_executable,
      owner_executable_sha256: lease.owner_executable_sha256,
      process_started_at: lease.process_started_at,
      module_instance_id: lease.module_instance_id,
      build_id: lease.build_id,
      protocol_version: lease.protocol_version,
      baseline,
    });
    const timer = setTimeout(() => {
      const current = this.get(lease.run_id);
      if (!["CLOSED", "ABORTED"].includes(current.state)) this.abort(current.run_id, "Design lease deadline expired");
    }, Math.max(1, Date.parse(manifest.deadline_at) - Date.now()));
    timer.unref();
    this.deadlineTimers.set(lease.run_id, timer);
    return lease;
  }

  processFacts(): NonNullable<RunManifest["guard_process"]> {
    const identity = processIdentity();
    return {
      pid: process.pid,
      ppid: process.ppid,
      executable: identity.executable,
      executable_sha256: identity.digest,
      process_started_at: PROCESS_STARTED_AT,
      module_instance_id: this.moduleInstanceID,
    };
  }

  get(runID: string): Lease {
    const cached = this.leases.get(runID);
    if (cached) return cached;
    const parsed = JSON.parse(fs.readFileSync(this.leasePath(runID), "utf8")) as Lease;
    this.leases.set(runID, parsed);
    return parsed;
  }

  findByNonce(nonce: string): Lease | undefined {
    return [...this.leases.values()].find((lease) => lease.manifest.nonce === nonce);
  }

  findBySession(sessionID: string): Lease | undefined {
    return [...this.leases.values()].find(
      (lease) => lease.manifest.parent_session_id === sessionID || lease.child_session_id === sessionID,
    );
  }

  active(): Lease[] {
    return [...this.leases.values()].filter((lease) => !["CLOSED", "ABORTED"].includes(lease.state));
  }

  setChild(runID: string, childSessionID: string, inputMessageID: string): Lease {
    const lease = this.get(runID);
    if (lease.state !== "CREATED" || lease.child_session_id) throw new Error("lease cannot spawn another child");
    lease.child_session_id = childSessionID;
    lease.input_message_id = inputMessageID;
    this.touch(lease, "child.created", { childSessionID, inputMessageID });
    return lease;
  }

  provisionalBind(runID: string): Lease {
    const lease = this.get(runID);
    this.assertOperable(lease, ["CREATED"]);
    if (lease.provisional || !lease.child_session_id || !lease.input_message_id) throw new Error("invalid provisional binding");
    lease.provisional = true;
    this.touch(lease, "binding.provisional", { childSessionID: lease.child_session_id, inputMessageID: lease.input_message_id });
    return lease;
  }

  finalBind(runID: string, assistantMessageID: string): Lease {
    const lease = this.get(runID);
    this.assertOperable(lease, ["CREATED"]);
    if (!lease.provisional || lease.state !== "CREATED") throw new Error("provisional binding is required");
    lease.assistant_message_id = assistantMessageID;
    lease.state = "BOUND";
    lease.provisional = false;
    lease.tombstoned_nonces.push(lease.manifest.nonce);
    this.touch(lease, "binding.final", { assistantMessageID, state: lease.state });
    return lease;
  }

  setOutput(runID: string, outputMessageID: string, outputText: string, outputPartsSha256: string): Lease {
    const lease = this.get(runID);
    this.assertOperable(lease, ["BOUND"]);
    if (lease.output_message_id) throw new Error("stage output message is already bound");
    lease.output_message_id = outputMessageID;
    lease.output_text_base64 = Buffer.from(outputText, "utf8").toString("base64");
    lease.output_text_sha256 = sha256(Buffer.from(outputText, "utf8"));
    lease.output_parts_sha256 = outputPartsSha256;
    this.touch(lease, "stage.output.bound", {
      outputMessageID,
      output_text_sha256: lease.output_text_sha256,
      output_parts_sha256: lease.output_parts_sha256,
    });
    return lease;
  }

  registerCall(runID: string, operationNonce: string, callID: string, argsHash: string, sessionID: string): void {
    const lease = this.get(runID);
    this.assertOperable(lease, ["CREATED", "BOUND"]);
    if (sessionID !== lease.child_session_id || (!lease.provisional && lease.state !== "BOUND")) throw new Error("writer call before binding or from wrong session");
    if (Object.keys(lease.pending_calls).length > 0 || lease.tombstoned_nonces.includes(operationNonce)) {
      throw new Error("writer calls must be single-flight with a fresh operation nonce");
    }
    lease.pending_calls[operationNonce] = { callID, argsHash };
    this.touch(lease, "writer.call.registered", { operationNonce, callID, argsHash });
  }

  consumeCall(runID: string, operationNonce: string, argsHash: string): { callID: string } {
    const lease = this.get(runID);
    this.assertOperable(lease, ["CREATED", "BOUND"]);
    const pending = lease.pending_calls[operationNonce];
    if (!pending || pending.argsHash !== argsHash) throw new Error("writer call correlation mismatch");
    delete lease.pending_calls[operationNonce];
    lease.tombstoned_nonces.push(operationNonce);
    this.touch(lease, "writer.call.consumed", { operationNonce, callID: pending.callID });
    return { callID: pending.callID };
  }

  recordWrite(runID: string, write: Lease["writes"][number]): void {
    const lease = this.get(runID);
    this.assertOperable(lease, ["BOUND"]);
    if (!write.assistant_message_id) throw new Error("writer AssistantMessage is required");
    const expectedBefore = lease.writes.filter((item) => item.path === write.path).at(-1)?.after_sha256 ?? lease.baseline[write.path];
    if (expectedBefore !== write.before_sha256) throw new Error("writer digest chain mismatch");
    lease.writes.push(write);
    this.touch(lease, "writer.recorded", write);
  }

  assertReadonly(runID: string, sessionID: string): Lease {
    const lease = this.get(runID);
    this.assertOperable(lease, ["CREATED", "BOUND"]);
    if (lease.manifest.parent_session_id !== sessionID) throw new Error("only the bound orchestrator may run OpenSpec");
    return lease;
  }

  finalize(runID: string, verdict: "PASS" | "BLOCKED", data: unknown): Lease {
    const lease = this.get(runID);
    if (verdict === "PASS") this.assertPassReady(lease);
    else if (["CLOSED", "ABORTED"].includes(lease.state)) return lease;
    lease.state = "FINALIZING";
    this.touch(lease, "lease.finalizing", data);
    lease.state = verdict === "PASS" ? "CLOSED" : "ABORTED";
    if (verdict === "BLOCKED") lease.failure = canonicalJson(data);
    this.touch(lease, `lease.${lease.state.toLowerCase()}`, { verdict });
    this.clearDeadline(runID);
    return lease;
  }

  abort(runID: string, reason: string): Lease {
    const lease = this.get(runID);
    if (["CLOSED", "ABORTED"].includes(lease.state)) return lease;
    lease.state = "FINALIZING";
    lease.failure = reason;
    this.touch(lease, "lease.finalizing", { reason });
    lease.state = "ABORTED";
    this.touch(lease, "lease.aborted", { reason, verdict: "BLOCKED" });
    this.clearDeadline(runID);
    return lease;
  }

  append(runID: string, event: string, data: unknown): JournalEvent {
    const journalPath = this.journalPath(runID);
    fs.mkdirSync(path.dirname(journalPath), { recursive: true, mode: 0o700 });
    const existing = fs.existsSync(journalPath)
      ? fs.readFileSync(journalPath, "utf8").split("\n").filter(Boolean)
      : [];
    const previous = existing.length ? (JSON.parse(existing.at(-1)!) as JournalEvent).hash : null;
    const unsigned = {
      sequence: existing.length + 1,
      at: new Date().toISOString(),
      run_id: runID,
      event,
      data,
      previous_hash: previous,
    };
    const record: JournalEvent = { ...unsigned, hash: sha256(canonicalJson(unsigned)) };
    const fd = fs.openSync(journalPath, fs.constants.O_CREAT | fs.constants.O_APPEND | fs.constants.O_WRONLY, 0o600);
    try {
      fs.writeSync(fd, `${canonicalJson(record)}\n`);
      fs.fsyncSync(fd);
    } finally {
      fs.closeSync(fd);
    }
    writeDurable(`${journalPath}.sha256`, `${sha256(fs.readFileSync(journalPath))}\n`);
    return record;
  }

  verifyJournal(runID: string): void {
    const journalPath = this.journalPath(runID);
    const lines = fs.readFileSync(journalPath, "utf8").split("\n").filter(Boolean);
    let previous: string | null = null;
    for (const [index, line] of lines.entries()) {
      const record = JSON.parse(line) as JournalEvent;
      const { hash, ...unsigned } = record;
      if (record.sequence !== index + 1 || record.previous_hash !== previous || sha256(canonicalJson(unsigned)) !== hash) {
        throw new Error(`invalid journal chain at sequence ${index + 1}`);
      }
      previous = hash;
    }
    const sidecar = fs.readFileSync(`${journalPath}.sha256`, "utf8").trim();
    if (sidecar !== sha256(fs.readFileSync(journalPath))) throw new Error("journal sidecar mismatch");
  }

  private touch(lease: Lease, event: string, data: unknown): void {
    lease.updated_at = new Date().toISOString();
    this.persist(lease);
    this.append(lease.run_id, event, data);
  }

  private persist(lease: Lease): void {
    const bytes = `${canonicalJson(lease)}\n`;
    writeDurable(this.leasePath(lease.run_id), bytes);
    writeDurable(`${this.leasePath(lease.run_id)}.sha256`, `${sha256(bytes)}\n`);
  }

  private assertOperable(lease: Lease, states: LeaseState[]): void {
    if (!states.includes(lease.state)) throw new Error(`Design lease is terminal or not in phase: ${lease.state}`);
    if (Date.parse(lease.manifest.deadline_at) <= Date.now()) {
      this.abort(lease.run_id, "Design lease deadline expired");
      throw new Error("Design lease deadline expired");
    }
  }

  private assertPassReady(lease: Lease): void {
    this.assertOperable(lease, ["BOUND"]);
    if (!lease.output_message_id || !lease.output_text_base64 || !lease.output_text_sha256 || !lease.output_parts_sha256) throw new Error("terminal output evidence is not bound");
    if (Object.keys(lease.pending_calls).length) throw new Error("pending writer call blocks finalization");
    const author = ["proposal", "design-specs", "tasks", "critique-synthesis"].includes(lease.manifest.stage);
    if (author) {
      for (const exactPath of lease.manifest.exact_write_paths.map((item) => path.resolve(item))) {
        const writes = lease.writes.filter((item) => item.path === exactPath);
        if (!writes.length || fileDigest(exactPath) !== writes.at(-1)!.after_sha256 || writes.at(-1)!.after_sha256 === lease.baseline[exactPath]) {
          throw new Error(`artifact lacks a complete writer chain: ${exactPath}`);
        }
      }
    } else if (lease.writes.length) {
      throw new Error("critic stage cannot contain writes");
    }
  }

  private assertDependencies(manifest: RunManifest): void {
    const requiredStages: Record<RunManifest["stage"], RunManifest["stage"][]> = {
      proposal: [],
      "design-specs": ["proposal"],
      tasks: ["design-specs"],
      "critique-a": ["tasks"],
      "critique-b": ["tasks", "critique-a"],
      "critique-synthesis": ["critique-a", "critique-b"],
    };
    const dependencies = manifest.dependency_run_ids.map((runID) => this.get(runID));
    const expected = requiredStages[manifest.stage];
    if (dependencies.length !== expected.length || expected.some((stage) => dependencies.filter((item) => item.manifest.stage === stage).length !== 1)) {
      throw new Error(`stage ${manifest.stage} has an invalid dependency set`);
    }
    for (const dependency of dependencies) {
      if (dependency.state !== "CLOSED" || dependency.manifest.change_id !== manifest.change_id || dependency.manifest.worktree !== manifest.worktree) {
        throw new Error("stage dependency is stale, foreign, or not closed");
      }
      for (const governedPath of dependency.manifest.exact_write_paths) {
        const logicalPath = path.relative(manifest.worktree, governedPath);
        const source = manifest.sources.find((item) => item.logical_path === logicalPath);
        const current = fileDigest(governedPath);
        if (!source || !current || source.sha256 !== current) throw new Error(`stage dependency bytes are not sealed: ${logicalPath}`);
      }
    }
    if (manifest.stage === "critique-b") {
      const assessmentA = dependencies.find((item) => item.manifest.stage === "critique-a")!;
      if (assessmentA.manifest.packet_sha256 !== manifest.packet_sha256) throw new Error("Assessment A/B packets differ");
    }
    for (const [stage, logicalPath] of [["critique-a", "assessment-a.json"], ["critique-b", "assessment-b.json"]] as const) {
      const dependency = dependencies.find((item) => item.manifest.stage === stage);
      if (!dependency) continue;
      if (!dependency.output_text_base64 || !dependency.output_text_sha256) throw new Error(`${stage} output evidence is absent`);
      const source = manifest.sources.find((item) => item.logical_path === logicalPath);
      const output = Buffer.from(dependency.output_text_base64, "base64");
      if (!source || !decodeSource(source).equals(output) || source.sha256 !== dependency.output_text_sha256) {
        throw new Error(`${stage} output bytes are not sealed in the dependent stage`);
      }
    }
    if (["critique-a", "critique-b", "critique-synthesis"].includes(manifest.stage)) {
      for (const dependency of dependencies.filter((item) => item.manifest.critique_context)) {
        if (canonicalJson(dependency.manifest.critique_context) !== canonicalJson(manifest.critique_context)) {
          throw new Error("critique dependency context mismatch");
        }
      }
      const closure = new Map<string, Lease>();
      const visit = (lease: Lease) => {
        if (closure.has(lease.run_id)) return;
        if (lease.state !== "CLOSED" || lease.manifest.change_id !== manifest.change_id || lease.manifest.worktree !== manifest.worktree) {
          throw new Error("critique dependency DAG contains stale or foreign evidence");
        }
        closure.set(lease.run_id, lease);
        for (const runID of lease.manifest.dependency_run_ids) visit(this.get(runID));
      };
      for (const dependency of dependencies) visit(dependency);
      const stage = (name: RunManifest["stage"]) => [...closure.values()].filter((item) => item.manifest.stage === name);
      if (stage("proposal").length !== 1 || stage("design-specs").length !== 1 || stage("tasks").length !== 1) {
        throw new Error("critique dependency DAG lacks a unique normative author chain");
      }
      const normativePaths = [
        ...stage("proposal")[0].manifest.exact_write_paths,
        ...stage("design-specs")[0].manifest.exact_write_paths.filter((item) => {
          const relative = path.relative(path.join(manifest.worktree, "openspec", "changes", manifest.change_id), item);
          return relative === "design.md" || (relative.startsWith(`specs${path.sep}`) && relative.endsWith(`${path.sep}spec.md`));
        }),
        ...stage("tasks")[0].manifest.exact_write_paths,
      ].map((item) => path.resolve(item));
      const expectedLogical = new Set(normativePaths.map((item) => path.relative(manifest.worktree, item)));
      for (const governedPath of normativePaths) {
        const logicalPath = path.relative(manifest.worktree, governedPath);
        const source = manifest.sources.find((item) => item.logical_path === logicalPath);
        const owner = [...closure.values()].find((item) => item.manifest.exact_write_paths.some((candidate) => path.resolve(candidate) === governedPath));
        const finalDigest = owner?.writes.filter((item) => item.path === governedPath).at(-1)?.after_sha256;
        const current = fileDigest(governedPath);
        if (!source || !current || source.sha256 !== current || source.sha256 !== finalDigest || !decodeSource(source).equals(fs.readFileSync(governedPath))) {
          throw new Error(`critique source is not the current transitive author output: ${logicalPath}`);
        }
      }
      const allowedSupport = new Set(manifest.stage === "critique-a" ? [] : manifest.stage === "critique-b" ? ["assessment-a.json"] : ["assessment-a.json", "assessment-b.json"]);
      if (manifest.sources.some((source) => !expectedLogical.has(source.logical_path) && !allowedSupport.has(source.logical_path))) {
        throw new Error("critique manifest contains an unrecognized source");
      }
    }
  }

  private clearDeadline(runID: string): void {
    const timer = this.deadlineTimers.get(runID);
    if (timer) clearTimeout(timer);
    this.deadlineTimers.delete(runID);
  }

  private recoverOrphans(): void {
    if (!fs.existsSync(this.root)) return;
    for (const entry of fs.readdirSync(this.root, { withFileTypes: true })) {
      if (!entry.isDirectory()) continue;
      const leasePath = this.leasePath(entry.name);
      if (!fs.existsSync(leasePath)) continue;
      try {
        const lease = JSON.parse(fs.readFileSync(leasePath, "utf8")) as Lease;
        this.leases.set(lease.run_id, lease);
        const leaseBytes = fs.readFileSync(leasePath);
        if (fs.readFileSync(`${leasePath}.sha256`, "utf8").trim() !== sha256(leaseBytes)) throw new Error("lease sidecar mismatch");
        this.verifyJournal(lease.run_id);
        if (["CLOSED", "ABORTED"].includes(lease.state)) {
          const records = fs.readFileSync(this.journalPath(lease.run_id), "utf8").trim().split("\n").map((line) => JSON.parse(line) as JournalEvent);
          const terminalEvent = lease.state === "CLOSED" ? "lease.closed" : "lease.aborted";
          const terminalIndex = records.findIndex((record) => record.event === terminalEvent);
          const observationalAfterTerminal = new Set(["runtime.tool.after", "runtime.assistant.verified"]);
          if (terminalIndex < 0 || records.slice(terminalIndex + 1).some((record) => !observationalAfterTerminal.has(record.event))) {
            throw new Error("terminal journal event missing or followed by a state-changing event");
          }
          continue;
        }
        const expired = Date.parse(lease.manifest.deadline_at) <= Date.now();
        let ownerAlive = true;
        try {
          process.kill(lease.owner_pid, 0);
        } catch {
          ownerAlive = false;
        }
        if (expired || !ownerAlive || lease.module_instance_id !== this.moduleInstanceID) {
          this.abort(lease.run_id, "orphaned or expired lease recovered at startup");
        }
      } catch {
        throw new Error(`unrecoverable Design lease: ${entry.name}`);
      }
    }
  }
}

function decodeSource(source: RunManifest["sources"][number]): Buffer {
  return Buffer.from(source.bytes, "base64");
}
