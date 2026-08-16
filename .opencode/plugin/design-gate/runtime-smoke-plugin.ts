import fs from "node:fs";
import path from "node:path";
import { tool } from "@opencode-ai/plugin";

export function createRuntimeSmokeLaunchTool(spawnStage: any) {
  const configuredRoot = process.env.DESIGN_RUNTIME_SMOKE_LAUNCH_ROOT;
  if (!configuredRoot) throw new Error("DESIGN_RUNTIME_SMOKE_LAUNCH_ROOT is required");
  const launchRoot = fs.realpathSync(configuredRoot);
  return tool({
    description: "Run one exact Design runtime-smoke launch file.",
    args: { path: tool.schema.string() },
    async execute(args, context) {
      const resolved = fs.realpathSync(args.path);
      if (!resolved.startsWith(`${launchRoot}${path.sep}`) || !resolved.endsWith(".json")) {
        throw new Error("unsafe runtime-smoke launch path");
      }
      const launch = JSON.parse(fs.readFileSync(resolved, "utf8"));
      const started = await spawnStage.execute({
        action: "start",
        manifest_json: launch.manifest_json,
        packet_base64: launch.packet_base64,
      }, context);
      const runID = started?.metadata?.run_id ?? JSON.parse(started?.output ?? "{}").run_id;
      if (!runID) throw new Error("runtime-smoke launch did not return a run ID");
      return spawnStage.execute({ action: "collect", run_id: runID }, context);
    },
  });
}
