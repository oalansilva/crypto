import { spawnSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

const projectRoot = path.resolve(import.meta.dirname, "..", "..", "..");
const dist = path.join(import.meta.dirname, "dist");
if (fs.existsSync(dist)) throw new Error("check:unbuilt requires a clean checkout without design-gate/dist");
const pathCandidates = (process.env.PATH ?? "").split(path.delimiter).filter(Boolean).map((directory) => path.join(directory, "opencode"));
const executable = [process.env.OPENCODE_BIN, path.join(os.homedir(), ".opencode", "bin", "opencode"), ...pathCandidates]
  .find((candidate) => candidate && fs.existsSync(candidate));
if (!executable) throw new Error("OpenCode executable not found");
const result = spawnSync(executable, ["debug", "agent", "build"], {
  cwd: projectRoot,
  encoding: "utf8",
  shell: false,
  env: { ...process.env, NO_COLOR: "1" },
  maxBuffer: 8 * 1024 * 1024,
});
if (result.status !== 0) throw new Error(`unbuilt guard failed to load safely: ${result.stderr}`);
const profile = JSON.parse(result.stdout);
for (const name of ["design_spawn_stage", "design_openspec_readonly", "design_artifact_write"]) {
  if (!(name in (profile.tools ?? {}))) throw new Error(`unbuilt guard did not register ${name}`);
}
const contractProbe = spawnSync(process.execPath, [
  "--import", "tsx", "--input-type=module", "-e",
  "import { validateManifest } from './plugin/design-gate/contract.ts'; try { validateManifest({}); process.exit(2); } catch (error) { console.log(error.message); }",
], { cwd: path.join(projectRoot, ".opencode"), encoding: "utf8", shell: false });
if (contractProbe.status !== 0 || !contractProbe.stdout.includes("Design gate is unbuilt")) {
  throw new Error(`unbuilt guard did not reject run startup fail-closed: ${contractProbe.stderr || contractProbe.stdout}`);
}
console.log(JSON.stringify({ schema: "design-gate-unbuilt-startup.v1", verdict: "PASS", pid: result.pid }));
