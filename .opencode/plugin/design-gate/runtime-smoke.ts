import { spawn, spawnSync, type ChildProcess } from "node:child_process";
import fs from "node:fs";
import { DatabaseSync } from "node:sqlite";
import net from "node:net";
import os from "node:os";
import path from "node:path";
import { randomUUID } from "node:crypto";
import { BUILD_ID, canonicalJson, sha256, type RunManifest } from "./contract.js";
import { verifyRunEvidence } from "./verifier.js";

const gateRoot = import.meta.dirname;
const opencodeRoot = path.resolve(gateRoot, "..", "..");
const sourceProjectRoot = path.resolve(opencodeRoot, "..");
const evidenceRoot = path.join(process.env.XDG_DATA_HOME || path.join(os.homedir(), ".local", "share"), "opencode", "design-gate");
const runID = `runtime-smoke-${randomUUID()}`;
const projectRoot = path.join(evidenceRoot, runID, "worktree");
const launchRoot = path.join(evidenceRoot, runID, "launches");
const sourceOpenCodeRoot = path.join(sourceProjectRoot, ".opencode");
const targetOpenCodeRoot = path.join(projectRoot, ".opencode");
fs.mkdirSync(projectRoot, { recursive: true, mode: 0o700 });
fs.mkdirSync(launchRoot, { recursive: true, mode: 0o700 });
for (const relative of ["opencode.json", "AGENTS.md", "rules.md"]) fs.copyFileSync(path.join(sourceProjectRoot, relative), path.join(projectRoot, relative));
fs.cpSync(sourceOpenCodeRoot, targetOpenCodeRoot, {
  recursive: true,
  filter: (source) => source !== path.join(sourceOpenCodeRoot, "node_modules") && !source.startsWith(path.join(sourceOpenCodeRoot, "plugin", "design-gate", "test-artifacts")),
});
fs.symlinkSync(path.join(sourceOpenCodeRoot, "node_modules"), path.join(targetOpenCodeRoot, "node_modules"), "dir");
const sourceChangeRoot = path.join(sourceProjectRoot, "openspec", "changes", "card-550-design-planner-contract");
const targetChangeRoot = path.join(projectRoot, "openspec", "changes", "card-550-design-planner-contract");
fs.mkdirSync(path.dirname(targetChangeRoot), { recursive: true });
fs.cpSync(sourceChangeRoot, targetChangeRoot, { recursive: true });
const gitInit = spawnSync("/usr/bin/git", ["init", "--quiet", projectRoot], { shell: false, encoding: "utf8" });
if (gitInit.status !== 0) throw new Error(`runtime smoke sandbox git init failed: ${gitInit.stderr}`);
const deploymentManifestPath = path.join(targetOpenCodeRoot, "plugin", "design-gate", "dist", "deployment-manifest.json");
const deployment = JSON.parse(fs.readFileSync(deploymentManifestPath, "utf8"));
const deploymentDigest = fs.readFileSync(path.join(gateRoot, "dist", "deployment-manifest.sha256"), "utf8").trim();
const proposalPath = path.join(targetChangeRoot, "proposal.md");
const proposal = fs.readFileSync(proposalPath);
const firstOperationNonce = randomUUID();
const secondOperationNonce = randomUUID();
const firstSuffix = Buffer.from(`\n<!-- ${runID} attributable first writer smoke -->\n`, "utf8");
const secondSuffix = Buffer.from(`<!-- ${runID} attributable second writer smoke -->\n`, "utf8");
const packet = Buffer.from(canonicalJson({
  schema: "design-gate-runtime-smoke.v2",
  instruction: "Call design_artifact_write once for each writer_args item in order. Copy manifest_sha256 from the design-gate marker. Use every other argument byte-for-byte. Wait for each tool result before issuing the next call in a new assistant message. Then return a short non-empty text result.",
  writer_args: [{
    run_id: runID,
    manifest_nonce: `${runID}-nonce`,
    operation_nonce: firstOperationNonce,
    exact_path: proposalPath,
    base_sha256: sha256(proposal),
    safe_patch_json: canonicalJson([{
      start: proposal.length,
      end: proposal.length,
      expected_sha256: sha256(Buffer.alloc(0)),
      replacement_base64: firstSuffix.toString("base64"),
    }]),
  }, {
    run_id: runID,
    manifest_nonce: `${runID}-nonce`,
    operation_nonce: secondOperationNonce,
    exact_path: proposalPath,
    base_sha256: sha256(Buffer.concat([proposal, firstSuffix])),
    safe_patch_json: canonicalJson([{
      start: proposal.length + firstSuffix.length,
      end: proposal.length + firstSuffix.length,
      expected_sha256: sha256(Buffer.alloc(0)),
      replacement_base64: secondSuffix.toString("base64"),
    }]),
  }],
}));
const manifest: RunManifest = {
  schema: "design-authoring-manifest.v1",
  run_id: runID,
  change_id: "card-550-design-planner-contract",
  card_id: "550",
  stage: "proposal",
  nonce: `${runID}-nonce`,
  parent_session_id: "PARENT_SESSION_IS_BOUND_BY_TOOL_CONTEXT",
  worktree: projectRoot,
  expected_agent: "design-planner",
  expected_model: { providerID: "openai", modelID: "gpt-5.6-sol" },
  expected_variant: "high",
  exact_write_paths: [proposalPath],
  expected_artifacts: [{ path: proposalPath, required: true }],
  sources: [],
  dependency_run_ids: [],
  packet_sha256: sha256(packet),
  build_id: BUILD_ID,
  deployment_manifest_sha256: deploymentDigest,
  profile_sha256: deployment.files[".opencode/agent/design-planner.md"],
  config_sha256: deployment.files["opencode.json"],
  schema_sha256: deployment.files[".opencode/plugin/design-gate/schemas/assessment-v1.json"],
  opencode_version: "1.18.18",
  deadline_at: new Date(Date.now() + 3 * 60_000).toISOString(),
};

// The parent ID is runtime-owned. The orchestrator passes a placeholder and the
// guard binds it to ToolContext before validating the sealed manifest.
const launchPath = path.join(launchRoot, `${runID}.json`);
fs.writeFileSync(launchPath, `${canonicalJson({ manifest_json: canonicalJson(manifest), packet_base64: packet.toString("base64") })}\n`, { mode: 0o600 });
const prompt = `Invoke design_runtime_launch_file once with path ${launchPath}. Use no other tool and return only its final result.`;
const executable = process.env.OPENCODE_BIN || path.join(os.homedir(), ".opencode", "bin", "opencode");
const runtimeDatabasePath = path.join(os.homedir(), ".local", "share", "opencode", "opencode.db");
const title = `Card #550 canonical runtime smoke ${runID}`;
const runtimeEnvironment = {
  ...process.env,
  DESIGN_RUNTIME_SMOKE_LAUNCH_ROOT: launchRoot,
};

function freePort(): Promise<number> {
  return new Promise((resolve, reject) => {
    const server = net.createServer();
    server.once("error", reject);
    server.listen(0, "127.0.0.1", () => {
      const address = server.address();
      const port = typeof address === "object" && address ? address.port : 0;
      server.close((error) => error ? reject(error) : resolve(port));
    });
  });
}

function run(args: string[]): Promise<void> {
  return new Promise((resolve, reject) => {
    const child = spawn(executable, args, { cwd: projectRoot, env: runtimeEnvironment, shell: false, stdio: ["ignore", "pipe", "pipe"] });
    const stderr: Buffer[] = [];
    let bytes = 0;
    for (const stream of [child.stdout, child.stderr]) stream.on("data", (chunk: Buffer) => {
      bytes += chunk.length;
      if (stream === child.stderr) stderr.push(chunk);
      if (bytes > 32 * 1024 * 1024) child.kill("SIGKILL");
    });
    child.once("error", reject);
    child.once("close", (code) => code === 0 ? resolve() : reject(new Error(`opencode run failed (${code}): ${Buffer.concat(stderr).toString("utf8").slice(-4000)}`)));
  });
}

function waitForServer(server: ChildProcess, port: number): Promise<void> {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error("OpenCode server startup timed out")), 30_000);
    const inspect = (chunk: Buffer) => {
      if (!chunk.toString("utf8").includes(`http://127.0.0.1:${port}`)) return;
      clearTimeout(timer);
      resolve();
    };
    server.stdout?.on("data", inspect);
    server.stderr?.on("data", inspect);
    server.once("close", (code) => reject(new Error(`OpenCode server exited before readiness (${code})`)));
  });
}

function assertStartSucceeded(parentID: string): void {
  const leasePath = path.join(evidenceRoot, runID, "lease.json");
  if (fs.existsSync(leasePath)) {
    const lease = JSON.parse(fs.readFileSync(leasePath, "utf8"));
    if (lease.state === "ABORTED") throw new Error(`runtime child aborted: ${lease.failure}`);
    return;
  }
  const database = new DatabaseSync(runtimeDatabasePath, { readOnly: true });
  try {
    const parts = database.prepare("SELECT data FROM part WHERE session_id = ? ORDER BY time_created, id").all(parentID) as Array<{ data: string }>;
    const failed = parts.map((item) => JSON.parse(item.data)).find((part) => part.type === "tool" && part.tool === "design_spawn_stage" && part.state?.status === "error");
    throw new Error(`runtime start produced no lease${failed?.state?.error ? `: ${failed.state.error}` : ""}`);
  } finally {
    database.close();
  }
}

const port = await freePort();
const server = spawn(executable, ["serve", "--hostname", "127.0.0.1", "--port", String(port)], {
  cwd: projectRoot,
  env: runtimeEnvironment,
  shell: false,
  stdio: ["ignore", "pipe", "pipe"],
});
let serverOutputBytes = 0;
for (const stream of [server.stdout, server.stderr]) stream.on("data", (chunk: Buffer) => {
  serverOutputBytes = Math.min(Number.MAX_SAFE_INTEGER, serverOutputBytes + chunk.length);
});
try {
  await waitForServer(server, port);
  const url = `http://127.0.0.1:${port}`;
  await run(["run", "--attach", url, "--dir", projectRoot, "--agent", "build", "--model", "openai/gpt-5.6-sol", "--variant", "high", "--format", "json", "--title", title, prompt]);
  const database = new DatabaseSync(runtimeDatabasePath, { readOnly: true });
  const parent = database.prepare("SELECT id FROM session WHERE title = ? ORDER BY time_created DESC LIMIT 1").get(title) as { id: string } | undefined;
  database.close();
  if (!parent) throw new Error("runtime smoke parent session was not found");
  assertStartSucceeded(parent.id);
  const verified = verifyRunEvidence({ evidenceRoot, runID, deploymentManifestPath, runtimeDatabasePath });
  if (verified.verdict !== "PASS") throw new Error("runtime smoke verifier did not pass");
  const lease = JSON.parse(fs.readFileSync(path.join(evidenceRoot, runID, "lease.json"), "utf8"));
  const expectedFirst = sha256(Buffer.concat([proposal, firstSuffix]));
  const expectedFinal = Buffer.concat([proposal, firstSuffix, secondSuffix]);
  if (lease.writes.length !== 2 || lease.writes[0].operation_nonce !== firstOperationNonce || lease.writes[1].operation_nonce !== secondOperationNonce ||
      new Set(lease.writes.map((write: any) => write.assistant_message_id)).size !== 2 || lease.writes[0].before_sha256 !== sha256(proposal) ||
      lease.writes[0].after_sha256 !== expectedFirst || lease.writes[1].before_sha256 !== expectedFirst ||
      lease.writes[1].after_sha256 !== sha256(expectedFinal) || !fs.readFileSync(proposalPath).equals(expectedFinal)) {
    throw new Error("runtime smoke did not preserve the exact two-write chain");
  }
  console.log(canonicalJson({ schema: "design-gate-runtime-smoke-result.v1", run_id: runID, build_id: BUILD_ID, ...verified }));
} catch (error) {
  throw new Error(`${error instanceof Error ? error.message : String(error)} (server_output_bytes=${serverOutputBytes})`);
} finally {
  server.kill("SIGTERM");
}
