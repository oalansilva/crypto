import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { BUILD_ID, canonicalJson, manifestDigest, sha256, type RunManifest } from "../contract.js";
import { EvidenceStore } from "../lease-evidence.js";

function createManifest(worktree: string, overrides: Partial<RunManifest> = {}): RunManifest {
  const value: RunManifest = {
    schema: "design-authoring-manifest.v1",
    run_id: "run-lease",
    change_id: "card-550-design-planner-contract",
    card_id: "550",
    stage: "proposal",
    nonce: "manifest-nonce",
    parent_session_id: "parent",
    worktree,
    expected_agent: "design-planner",
    expected_model: { providerID: "openai", modelID: "gpt-5.6-sol" },
    expected_variant: "high",
    exact_write_paths: [path.join(worktree, "proposal.md")],
    expected_artifacts: [{ path: path.join(worktree, "proposal.md"), required: true }],
    sources: [],
    dependency_run_ids: [],
    packet_sha256: sha256("packet"),
    build_id: BUILD_ID,
    deployment_manifest_sha256: "a".repeat(64),
    profile_sha256: "b".repeat(64),
    config_sha256: "c".repeat(64),
    schema_sha256: "d".repeat(64),
    opencode_version: "1.18.18",
    deadline_at: new Date(Date.now() + 60_000).toISOString(),
    ...overrides,
  };
  value.manifest_sha256 = manifestDigest(value);
  return value;
}

test("lease enforces one child, provisional/final binding, and single-flight calls", () => {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), "design-gate-lease-"));
  const worktree = fs.mkdtempSync(path.join(os.tmpdir(), "design-gate-worktree-"));
  const store = new EvidenceStore(temp, "module-test");
  const lease = store.create(createManifest(worktree));
  store.setChild(lease.run_id, "child", "input-message");
  store.provisionalBind(lease.run_id);
  store.registerCall(lease.run_id, "operation", "call", "args", "child");
  assert.throws(() => store.registerCall(lease.run_id, "other", "call-2", "args-2", "child"), /single-flight/);
  assert.deepEqual(store.consumeCall(lease.run_id, "operation", "args"), { callID: "call" });
  assert.throws(() => store.registerCall(lease.run_id, "operation", "call-reused", "args", "child"), /fresh operation nonce/);
  store.finalBind(lease.run_id, "assistant-message");
  const artifact = lease.manifest.exact_write_paths[0];
  fs.mkdirSync(path.dirname(artifact), { recursive: true });
  fs.writeFileSync(artifact, "written");
  store.recordWrite(lease.run_id, {
    path: artifact,
    before_sha256: null,
    after_sha256: sha256("written"),
    operation_nonce: "operation",
    callID: "call",
    assistant_message_id: "assistant-message",
  });
  store.setOutput(lease.run_id, "assistant-message", "complete", sha256(canonicalJson([{ type: "text", text: "complete" }])));
  assert.equal(store.get(lease.run_id).state, "BOUND");
  store.finalize(lease.run_id, "PASS", { ok: true });
  assert.equal(store.get(lease.run_id).state, "CLOSED");
  assert.throws(() => store.registerCall(lease.run_id, "late", "call-late", "args-late", "child"), /terminal|phase/);
  const journal = fs.readFileSync(path.join(temp, lease.run_id, "journal.jsonl"), "utf8").trim().split("\n");
  assert.ok(journal.length >= 7);
});

test("startup recovery aborts stale non-terminal leases", () => {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), "design-gate-recovery-"));
  const worktree = fs.mkdtempSync(path.join(os.tmpdir(), "design-gate-worktree-"));
  const first = new EvidenceStore(temp, "old-module");
  first.create(createManifest(worktree, { run_id: "stale" }));
  const recovered = new EvidenceStore(temp, "new-module");
  assert.equal(recovered.get("stale").state, "ABORTED");
  assert.match(recovered.get("stale").failure || "", /orphaned or expired/);
});

test("startup accepts observational events after a terminal abort", () => {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), "design-gate-terminal-observation-"));
  const worktree = fs.mkdtempSync(path.join(os.tmpdir(), "design-gate-worktree-"));
  const first = new EvidenceStore(temp, "terminal-module");
  first.create(createManifest(worktree, { run_id: "terminal-observation" }));
  first.abort("terminal-observation", "expected failure");
  first.append("terminal-observation", "runtime.assistant.verified", { assistantMessageID: "late-observation" });
  const recovered = new EvidenceStore(temp, "new-module");
  assert.equal(recovered.get("terminal-observation").state, "ABORTED");
});

test("startup rejects state-changing events after a terminal abort", () => {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), "design-gate-terminal-mutation-"));
  const worktree = fs.mkdtempSync(path.join(os.tmpdir(), "design-gate-worktree-"));
  const first = new EvidenceStore(temp, "terminal-module");
  first.create(createManifest(worktree, { run_id: "terminal-mutation" }));
  first.abort("terminal-mutation", "expected failure");
  first.append("terminal-mutation", "binding.final", { assistantMessageID: "forged" });
  assert.throws(() => new EvidenceStore(temp, "new-module"), /unrecoverable Design lease/);
});

test("lease deadline aborts without requiring another guard operation", async () => {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), "design-gate-deadline-"));
  const worktree = fs.mkdtempSync(path.join(os.tmpdir(), "design-gate-worktree-"));
  const store = new EvidenceStore(temp, "deadline-module");
  store.create(createManifest(worktree, { run_id: "deadline", deadline_at: new Date(Date.now() + 25).toISOString() }));
  await new Promise((resolve) => setTimeout(resolve, 75));
  assert.equal(store.get("deadline").state, "ABORTED");
  assert.match(store.get("deadline").failure || "", /deadline expired/);
});

test("stage ordering fails closed when dependency runs are absent", () => {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), "design-gate-order-"));
  const worktree = fs.mkdtempSync(path.join(os.tmpdir(), "design-gate-worktree-"));
  const store = new EvidenceStore(temp, "module-order");
  assert.throws(() => store.create(createManifest(worktree, {
    run_id: "tasks-too-early",
    stage: "tasks",
    dependency_run_ids: [],
  })), /invalid dependency set/);
});
