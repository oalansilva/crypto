import assert from "node:assert/strict";
import test from "node:test";
import {
  GENERATED_BEGIN,
  GENERATED_END,
  BUILD_ID,
  applySafePatch,
  buildPacket,
  canonicalJson,
  manifestDigest,
  mergeAssessments,
  normativeDigest,
  parseAssessment,
  parsePacketText,
  sha256,
  validateManifest,
  type Assessment,
  type RunManifest,
} from "../contract.js";
import { assertGeneratedBlock, insertGeneratedBlock, synthesizeAssessments } from "../assessments.js";

function manifest(overrides: Partial<RunManifest> = {}): RunManifest {
  const packet = Buffer.from("packet");
  const worktree = "/tmp/design-gate-worktree";
  const proposalPath = `${worktree}/openspec/changes/card-550-design-planner-contract/proposal.md`;
  const base: RunManifest = {
    schema: "design-authoring-manifest.v1",
    run_id: "run-1",
    change_id: "card-550-design-planner-contract",
    card_id: "550",
    stage: "proposal",
    nonce: "nonce-1",
    parent_session_id: "parent-1",
    worktree,
    expected_agent: "design-planner",
    expected_model: { providerID: "openai", modelID: "gpt-5.6-sol" },
    expected_variant: "high",
    exact_write_paths: [proposalPath],
    expected_artifacts: [{ path: proposalPath, required: true }],
    sources: [],
    dependency_run_ids: [],
    packet_sha256: sha256(packet),
    build_id: BUILD_ID,
    deployment_manifest_sha256: "a".repeat(64),
    profile_sha256: "b".repeat(64),
    config_sha256: "c".repeat(64),
    schema_sha256: "d".repeat(64),
    opencode_version: "1.18.18",
    deadline_at: new Date(Date.now() + 60_000).toISOString(),
  };
  return { ...base, ...overrides };
}

test("manifest and complete packet round-trip", () => {
  const packet = Buffer.from("packet");
  const source = manifest();
  source.manifest_sha256 = manifestDigest(source);
  const checked = validateManifest(source);
  const prompt = buildPacket(checked, packet);
  const parsed = parsePacketText(prompt);
  assert.equal(parsed.nonce, source.nonce);
  assert.equal(parsed.manifestSha256, source.manifest_sha256);
  assert.deepEqual(parsed.packet, packet);
});

test("manifest rejects paths outside the worktree", () => {
  assert.throws(() => validateManifest(manifest({ exact_write_paths: ["/etc/passwd"] })), /outside worktree/);
});

test("safe patches require ordered source digests", () => {
  const original = Buffer.from("abcdef");
  const output = applySafePatch(original, [
    { start: 1, end: 3, expected_sha256: sha256(Buffer.from("bc")), replacement_base64: Buffer.from("XY").toString("base64") },
  ]);
  assert.equal(output.toString(), "aXYdef");
  assert.throws(
    () => applySafePatch(original, [{ start: 1, end: 3, expected_sha256: "0".repeat(64), replacement_base64: "" }]),
    /digest mismatch/,
  );
  assert.throws(() => applySafePatch(original, []), /at least one effective/);
  assert.throws(() => applySafePatch(original, [{ start: 1, end: 2, expected_sha256: sha256(Buffer.from("b")), replacement_base64: Buffer.from("b").toString("base64") }]), /must change/);
});

test("normative digest ignores only generated critique evidence", () => {
  const first = normativeDigest({
    proposal: Buffer.from("proposal"),
    design: Buffer.from(`before\n${GENERATED_BEGIN}\none\n${GENERATED_END}\nafter`),
    specs: [{ path: "specs/a/spec.md", bytes: Buffer.from("spec") }],
    tasks: Buffer.from("tasks"),
  });
  const second = normativeDigest({
    proposal: Buffer.from("proposal"),
    design: Buffer.from(`before\n${GENERATED_BEGIN}\ntwo\n${GENERATED_END}\nafter`),
    specs: [{ path: "specs/a/spec.md", bytes: Buffer.from("spec") }],
    tasks: Buffer.from("tasks"),
  });
  assert.equal(first, second);
});

function assessment(identity: "A" | "B", disposition: "resolved" | "open" = "resolved"): Assessment {
  return parseAssessment(
    canonicalJson({
      schema: "design-critique-assessment.v1",
      assessment: identity,
      lineage_id: "lineage",
      round: 2,
      source_digest: "b".repeat(64),
      resolutions: [{
        finding_id: "old-p1",
        prior_source_digest: "a".repeat(64),
        source_digest: "b".repeat(64),
        disposition,
        rationale: "checked",
      }],
      findings: [],
    }),
  );
}

test("manifest rejects unsafe identity, route, and in-worktree production paths", () => {
  assert.throws(() => validateManifest(manifest({ run_id: "../../escape" })), /unsafe manifest identifier/);
  assert.throws(() => validateManifest(manifest({ expected_variant: "default" })), /variant high/);
  assert.throws(
    () => validateManifest(manifest({
      exact_write_paths: ["/tmp/design-gate-worktree/opencode.json"],
      expected_artifacts: [{ path: "/tmp/design-gate-worktree/opencode.json", required: true }],
    })),
    /not allowed for stage/,
  );
  assert.throws(() => validateManifest(manifest({ expected_agent: "design-planner-candidate-v1" })), /not allowed for stage/);
  assert.throws(() => validateManifest(manifest({ deadline_at: new Date(Date.now() - 1).toISOString() })), /expired deadline/);
});

test("manifest rejects malformed packet/source encodings and unbound synthesis", () => {
  assert.throws(() => validateManifest(manifest({
    sources: [{ logical_path: "source", encoding: "base64", bytes: "not-base64", sha256: "a".repeat(64) }],
  })), /canonical base64/);
  const synthesis = manifest({
    stage: "critique-synthesis",
    expected_agent: "design-planner",
    exact_write_paths: ["/tmp/design-gate-worktree/openspec/changes/card-550-design-planner-contract/design.md"],
    expected_artifacts: [{ path: "/tmp/design-gate-worktree/openspec/changes/card-550-design-planner-contract/design.md", required: true }],
  });
  assert.throws(() => validateManifest(synthesis), /critique_context/);
});

test("assessment parser rejects non-canonical and extra fields", () => {
  const valid = assessment("A");
  assert.throws(() => parseAssessment(JSON.stringify(valid, null, 2)), /not canonical/);
  assert.throws(() => parseAssessment(canonicalJson({ ...valid, extra: true })), /envelope fields/);
});

test("conservative merge requires both critics to resolve inherited P1", () => {
  assert.equal(
    mergeAssessments({ assessmentA: assessment("A"), assessmentB: assessment("B"), inheritedBlockingIds: ["old-p1"] }).verdict,
    "PASS",
  );
  assert.equal(
    mergeAssessments({ assessmentA: assessment("A"), assessmentB: assessment("B", "open"), inheritedBlockingIds: ["old-p1"] }).verdict,
    "BLOCKED",
  );
});

test("assessment synthesis preserves exact critic bytes and inserts a byte-identical generated block", () => {
  const assessmentABytes = Buffer.from(canonicalJson(assessment("A")));
  const assessmentBBytes = Buffer.from(canonicalJson(assessment("B")));
  const synthesis = synthesizeAssessments({ assessmentABytes, assessmentBBytes, inheritedBlockingIds: ["old-p1"] });
  assert.equal(synthesis.verdict, "PASS");
  assert.match(synthesis.generatedBlockBytes.toString("utf8"), new RegExp(assessmentABytes.toString("base64")));
  const design = Buffer.from(`before\n${GENERATED_BEGIN}\nold\n${GENERATED_END}\nafter\n`);
  const inserted = insertGeneratedBlock(design, synthesis.generatedBlockBytes);
  assert.ok(inserted.includes(synthesis.generatedBlockBytes));
  assert.doesNotThrow(() => assertGeneratedBlock(inserted, synthesis.generatedBlockBytes));
  const changed = Buffer.from(synthesis.generatedBlockBytes);
  changed[0] ^= 1;
  assert.throws(() => assertGeneratedBlock(inserted, changed), /differs/);
});
