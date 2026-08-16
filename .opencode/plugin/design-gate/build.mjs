import { createHash, randomUUID } from "node:crypto";
import { spawnSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const opencodeRoot = path.resolve(here, "..", "..");
const projectRoot = path.resolve(opencodeRoot, "..");
const dist = path.join(here, "dist");
const writerSource = path.join(here, "native", "design_writer.c");
const writerBinary = path.join(dist, "design-writer");
const buildIDPath = path.join(dist, "build-id");

const sha256 = (bytes) => createHash("sha256").update(bytes).digest("hex");
const fileHash = (file) => sha256(fs.readFileSync(file));
const canonical = (value) => {
  if (Array.isArray(value)) return value.map(canonical);
  if (value && typeof value === "object") {
    return Object.fromEntries(Object.entries(value).sort(([a], [b]) => a.localeCompare(b)).map(([key, item]) => [key, canonical(item)]));
  }
  return value;
};

fs.mkdirSync(dist, { recursive: true });
const contractText = fs.readFileSync(path.join(here, "contract.ts"), "utf8");
const protocolVersion = /PROTOCOL_VERSION = "([^"]+)"/.exec(contractText)?.[1];
if (!protocolVersion) throw new Error("PROTOCOL_VERSION is missing from contract.ts");
const buildID = randomUUID();
fs.writeFileSync(buildIDPath, `${buildID}\n`, { mode: 0o600 });
const compile = spawnSync("/usr/bin/gcc", [
  "-O2", "-std=c11", "-Wall", "-Wextra",
  `-DDESIGN_BUILD_ID=\"${buildID}\"`,
  `-DDESIGN_PROTOCOL_VERSION=\"${protocolVersion}\"`,
  writerSource, "-o", writerBinary,
], {
  cwd: projectRoot,
  encoding: "utf8",
  shell: false,
});
if (compile.status !== 0) throw new Error(`native writer build failed:\n${compile.stderr}`);
fs.chmodSync(writerBinary, 0o700);

const tracked = [
  ".opencode/agent/design-planner.md",
  ".opencode/agent/design-critic-readonly.md",
  ".opencode/plugin/design-gate-guard.ts",
  ".opencode/plugin/design-gate/contract.ts",
  ".opencode/plugin/design-gate/runtime-adapter.ts",
  ".opencode/plugin/design-gate/runtime-smoke.ts",
  ".opencode/plugin/design-gate/runtime-smoke-plugin.ts",
  ".opencode/plugin/design-gate/lease-evidence.ts",
  ".opencode/plugin/design-gate/native-writer.ts",
  ".opencode/plugin/design-gate/spawn-readonly-tools.ts",
  ".opencode/plugin/design-gate/assessments.ts",
  ".opencode/plugin/design-gate/verifier.ts",
  ".opencode/plugin/design-gate/build.mjs",
  ".opencode/plugin/design-gate/check-unbuilt.mjs",
  ".opencode/plugin/design-gate/README.md",
  ".opencode/plugin/design-gate/check-profiles.mjs",
  ".opencode/plugin/design-gate/check-cutover.mjs",
  ".opencode/plugin/design-gate/check-scope.mjs",
  ".opencode/plugin/design-gate/native/design_writer.c",
  ".opencode/plugin/design-gate/schemas/assessment-v1.json",
  ".opencode/package.json",
  ".opencode/package-lock.json",
  ".opencode/tsconfig.json",
  "opencode.json",
];
for (const relative of tracked) {
  if (!fs.existsSync(path.join(projectRoot, relative))) throw new Error(`deployment input missing: ${relative}`);
}

const optionalExecutable = (candidates) => candidates.find((candidate) => candidate && fs.existsSync(candidate));
const opencodeBinary = optionalExecutable([process.env.OPENCODE_BIN, path.join(os.homedir(), ".opencode", "bin", "opencode")]);
const openspecBinary = optionalExecutable([process.env.OPENSPEC_BIN, "/usr/bin/openspec"]);
const versionOf = (executable) => {
  if (!executable) return undefined;
  const result = spawnSync(executable, ["--version"], { encoding: "utf8", shell: false });
  if (result.status !== 0) throw new Error(`failed to read version from ${executable}`);
  return result.stdout.trim();
};
const manifest = canonical({
  schema: "design-gate-deployment.v1",
  build_id: buildID,
  protocol_version: protocolVersion,
  created_at: new Date().toISOString(),
  platform: `${process.platform}-${process.arch}`,
  files: Object.fromEntries(tracked.map((relative) => [relative, fileHash(path.join(projectRoot, relative))])),
  build_identity: { path: buildIDPath, sha256: fileHash(buildIDPath) },
  native_writer: { path: writerBinary, sha256: fileHash(writerBinary) },
  opencode: opencodeBinary ? { path: opencodeBinary, sha256: fileHash(opencodeBinary), version: versionOf(opencodeBinary) } : { unavailable: true },
  openspec: openspecBinary ? {
    path: fs.realpathSync(openspecBinary),
    sha256: fileHash(fs.realpathSync(openspecBinary)),
    version: versionOf(openspecBinary),
    interpreter: { path: fs.realpathSync(process.execPath), sha256: fileHash(fs.realpathSync(process.execPath)), version: process.version },
  } : { unavailable: true },
});
const bytes = `${JSON.stringify(manifest)}\n`;
fs.writeFileSync(path.join(dist, "deployment-manifest.json"), bytes, { mode: 0o600 });
fs.writeFileSync(path.join(dist, "deployment-manifest.sha256"), `${sha256(bytes)}\n`, { mode: 0o600 });
console.log(JSON.stringify({ build_id: buildID, deployment_manifest_sha256: sha256(bytes), writer: writerBinary }));
