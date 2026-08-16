import { spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

const here = import.meta.dirname;
const dist = path.join(here, "dist");
const buildScript = path.join(here, "build.mjs");
const profileScript = path.join(here, "check-profiles.mjs");
const evidenceRoot = path.join(process.env.XDG_DATA_HOME || path.join(os.homedir(), ".local", "share"), "opencode", "design-gate");
const sha256 = (bytes) => createHash("sha256").update(bytes).digest("hex");

if (fs.existsSync(evidenceRoot)) {
  for (const entry of fs.readdirSync(evidenceRoot, { withFileTypes: true })) {
    const leasePath = path.join(evidenceRoot, entry.name, "lease.json");
    if (!entry.isDirectory() || !fs.existsSync(leasePath)) continue;
    const lease = JSON.parse(fs.readFileSync(leasePath, "utf8"));
    if (!['CLOSED', 'ABORTED'].includes(lease.state)) throw new Error(`active Design lease blocks cutover: ${lease.run_id}`);
  }
}

function build() {
  const result = spawnSync(process.execPath, [buildScript], { encoding: "utf8", shell: false, env: process.env });
  if (result.status !== 0) throw new Error(result.stderr || "Design gate build failed");
  return JSON.parse(result.stdout.trim());
}

function checkProfiles() {
  const result = spawnSync(process.execPath, [profileScript], { encoding: "utf8", shell: false, env: process.env });
  if (result.status !== 0) throw new Error(result.stderr || result.stdout || "profile check failed");
  return JSON.parse(result.stdout.trim());
}

const temp = fs.mkdtempSync(path.join(os.tmpdir(), "design-gate-cutover-"));
const first = build();
fs.cpSync(dist, path.join(temp, "first"), { recursive: true });
const second = build();
fs.cpSync(dist, path.join(temp, "second"), { recursive: true });
if (first.build_id === second.build_id || first.deployment_manifest_sha256 === second.deployment_manifest_sha256) {
  throw new Error("independent pre-build identity was reused");
}

fs.rmSync(dist, { recursive: true, force: true });
fs.cpSync(path.join(temp, "first"), dist, { recursive: true });
const rollbackProfiles = checkProfiles();
const rollbackDigest = sha256(fs.readFileSync(path.join(dist, "deployment-manifest.json")));
if (rollbackDigest !== first.deployment_manifest_sha256) throw new Error("rollback did not restore a coherent first build");

fs.rmSync(dist, { recursive: true, force: true });
fs.cpSync(path.join(temp, "second"), dist, { recursive: true });
const cutoverProfiles = checkProfiles();
const cutoverDigest = sha256(fs.readFileSync(path.join(dist, "deployment-manifest.json")));
if (cutoverDigest !== second.deployment_manifest_sha256) throw new Error("cutover did not restore a coherent second build");

const evidence = {
  schema: "design-gate-cutover-check.v1",
  freeze: "no active process-scoped Design leases",
  first_build_id: first.build_id,
  first_deployment_sha256: first.deployment_manifest_sha256,
  second_build_id: second.build_id,
  second_deployment_sha256: second.deployment_manifest_sha256,
  rollback_verified: true,
  fresh_process_profile_matrix_verified: true,
  rollback_profiles: rollbackProfiles.fresh_processes,
  cutover_profiles: cutoverProfiles.fresh_processes,
};
fs.writeFileSync(path.join(dist, "cutover-evidence.json"), `${JSON.stringify(evidence)}\n`, { mode: 0o600 });
console.log(JSON.stringify(evidence));
