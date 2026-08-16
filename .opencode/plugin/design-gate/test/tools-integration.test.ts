import assert from "node:assert/strict";
import fs from "node:fs";
import { DatabaseSync } from "node:sqlite";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { BUILD_ID, GENERATED_BEGIN, GENERATED_END, buildCritiquePacket, buildPacket, canonicalJson, manifestDigest, normativeDigest, normativeDigestFromSources, sha256, validateManifest, type RunManifest } from "../contract.js";
import { insertGeneratedBlock, synthesizeAssessments } from "../assessments.js";
import { EvidenceStore } from "../lease-evidence.js";
import { RuntimeAdapter } from "../runtime-adapter.js";
import { createDesignGateTools } from "../spawn-readonly-tools.js";
import { verifyRunEvidence } from "../verifier.js";

const gateRoot = path.resolve(import.meta.dirname, "..");
const deploymentDigest = fs.readFileSync(path.join(gateRoot, "dist", "deployment-manifest.sha256"), "utf8").trim();
const deploymentManifestPath = path.join(gateRoot, "dist", "deployment-manifest.json");
const deployment = JSON.parse(fs.readFileSync(deploymentManifestPath, "utf8"));

function manifestFor(worktree: string, stage: RunManifest["stage"], runID: string): { manifest: RunManifest; packet: Buffer } {
  const packet = Buffer.from(canonicalJson({ stage, source: "immutable" }));
  const author = !stage.startsWith("critique-") || stage === "critique-synthesis";
  const relative = stage === "proposal" ? "proposal.md" : stage === "tasks" ? "tasks.md" : "design.md";
  const artifact = path.join(worktree, "openspec", "changes", "card-550-design-planner-contract", relative);
  const manifest: RunManifest = {
    schema: "design-authoring-manifest.v1",
    run_id: runID,
    change_id: "card-550-design-planner-contract",
    card_id: "550",
    stage,
    nonce: `${runID}-nonce`,
    parent_session_id: "parent",
    worktree,
    expected_agent: author ? "design-planner" : "design-critic-readonly",
    expected_model: { providerID: "openai", modelID: "gpt-5.6-sol" },
    expected_variant: "high",
    exact_write_paths: author ? [artifact] : [],
    expected_artifacts: author ? [{ path: artifact, required: true }] : [],
    sources: [],
    dependency_run_ids: [],
    packet_sha256: sha256(packet),
    build_id: BUILD_ID,
    deployment_manifest_sha256: deploymentDigest,
    profile_sha256: deployment.files[`.opencode/agent/${author ? "design-planner" : "design-critic-readonly"}.md`],
    config_sha256: deployment.files["opencode.json"],
    schema_sha256: deployment.files[".opencode/plugin/design-gate/schemas/assessment-v1.json"],
    opencode_version: "1.18.18",
    deadline_at: new Date(Date.now() + 60_000).toISOString(),
  };
  manifest.manifest_sha256 = manifestDigest(manifest);
  return { manifest, packet };
}

function context(worktree: string, overrides: Record<string, unknown> = {}) {
  return {
    sessionID: "parent",
    messageID: "orchestrator-message",
    agent: "build",
    directory: worktree,
    worktree,
    abort: new AbortController().signal,
    metadata() {},
    ...overrides,
  } as any;
}

function closeAuthorStage(store: EvidenceStore, manifest: RunManifest, content: string | Record<string, string>): void {
  store.create(manifest);
  store.setChild(manifest.run_id, `${manifest.run_id}-child`, `${manifest.run_id}-input`);
  store.provisionalBind(manifest.run_id);
  store.finalBind(manifest.run_id, `${manifest.run_id}-assistant`);
  for (const [index, artifact] of manifest.exact_write_paths.entries()) {
    fs.mkdirSync(path.dirname(artifact), { recursive: true });
    const artifactContent = typeof content === "string" ? content : content[artifact];
    if (artifactContent === undefined) throw new Error(`missing seeded content for ${artifact}`);
    const before = fs.existsSync(artifact) ? sha256(fs.readFileSync(artifact)) : null;
    fs.writeFileSync(artifact, artifactContent);
    store.recordWrite(manifest.run_id, {
      path: artifact,
      before_sha256: before,
      after_sha256: sha256(artifactContent),
      operation_nonce: `${manifest.run_id}-operation-${index}`,
      callID: `${manifest.run_id}-call-${index}`,
      assistant_message_id: `${manifest.run_id}-assistant`,
    });
  }
  store.setOutput(manifest.run_id, `${manifest.run_id}-assistant`, "seeded", sha256(canonicalJson([{ type: "text", text: "seeded" }])));
  store.finalize(manifest.run_id, "PASS", { seeded: true });
}

function dependOn(manifest: RunManifest, dependencies: RunManifest[]): void {
  manifest.dependency_run_ids = dependencies.map((item) => item.run_id);
  manifest.sources = dependencies.flatMap((dependency) => dependency.exact_write_paths.map((filePath) => {
    const bytes = fs.readFileSync(filePath);
    return {
      logical_path: path.relative(manifest.worktree, filePath),
      encoding: "base64" as const,
      bytes: bytes.toString("base64"),
      sha256: sha256(bytes),
    };
  }));
  manifest.manifest_sha256 = manifestDigest(manifest);
}

function addCritiqueContext(manifest: RunManifest): string {
  const changeRoot = path.join(manifest.worktree, "openspec", "changes", manifest.change_id);
  const prefix = `openspec/changes/${manifest.change_id}/`;
  const files = [
    [`${prefix}proposal.md`, path.join(changeRoot, "proposal.md")],
    [`${prefix}design.md`, path.join(changeRoot, "design.md")],
    [`${prefix}specs/gate/spec.md`, path.join(changeRoot, "specs", "gate", "spec.md")],
    [`${prefix}tasks.md`, path.join(changeRoot, "tasks.md")],
  ] as const;
  manifest.sources.push(...files.filter(([logicalPath]) => !manifest.sources.some((source) => source.logical_path === logicalPath)).map(([logical_path, filePath]) => {
    const bytes = fs.readFileSync(filePath);
    return { logical_path, encoding: "base64" as const, bytes: bytes.toString("base64"), sha256: sha256(bytes) };
  }));
  const sourceDigest = normativeDigest({
    proposal: fs.readFileSync(files[0][1]),
    design: fs.readFileSync(files[1][1]),
    specs: [{ path: "specs/gate/spec.md", bytes: fs.readFileSync(files[2][1]) }],
    tasks: fs.readFileSync(files[3][1]),
  });
  manifest.critique_context = { lineage_id: "lineage", round: 0, source_digest: sourceDigest, inherited_blocking_findings: [] };
  manifest.manifest_sha256 = manifestDigest(manifest);
  return sourceDigest;
}

test("spawn tool binds an author write and closes only after an attributable artifact change", async () => {
  const worktree = fs.mkdtempSync(path.join(os.tmpdir(), "design-tools-author-"));
  const evidence = fs.mkdtempSync(path.join(os.tmpdir(), "design-tools-evidence-"));
  const { manifest, packet } = manifestFor(worktree, "proposal", "author-positive");
  fs.mkdirSync(path.dirname(manifest.exact_write_paths[0]), { recursive: true });
  const store = new EvidenceStore(evidence, "module-tools");
  const runtime = new RuntimeAdapter(store);
  let guarded: ReturnType<typeof createDesignGateTools>;
  const recordedWriteArgs: any[] = [];
  const client = {
    session: {
      create: async () => ({ data: { id: "child", parentID: "parent", version: "1.18.18" } }),
      message: async (request: any) => ({ data: { info: {
        id: request.path.messageID,
        role: "assistant", sessionID: "child", parentID: store.get(manifest.run_id).input_message_id,
        agent: manifest.expected_agent, providerID: "openai", modelID: "gpt-5.6-sol", variant: "high",
      } } }),
      prompt: async (request: any) => {
        assert.equal(request.body.tools, undefined);
        runtime.onSessionCreated({ id: "child", parentID: "parent", version: "1.18.18" });
        runtime.onChatMessage(
          { sessionID: "child", agent: manifest.expected_agent, model: manifest.expected_model, messageID: request.body.messageID, variant: "high" },
          request.body.parts,
        );
        for (const [index, content] of ["authored once\n", "authored twice\n"].entries()) {
          const writeArgs = {
            run_id: manifest.run_id,
            manifest_nonce: manifest.nonce,
            manifest_sha256: store.get(manifest.run_id).manifest.manifest_sha256!,
            operation_nonce: `write-${index}`,
            exact_path: manifest.exact_write_paths[0],
            base_sha256: index === 0 ? "-" : sha256("authored once\n"),
            full_content_base64: Buffer.from(content).toString("base64"),
          };
          recordedWriteArgs.push(writeArgs);
          guarded.beforeTool("design_artifact_write", "child", `call-${index}`, writeArgs);
          await guarded.tool.design_artifact_write.execute(writeArgs, context(worktree, {
            sessionID: "child",
            messageID: `assistant-${index}`,
            agent: manifest.expected_agent,
          }));
          guarded.afterTool("design_artifact_write", "child", `call-${index}`, { ok: true });
        }
        return { data: { info: { id: "assistant-output", parentID: request.body.messageID, finish: "stop" }, parts: [{ type: "text", text: "authored" }] } };
      },
    },
  };
  guarded = createDesignGateTools({ client, store, runtime });
  const result = await guarded.tool.design_spawn_stage.execute({
    manifest_json: canonicalJson(manifest),
    packet_base64: packet.toString("base64"),
  }, context(worktree));
  assert.match((result as any).output, /"verdict":"PASS"/);
  assert.equal(fs.readFileSync(manifest.exact_write_paths[0], "utf8"), "authored twice\n");
  assert.equal(store.get(manifest.run_id).state, "CLOSED");
  const lease = store.get(manifest.run_id);
  const databasePath = path.join(worktree, "runtime.db");
  const database = new DatabaseSync(databasePath);
  database.exec([
    "CREATE TABLE session (id TEXT PRIMARY KEY, parent_id TEXT, directory TEXT, version TEXT, time_created INTEGER)",
    "CREATE TABLE message (id TEXT PRIMARY KEY, session_id TEXT, data TEXT)",
    "CREATE TABLE part (id TEXT PRIMARY KEY, message_id TEXT, session_id TEXT, time_created INTEGER, data TEXT)",
  ].join(";"));
  database.prepare("INSERT INTO session VALUES (?, ?, ?, ?, ?)").run("child", "parent", worktree, "1.18.18", Date.now());
  database.prepare("INSERT INTO message VALUES (?, ?, ?)").run(lease.input_message_id!, "child", canonicalJson({
    role: "user",
    agent: manifest.expected_agent,
    model: { ...manifest.expected_model, variant: manifest.expected_variant },
  }));
  for (const messageID of ["assistant-0", "assistant-1", "assistant-output"]) {
    database.prepare("INSERT INTO message VALUES (?, ?, ?)").run(messageID, "child", canonicalJson({
      agent: manifest.expected_agent,
      modelID: "gpt-5.6-sol",
      parentID: lease.input_message_id,
      providerID: "openai",
      role: "assistant",
      variant: "high",
    }));
  }
  database.prepare("INSERT INTO part VALUES (?, ?, ?, ?, ?)").run("part-input", lease.input_message_id!, "child", Date.now() - 2, canonicalJson({ type: "text", text: buildPacket(lease.manifest, packet) }));
  for (const index of [0, 1]) database.prepare("INSERT INTO part VALUES (?, ?, ?, ?, ?)").run(`part-tool-${index}`, `assistant-${index}`, "child", Date.now() - 1 + index, canonicalJson({
    type: "tool", tool: "design_artifact_write", callID: `call-${index}`, state: { status: "completed", input: recordedWriteArgs[index] },
  }));
  database.prepare("INSERT INTO part VALUES (?, ?, ?, ?, ?)").run("part-output", "assistant-output", "child", Date.now() + 1, canonicalJson({ type: "text", text: "authored" }));
  database.close();
  assert.equal(verifyRunEvidence({
    evidenceRoot: evidence,
    runID: manifest.run_id,
    deploymentManifestPath,
    runtimeDatabasePath: databasePath,
  }).verdict, "PASS");
  const leasePath = path.join(evidence, manifest.run_id, "lease.json");
  const originalLeaseBytes = fs.readFileSync(leasePath);
  const swappedLease = JSON.parse(originalLeaseBytes.toString("utf8"));
  [swappedLease.writes[0].assistant_message_id, swappedLease.writes[1].assistant_message_id] =
    [swappedLease.writes[1].assistant_message_id, swappedLease.writes[0].assistant_message_id];
  const swappedLeaseBytes = Buffer.from(`${canonicalJson(swappedLease)}\n`);
  fs.writeFileSync(leasePath, swappedLeaseBytes);
  fs.writeFileSync(`${leasePath}.sha256`, `${sha256(swappedLeaseBytes)}\n`);
  assert.throws(() => verifyRunEvidence({ evidenceRoot: evidence, runID: manifest.run_id, deploymentManifestPath, runtimeDatabasePath: databasePath }), /tool-call correlation/);
  fs.writeFileSync(leasePath, originalLeaseBytes);
  fs.writeFileSync(`${leasePath}.sha256`, `${sha256(originalLeaseBytes)}\n`);
  const extraToolDatabase = new DatabaseSync(databasePath);
  extraToolDatabase.prepare("INSERT INTO part VALUES (?, ?, ?, ?, ?)").run("part-tool-extra", "assistant-0", "child", Date.now(), canonicalJson({
    type: "tool", tool: "read", callID: "call-extra", state: { status: "completed", input: {} },
  }));
  extraToolDatabase.close();
  assert.throws(() => verifyRunEvidence({ evidenceRoot: evidence, runID: manifest.run_id, deploymentManifestPath, runtimeDatabasePath: databasePath }), /tool-call count/);
  const cleanDatabase = new DatabaseSync(databasePath);
  cleanDatabase.prepare("DELETE FROM part WHERE id = ?").run("part-tool-extra");
  cleanDatabase.close();
  const tamperedDatabase = new DatabaseSync(databasePath);
  tamperedDatabase.prepare("UPDATE part SET data = ? WHERE id = ?").run(canonicalJson({
    type: "tool", tool: "design_artifact_write", callID: "call-0", state: { status: "completed", input: { ...recordedWriteArgs[0], operation_nonce: "forged" } },
  }), "part-tool-0");
  tamperedDatabase.close();
  assert.throws(() => verifyRunEvidence({ evidenceRoot: evidence, runID: manifest.run_id, deploymentManifestPath, runtimeDatabasePath: databasePath }), /tool-call correlation/);
  assert.throws(() => guarded.beforeTool("design_artifact_write", "child", "late", {
    run_id: manifest.run_id,
    operation_nonce: "late",
  }), /terminal|phase/);
  fs.appendFileSync(path.join(evidence, manifest.run_id, "journal.jsonl"), "\n");
  assert.throws(() => verifyRunEvidence({ evidenceRoot: evidence, runID: manifest.run_id, deploymentManifestPath, runtimeDatabasePath: databasePath }), /sidecar mismatch/);
});

test("spawn tool aborts an author that only points at a pre-existing artifact", async () => {
  const worktree = fs.mkdtempSync(path.join(os.tmpdir(), "design-tools-false-pass-"));
  const { manifest, packet } = manifestFor(worktree, "proposal", "author-no-write");
  fs.mkdirSync(path.dirname(manifest.exact_write_paths[0]), { recursive: true });
  fs.writeFileSync(manifest.exact_write_paths[0], "pre-existing\n");
  const store = new EvidenceStore(fs.mkdtempSync(path.join(os.tmpdir(), "design-tools-evidence-")), "module-tools");
  const runtime = new RuntimeAdapter(store);
  const client = {
    session: {
      create: async () => ({ data: { id: "child", parentID: "parent", version: "1.18.18" } }),
      prompt: async (request: any) => {
        runtime.onSessionCreated({ id: "child", parentID: "parent", version: "1.18.18" });
        runtime.onChatMessage(
          { sessionID: "child", agent: manifest.expected_agent, model: manifest.expected_model, messageID: request.body.messageID, variant: "high" },
          request.body.parts,
        );
        return { data: { info: { id: "assistant", parentID: request.body.messageID, finish: "stop" }, parts: [{ type: "text", text: "done" }] } };
      },
    },
  };
  const guarded = createDesignGateTools({ client, store, runtime });
  await assert.rejects(
    guarded.tool.design_spawn_stage.execute({ manifest_json: canonicalJson(manifest), packet_base64: packet.toString("base64") }, context(worktree)),
    /phase|writer chain/,
  );
  assert.equal(store.get(manifest.run_id).state, "ABORTED");
});

test("author writes multiple artifacts across sequential AssistantMessages", async () => {
  const worktree = fs.mkdtempSync(path.join(os.tmpdir(), "design-tools-multi-artifact-"));
  const store = new EvidenceStore(fs.mkdtempSync(path.join(os.tmpdir(), "design-tools-evidence-")), "module-multi-artifact");
  const proposal = manifestFor(worktree, "proposal", "multi-dependency-proposal").manifest;
  closeAuthorStage(store, proposal, "proposal\n");
  const design = manifestFor(worktree, "design-specs", "multi-design-specs").manifest;
  dependOn(design, [proposal]);
  const specPath = path.join(worktree, "openspec", "changes", design.change_id, "specs", "gate", "spec.md");
  design.exact_write_paths.push(specPath);
  design.expected_artifacts.push({ path: specPath, required: true });
  design.manifest_sha256 = manifestDigest(design);
  const checked = validateManifest(design);
  store.create(checked);
  store.setChild(checked.run_id, "multi-child", "multi-input");
  store.provisionalBind(checked.run_id);
  const client = { session: { message: async (request: any) => ({ data: { info: {
    id: request.path.messageID,
    role: "assistant",
    sessionID: "multi-child",
    parentID: "multi-input",
    agent: checked.expected_agent,
    providerID: "openai",
    modelID: "gpt-5.6-sol",
    variant: "high",
  } } }) } };
  const guarded = createDesignGateTools({ client, store, runtime: new RuntimeAdapter(store) });
  for (const [index, artifact] of checked.exact_write_paths.entries()) {
    fs.mkdirSync(path.dirname(artifact), { recursive: true });
    const args = {
      run_id: checked.run_id,
      manifest_nonce: checked.nonce,
      manifest_sha256: checked.manifest_sha256!,
      operation_nonce: `multi-operation-${index}`,
      exact_path: artifact,
      base_sha256: "-",
      full_content_base64: Buffer.from(`artifact-${index}\n`).toString("base64"),
    };
    const messageID = `multi-assistant-${index}`;
    guarded.beforeTool("design_artifact_write", "multi-child", `multi-call-${index}`, args);
    await guarded.tool.design_artifact_write.execute(args, context(worktree, {
      sessionID: "multi-child",
      messageID,
      agent: checked.expected_agent,
    }));
    guarded.afterTool("design_artifact_write", "multi-child", `multi-call-${index}`, { ok: true });
  }
  store.setOutput(checked.run_id, "multi-output", "complete", sha256(canonicalJson([{ type: "text", text: "complete" }])));
  store.finalize(checked.run_id, "PASS", { multi_artifact: true });
  const lease = store.get(checked.run_id);
  assert.equal(lease.state, "CLOSED");
  assert.deepEqual(lease.writes.map((write) => write.assistant_message_id), ["multi-assistant-0", "multi-assistant-1"]);
  assert.deepEqual(checked.exact_write_paths.map((artifact) => fs.readFileSync(artifact, "utf8")), ["artifact-0\n", "artifact-1\n"]);
});

test("spawn tool fails closed for empty output and SDK child mismatch", async () => {
  for (const scenario of ["empty", "child-mismatch"] as const) {
    const worktree = fs.mkdtempSync(path.join(os.tmpdir(), `design-tools-${scenario}-`));
    const { manifest, packet } = manifestFor(worktree, "proposal", `spawn-${scenario}`);
    fs.mkdirSync(path.dirname(manifest.exact_write_paths[0]), { recursive: true });
    const store = new EvidenceStore(fs.mkdtempSync(path.join(os.tmpdir(), "design-tools-evidence-")), `module-${scenario}`);
    const runtime = new RuntimeAdapter(store);
    const client = {
      session: {
        create: async () => ({ data: { id: "child", parentID: scenario === "child-mismatch" ? "wrong-parent" : "parent", version: "1.18.18" } }),
        prompt: async (request: any) => {
          runtime.onSessionCreated({ id: "child", parentID: "parent", version: "1.18.18" });
          runtime.onChatMessage(
            { sessionID: "child", agent: manifest.expected_agent, model: manifest.expected_model, messageID: request.body.messageID, variant: "high" },
            request.body.parts,
          );
          return { data: { info: { id: "assistant", parentID: request.body.messageID }, parts: [] } };
        },
      },
    };
    const guarded = createDesignGateTools({ client, store, runtime });
    await assert.rejects(
      guarded.tool.design_spawn_stage.execute({ manifest_json: canonicalJson(manifest), packet_base64: packet.toString("base64") }, context(worktree)),
      scenario === "empty" ? /no correlatable usable output/ : /invalid child session/,
    );
    assert.equal(store.get(manifest.run_id).state, "ABORTED");
  }
});

test("critic stage requires canonical output and runtime assistant-parent correlation", async () => {
  const worktree = fs.mkdtempSync(path.join(os.tmpdir(), "design-tools-critic-"));
  const store = new EvidenceStore(fs.mkdtempSync(path.join(os.tmpdir(), "design-tools-evidence-")), "module-tools");
  const proposal = manifestFor(worktree, "proposal", "dependency-proposal").manifest;
  closeAuthorStage(store, proposal, "proposal\n");
  const design = manifestFor(worktree, "design-specs", "dependency-design").manifest;
  dependOn(design, [proposal]);
  const specPath = path.join(worktree, "openspec", "changes", "card-550-design-planner-contract", "specs", "gate", "spec.md");
  design.exact_write_paths.push(specPath);
  design.expected_artifacts.push({ path: specPath, required: true });
  design.manifest_sha256 = manifestDigest(design);
  closeAuthorStage(store, design, {
    [design.exact_write_paths[0]]: `${GENERATED_BEGIN}\nold\n${GENERATED_END}\n`,
    [specPath]: "spec\n",
  });
  const tasks = manifestFor(worktree, "tasks", "dependency-tasks").manifest;
  dependOn(tasks, [design]);
  closeAuthorStage(store, tasks, "tasks\n");
  const { manifest } = manifestFor(worktree, "critique-a", "critic-positive");
  dependOn(manifest, [tasks]);
  const sourceDigest = addCritiqueContext(manifest);
  const packet = buildCritiquePacket(manifest);
  manifest.packet_sha256 = sha256(packet);
  manifest.manifest_sha256 = manifestDigest(manifest);
  const runtime = new RuntimeAdapter(store);
  const assessment = canonicalJson({
    assessment: "A",
    findings: [],
    lineage_id: "lineage",
    resolutions: [],
    round: 0,
    schema: "design-critique-assessment.v1",
    source_digest: sourceDigest,
  });
  const client = {
    session: {
      create: async () => ({ data: { id: "critic-child", parentID: "parent", version: "1.18.18" } }),
      message: async () => ({ data: { info: {
        id: "critic-assistant",
        role: "assistant", sessionID: "critic-child", parentID: store.get(manifest.run_id).input_message_id,
        agent: manifest.expected_agent, providerID: "openai", modelID: "gpt-5.6-sol", variant: "high",
      } } }),
      prompt: async (request: any) => {
        runtime.onSessionCreated({ id: "critic-child", parentID: "parent", version: "1.18.18" });
        runtime.onChatMessage(
          { sessionID: "critic-child", agent: manifest.expected_agent, model: manifest.expected_model, messageID: request.body.messageID, variant: "high" },
          request.body.parts,
        );
        return { data: { info: { id: "critic-assistant", parentID: request.body.messageID, finish: "stop" }, parts: [{ type: "text", text: assessment }] } };
      },
    },
  };
  const guarded = createDesignGateTools({ client, store, runtime });
  const forged = structuredClone(manifest);
  forged.run_id = "critic-forged-source";
  forged.nonce = "critic-forged-source-nonce";
  const forgedProposal = forged.sources.find((source) => source.logical_path.endsWith("/proposal.md"))!;
  forgedProposal.bytes = Buffer.from("forged proposal\n").toString("base64");
  forgedProposal.sha256 = sha256(Buffer.from("forged proposal\n"));
  forged.critique_context!.source_digest = normativeDigestFromSources(forged);
  const forgedPacket = buildCritiquePacket(forged);
  forged.packet_sha256 = sha256(forgedPacket);
  forged.manifest_sha256 = manifestDigest(forged);
  assert.throws(() => store.create(validateManifest(forged)), /current transitive author output/);

  const opaque = structuredClone(manifest);
  opaque.run_id = "critic-opaque-packet";
  opaque.nonce = "critic-opaque-packet-nonce";
  const opaquePacket = Buffer.from(canonicalJson({ source: "not-the-normative-artifacts" }));
  opaque.packet_sha256 = sha256(opaquePacket);
  opaque.manifest_sha256 = manifestDigest(opaque);
  await assert.rejects(guarded.tool.design_spawn_stage.execute({ manifest_json: canonicalJson(opaque), packet_base64: opaquePacket.toString("base64") }, context(worktree)), /canonical normative packet/);

  await guarded.tool.design_spawn_stage.execute({ manifest_json: canonicalJson(manifest), packet_base64: packet.toString("base64") }, context(worktree));
  assert.equal(store.get(manifest.run_id).state, "CLOSED");

  const criticB = manifestFor(worktree, "critique-b", "critic-b-positive");
  dependOn(criticB.manifest, [tasks, manifest]);
  const assessmentABytes = Buffer.from(store.get(manifest.run_id).output_text_base64!, "base64");
  criticB.manifest.sources.push({ logical_path: "assessment-a.json", encoding: "base64", bytes: assessmentABytes.toString("base64"), sha256: sha256(assessmentABytes) });
  addCritiqueContext(criticB.manifest);
  criticB.manifest.packet_sha256 = sha256(buildCritiquePacket(criticB.manifest));
  criticB.manifest.manifest_sha256 = manifestDigest(criticB.manifest);
  assert.equal(criticB.manifest.packet_sha256, manifest.packet_sha256);
  assert.equal(buildCritiquePacket(criticB.manifest).toString("base64"), packet.toString("base64"));
  assert.match(buildPacket(manifest, packet), /assignment="critique-a"/);
  assert.match(buildPacket(criticB.manifest, packet), /assignment="critique-b"/);
  const assessmentB = canonicalJson({ ...JSON.parse(assessment), assessment: "B" });
  const clientB = {
    session: {
      create: async () => ({ data: { id: "critic-b-child", parentID: "parent", version: "1.18.18" } }),
      message: async () => ({ data: { info: {
        id: "critic-b-assistant", role: "assistant", sessionID: "critic-b-child", parentID: store.get(criticB.manifest.run_id).input_message_id,
        agent: criticB.manifest.expected_agent, providerID: "openai", modelID: "gpt-5.6-sol", variant: "high",
      } } }),
      prompt: async (request: any) => {
        runtime.onSessionCreated({ id: "critic-b-child", parentID: "parent", version: "1.18.18" });
        runtime.onChatMessage(
          { sessionID: "critic-b-child", agent: criticB.manifest.expected_agent, model: criticB.manifest.expected_model, messageID: request.body.messageID, variant: "high" },
          request.body.parts,
        );
        return { data: { info: { id: "critic-b-assistant", parentID: request.body.messageID, finish: "stop" }, parts: [{ type: "text", text: assessmentB }] } };
      },
    },
  };
  const guardedB = createDesignGateTools({ client: clientB, store, runtime });
  await guardedB.tool.design_spawn_stage.execute({ manifest_json: canonicalJson(criticB.manifest), packet_base64: packet.toString("base64") }, context(worktree));
  assert.equal(store.get(criticB.manifest.run_id).state, "CLOSED");
  assert.notEqual(store.get(manifest.run_id).child_session_id, store.get(criticB.manifest.run_id).child_session_id);

  const synthesis = manifestFor(worktree, "critique-synthesis", "critique-synthesis-positive");
  dependOn(synthesis.manifest, [manifest, criticB.manifest]);
  const assessmentBBytes = Buffer.from(store.get(criticB.manifest.run_id).output_text_base64!, "base64");
  synthesis.manifest.sources.push(
    { logical_path: "assessment-a.json", encoding: "base64", bytes: assessmentABytes.toString("base64"), sha256: sha256(assessmentABytes) },
    { logical_path: "assessment-b.json", encoding: "base64", bytes: assessmentBBytes.toString("base64"), sha256: sha256(assessmentBBytes) },
  );
  addCritiqueContext(synthesis.manifest);
  const checkedSynthesis = validateManifest(synthesis.manifest);
  store.create(checkedSynthesis);
  store.setChild(checkedSynthesis.run_id, "synthesis-child", "synthesis-input");
  store.provisionalBind(checkedSynthesis.run_id);
  const generated = synthesizeAssessments({ assessmentABytes, assessmentBBytes, inheritedBlockingIds: [] });
  const synthesisContent = insertGeneratedBlock(fs.readFileSync(checkedSynthesis.exact_write_paths[0]), generated.generatedBlockBytes);
  const synthesisArgs = {
    run_id: checkedSynthesis.run_id,
    manifest_nonce: checkedSynthesis.nonce,
    manifest_sha256: checkedSynthesis.manifest_sha256!,
    operation_nonce: "synthesis-operation",
    exact_path: checkedSynthesis.exact_write_paths[0],
    base_sha256: sha256(fs.readFileSync(checkedSynthesis.exact_write_paths[0])),
    full_content_base64: synthesisContent.toString("base64"),
  };
  const synthesisClient = { session: { message: async () => ({ data: { info: {
    id: "synthesis-assistant", role: "assistant", sessionID: "synthesis-child", parentID: "synthesis-input",
    agent: "design-planner", providerID: "openai", modelID: "gpt-5.6-sol", variant: "high",
  } } }) } };
  const guardedSynthesis = createDesignGateTools({ client: synthesisClient, store, runtime });
  guardedSynthesis.beforeTool("design_artifact_write", "synthesis-child", "synthesis-call", synthesisArgs);
  await guardedSynthesis.tool.design_artifact_write.execute(synthesisArgs, context(worktree, { sessionID: "synthesis-child", messageID: "synthesis-assistant", agent: "design-planner" }));
  store.setOutput(checkedSynthesis.run_id, "synthesis-output", "PASS", sha256(canonicalJson([{ type: "text", text: "PASS" }])));
  store.finalize(checkedSynthesis.run_id, "PASS", { synthesis: true });
  assert.equal(store.get(checkedSynthesis.run_id).state, "CLOSED");
});

test("spawn stage is restricted to the primary build orchestrator", async () => {
  const worktree = fs.mkdtempSync(path.join(os.tmpdir(), "design-tools-orchestrator-"));
  const { manifest, packet } = manifestFor(worktree, "proposal", "wrong-orchestrator");
  const store = new EvidenceStore(fs.mkdtempSync(path.join(os.tmpdir(), "design-tools-evidence-")), "module-tools");
  const guarded = createDesignGateTools({ client: {}, store, runtime: new RuntimeAdapter(store) });
  await assert.rejects(guarded.tool.design_spawn_stage.execute({ manifest_json: canonicalJson(manifest), packet_base64: packet.toString("base64") }, context(worktree, { agent: "general" })), /orchestrator-only/);
});

test("process-scoped guard denies unknown tools and aborts the bound lease", () => {
  const worktree = fs.mkdtempSync(path.join(os.tmpdir(), "design-tools-deny-"));
  const { manifest } = manifestFor(worktree, "proposal", "deny-unknown");
  fs.mkdirSync(path.dirname(manifest.exact_write_paths[0]), { recursive: true });
  const store = new EvidenceStore(fs.mkdtempSync(path.join(os.tmpdir(), "design-tools-evidence-")), "module-tools");
  store.create(manifest);
  const guarded = createDesignGateTools({ client: {}, store, runtime: new RuntimeAdapter(store) });
  assert.throws(() => guarded.beforeTool("bash", "other-session", "call", {}), /denies tool bash/);
  store.abort(manifest.run_id, "denied tool");
  assert.equal(store.get(manifest.run_id).state, "ABORTED");
});

test("read-only OpenSpec tool executes only the structured allowlist", async () => {
  const worktree = path.resolve(gateRoot, "..", "..", "..");
  const { manifest } = manifestFor(worktree, "proposal", "openspec-readonly");
  const store = new EvidenceStore(fs.mkdtempSync(path.join(os.tmpdir(), "design-tools-evidence-")), "module-tools");
  store.create(manifest);
  const guarded = createDesignGateTools({ client: {}, store, runtime: new RuntimeAdapter(store) });
  const result = await guarded.tool.design_openspec_readonly.execute({
    run_id: manifest.run_id,
    operation: "status",
    change: manifest.change_id,
  }, context(worktree));
  assert.match((result as any).output, /"changeName"/);
  const readonlyEvent = fs.readFileSync(path.join(store.root, manifest.run_id, "journal.jsonl"), "utf8").split("\n").filter(Boolean)
    .map((line) => JSON.parse(line)).find((event) => event.event === "openspec.readonly");
  assert.equal(readonlyEvent.data.executable, fs.realpathSync(process.execPath));
  assert.equal(readonlyEvent.data.entrypoint, deployment.openspec.path);
  await assert.rejects(guarded.tool.design_openspec_readonly.execute({
    run_id: manifest.run_id,
    operation: "apply" as any,
    change: manifest.change_id,
    artifact: "apply",
  }, context(worktree)), /not allowlisted/);
  store.abort(manifest.run_id, "test complete");
});
