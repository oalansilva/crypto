import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { BUILD_ID, buildPacket, manifestDigest, sha256, type RunManifest } from "../contract.js";
import { EvidenceStore } from "../lease-evidence.js";
import { RuntimeAdapter } from "../runtime-adapter.js";

function setup() {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "runtime-adapter-"));
  const store = new EvidenceStore(path.join(root, "evidence"), "module");
  const packet = Buffer.from("immutable packet");
  const manifest: RunManifest = {
    schema: "design-authoring-manifest.v1",
    run_id: "runtime-run",
    change_id: "card-550-design-planner-contract",
    card_id: "550",
    stage: "proposal",
    nonce: "runtime-nonce",
    parent_session_id: "parent",
    worktree: root,
    expected_agent: "design-planner",
    expected_model: { providerID: "openai", modelID: "gpt-5.6-sol" },
    expected_variant: "high",
    exact_write_paths: [path.join(root, "proposal.md")],
    expected_artifacts: [],
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
  manifest.manifest_sha256 = manifestDigest(manifest);
  store.create(manifest);
  store.setChild(manifest.run_id, "child", "input-message");
  const adapter = new RuntimeAdapter(store);
  adapter.onSessionCreated({ id: "child", parentID: "parent", version: "1.18.18" });
  return { adapter, store, manifest, packet };
}

test("runtime adapter binds exact child route and input message", () => {
  const { adapter, store, manifest, packet } = setup();
  adapter.onChatMessage(
    {
      sessionID: "child",
      agent: manifest.expected_agent,
      model: manifest.expected_model,
      messageID: "input-message",
      variant: "high",
    },
    [{ type: "text", text: buildPacket(manifest, packet) }],
  );
  assert.equal(store.get(manifest.run_id).provisional, true);
});

test("runtime adapter rejects extra input parts and aborts a failed child without a waiter", () => {
  const { adapter, store, manifest, packet } = setup();
  assert.throws(() => adapter.onChatMessage(
    { sessionID: "child", agent: manifest.expected_agent, model: manifest.expected_model, messageID: "input-message", variant: "high" },
    [{ type: "text", text: buildPacket(manifest, packet) }, { type: "text", text: "injected" }],
  ), /exactly one text part/);
  adapter.onEvent({ type: "session.error", properties: { sessionID: "child" } });
  assert.equal(store.get(manifest.run_id).state, "ABORTED");
});

test("runtime adapter fails closed on route mismatch", () => {
  const { adapter, manifest, packet } = setup();
  assert.throws(
    () => adapter.onChatMessage(
      { sessionID: "child", agent: manifest.expected_agent, model: manifest.expected_model, messageID: "input-message", variant: "default" },
      [{ type: "text", text: buildPacket(manifest, packet) }],
    ),
    /variant mismatch/,
  );
});

test("runtime adapter defers an absent input variant to AssistantMessage verification", () => {
  const { adapter, store, manifest, packet } = setup();
  adapter.onChatMessage(
    { sessionID: "child", agent: manifest.expected_agent, model: manifest.expected_model, messageID: "input-message" },
    [{ type: "text", text: buildPacket(manifest, packet) }],
  );
  assert.equal(store.get(manifest.run_id).provisional, true);
});

test("assistant correlation requires the input message as parent", async () => {
  const { adapter, store, manifest } = setup();
  store.provisionalBind(manifest.run_id);
  const client = {
    session: {
      message: async () => ({ data: { info: {
        id: "assistant",
        role: "assistant",
        sessionID: "child",
        parentID: "input-message",
        agent: manifest.expected_agent,
        providerID: "openai",
        modelID: "gpt-5.6-sol",
        variant: "high",
      } } }),
    },
  };
  await adapter.assertAssistantParent(client, manifest.run_id, "assistant", manifest.worktree);
  const wrong = {
    session: {
      message: async () => ({ data: { info: {
        id: "assistant",
        role: "assistant",
        sessionID: "child",
        parentID: "other",
        agent: manifest.expected_agent,
        providerID: "openai",
        modelID: "gpt-5.6-sol",
        variant: "high",
      } } }),
    },
  };
  await assert.rejects(adapter.assertAssistantParent(wrong, manifest.run_id, "assistant", manifest.worktree), /parent correlation/);
});
