import { spawnSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

const projectRoot = path.resolve(import.meta.dirname, "..", "..", "..");
const executable = [process.env.OPENCODE_BIN, path.join(os.homedir(), ".opencode", "bin", "opencode")]
  .find((candidate) => candidate && fs.existsSync(candidate));
if (!executable) throw new Error("OpenCode executable not found");

const profiles = [
  ["design-planner", true],
  ["design-critic-readonly", false],
];
const evidence = [];

for (const [name, writer] of profiles) {
  const result = spawnSync(executable, ["debug", "agent", name], {
    cwd: projectRoot,
    encoding: "utf8",
    shell: false,
    env: { ...process.env, NO_COLOR: "1" },
    maxBuffer: 8 * 1024 * 1024,
  });
  if (result.status !== 0) throw new Error(`${name}: opencode debug failed: ${result.stderr}`);
  const profile = JSON.parse(result.stdout);
  if (profile.model?.providerID !== "openai" || profile.model?.modelID !== "gpt-5.6-sol" || profile.variant !== "high") {
    throw new Error(`${name}: expected openai/gpt-5.6-sol variant high`);
  }
  if (profile.mode !== "subagent") throw new Error(`${name}: expected subagent mode`);
  for (const [tool, enabled] of Object.entries(profile.tools ?? {})) {
    const expected = writer && tool === "design_artifact_write";
    if (enabled !== expected) throw new Error(`${name}: effective tool ${tool}=${enabled}, expected ${expected}`);
  }
  for (const required of ["design_spawn_stage", "design_openspec_readonly", "design_artifact_write"]) {
    if (!(required in (profile.tools ?? {}))) throw new Error(`${name}: guard tool ${required} was not loaded`);
  }
  const wildcard = [...(profile.permission ?? [])].reverse().find((rule) => rule.permission === "*");
  if (wildcard?.action !== "deny") throw new Error(`${name}: final wildcard permission must deny`);
  const writerRule = [...(profile.permission ?? [])].reverse().find((rule) => rule.permission === "design_artifact_write" || rule.permission === "*");
  if (writerRule?.action !== (writer ? "allow" : "deny")) throw new Error(`${name}: writer permission order is unsafe`);
  evidence.push({
    name,
    pid: result.pid,
    model: `${profile.model.providerID}/${profile.model.modelID}`,
    variant: profile.variant,
    enabled_tools: Object.entries(profile.tools).filter(([, enabled]) => enabled).map(([tool]) => tool).sort(),
  });
}

const orchestratorResult = spawnSync(executable, ["debug", "agent", "build"], {
  cwd: projectRoot,
  encoding: "utf8",
  shell: false,
  env: { ...process.env, NO_COLOR: "1" },
  maxBuffer: 8 * 1024 * 1024,
});
if (orchestratorResult.status !== 0) throw new Error(`build: opencode debug failed: ${orchestratorResult.stderr}`);
const orchestrator = JSON.parse(orchestratorResult.stdout);
if (orchestrator.mode !== "primary") throw new Error("build: Design orchestrator must be a primary agent");
if (orchestrator.tools?.design_spawn_stage !== true || orchestrator.tools?.design_openspec_readonly !== true || orchestrator.tools?.design_artifact_write !== false) {
  throw new Error("build: orchestrator Design tool policy is unsafe");
}
evidence.push({
  name: "build",
  pid: orchestratorResult.pid,
  model: `${orchestrator.model?.providerID ?? "runtime"}/${orchestrator.model?.modelID ?? "selected"}`,
  variant: orchestrator.variant ?? "runtime-selected",
  enabled_tools: ["design_openspec_readonly", "design_spawn_stage"],
});

console.log(JSON.stringify({ schema: "design-profile-matrix.v1", fresh_processes: evidence }));
