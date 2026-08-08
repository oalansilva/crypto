/**
 * Impeccable design hook — opencode adapter.
 *
 * Maps opencode lifecycle events onto the canonical impeccable detector
 * (`./.agents/skills/impeccable/scripts/hook.mjs`):
 *
 *   - tool.execute.after (edit/write/apply_patch) -> PostToolUse pass
 *   - event session.idle (end of agent turn)     -> Stop deep pass
 *
 * Contract: never break a turn. Failures are swallowed and logged; the
 * detector output is audited by the hook itself (`.impeccable/`).
 */

import type { Plugin } from "@opencode-ai/plugin";
import { spawn } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PROJECT_ROOT = path.resolve(__dirname, "..", "..");
const HOOK_SCRIPT = path.join(
  PROJECT_ROOT,
  ".agents",
  "skills",
  "impeccable",
  "scripts",
  "hook.mjs",
);

const TRIGGER_TOOLS = new Set(["edit", "write", "apply_patch"]);
const STOPPED_SESSIONS = new Set<string>();

function runHookScript(payload: Record<string, unknown>): Promise<void> {
  return new Promise((resolve) => {
    const child = spawn("node", [HOOK_SCRIPT], {
      cwd: PROJECT_ROOT,
      env: { ...process.env, IMPECCABLE_HOOK_HARNESS: "claude" },
      stdio: ["pipe", "ignore", "ignore"],
    });
    child.stdin.on("error", () => {});
    child.stdin.write(JSON.stringify(payload));
    child.stdin.end();
    child.on("error", () => resolve());
    child.on("exit", () => resolve());
  });
}

export default (async () => {
  return {
    "tool.execute.after": async (input: {
      tool: string;
      sessionID: string;
      args: any;
    }) => {
      if (!TRIGGER_TOOLS.has(input.tool)) return;
      const args = input.args && typeof input.args === "object" ? input.args : {};
      const toolInput: Record<string, unknown> = {};
      if (input.tool === "apply_patch") {
        if (typeof args.command === "string") toolInput.command = args.command;
      } else {
        const filePath = args.filePath ?? args.path ?? args.file_path;
        if (typeof filePath === "string") toolInput.file_path = filePath;
      }
      if (Object.keys(toolInput).length === 0) return;
      await runHookScript({
        hook_event_name: "PostToolUse",
        session_id: input.sessionID,
        cwd: PROJECT_ROOT,
        tool_name: input.tool,
        tool_input: toolInput,
      });
    },

    event: async (input: { event: { type: string; properties?: any } }) => {
      const event = input.event;
      if (!event || event.type !== "session.idle") return;
      const sessionID: string | undefined = event.properties?.sessionID;
      if (!sessionID || STOPPED_SESSIONS.has(sessionID)) return;
      STOPPED_SESSIONS.add(sessionID);
      await runHookScript({
        hook_event_name: "Stop",
        session_id: sessionID,
        cwd: PROJECT_ROOT,
      });
    },
  };
}) satisfies Plugin;
