import { spawnSync } from "node:child_process";
import fs from "node:fs";

const base = process.argv[2] || "origin/develop";
const result = spawnSync("/usr/bin/git", ["diff", "--name-only", base], { encoding: "utf8", shell: false });
if (result.status !== 0) throw new Error(result.stderr || "git diff failed");
const status = spawnSync("/usr/bin/git", ["status", "--porcelain", "--untracked-files=all"], { encoding: "utf8", shell: false });
if (status.status !== 0) throw new Error(status.stderr || "git status failed");
const allowed = [
  /^\.gitignore$/,
  /^opencode\.json$/,
  /^AGENTS\.md$/,
  /^rules\.md$/,
  /^\.github\/workflows\/ci\.yml$/,
  /^\.agents\/skills\/design-critic\/SKILL\.md$/,
  /^\.opencode\/agent\/design-(?:planner|critic-readonly)\.md$/,
  /^\.opencode\/plugin\/design-gate-guard\.ts$/,
  /^\.opencode\/plugin\/design-gate\//,
  /^\.opencode\/(package(-lock)?\.json|tsconfig\.json)$/,
  /^openspec\/changes\/card-550-design-planner-contract\//,
];
const files = [...new Set([
  ...result.stdout.split("\n").filter(Boolean),
  ...status.stdout.split("\n").filter(Boolean).map((line) => line.slice(3)),
])];
const outside = files.filter((file) => !allowed.some((pattern) => pattern.test(file)));
if (outside.length) {
  console.error(`card #550 scope violation:\n${outside.join("\n")}`);
  process.exit(1);
}
const configDiff = spawnSync("/usr/bin/git", ["diff", base, "--", "opencode.json"], { encoding: "utf8", shell: false });
if (/^[+-]\s*"(?:model|small_model)"/m.test(configDiff.stdout)) {
  console.error("card #550 must not change default model or small_model");
  process.exit(1);
}
const baseConfigResult = spawnSync("/usr/bin/git", ["show", `${base}:opencode.json`], { encoding: "utf8", shell: false });
if (baseConfigResult.status !== 0) throw new Error(baseConfigResult.stderr || "cannot read base opencode.json");
const baseConfig = JSON.parse(baseConfigResult.stdout);
const currentConfig = JSON.parse(await fs.promises.readFile("../opencode.json", "utf8"));
const expectedPlugins = [...new Set([...(baseConfig.plugin ?? []), ".opencode/plugin/design-gate-guard.ts"])];
const expectedPermissions = {
  ...(baseConfig.permission ?? {}),
  design_spawn_stage: "deny",
  design_openspec_readonly: "deny",
  design_artifact_write: "deny",
};
const expectedAgents = {
  ...(baseConfig.agent ?? {}),
  build: {
    ...(baseConfig.agent?.build ?? {}),
    permission: {
      ...(baseConfig.agent?.build?.permission ?? {}),
      design_spawn_stage: "allow",
      design_openspec_readonly: "allow",
      design_artifact_write: "deny",
    },
  },
};
const expectedTools = {
  ...(baseConfig.tools ?? {}),
  design_spawn_stage: true,
  design_openspec_readonly: true,
  design_artifact_write: true,
};
const withoutDedicated = (value) => {
  const clone = structuredClone(value);
  delete clone.plugin;
  delete clone.permission;
  delete clone.tools;
  delete clone.agent;
  return JSON.stringify(clone);
};
if (withoutDedicated(currentConfig) !== withoutDedicated(baseConfig) || JSON.stringify(currentConfig.plugin) !== JSON.stringify(expectedPlugins) ||
    JSON.stringify(currentConfig.permission) !== JSON.stringify(expectedPermissions) || JSON.stringify(currentConfig.tools) !== JSON.stringify(expectedTools) ||
    JSON.stringify(currentConfig.agent) !== JSON.stringify(expectedAgents)) {
  console.error("card #550 may only add the dedicated guard and its three explicit tool availability/permission entries to opencode.json");
  process.exit(1);
}
console.log(`card #550 scope check passed (${files.length} files)`);
