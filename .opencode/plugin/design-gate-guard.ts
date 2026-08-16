import type { Plugin } from "@opencode-ai/plugin";
import { EvidenceStore } from "./design-gate/lease-evidence.js";
import { RuntimeAdapter } from "./design-gate/runtime-adapter.js";
import { createDesignGateTools } from "./design-gate/spawn-readonly-tools.js";

export default (async ({ client }) => {
  const store = new EvidenceStore();
  const runtime = new RuntimeAdapter(store);
  const guarded = createDesignGateTools({ client, store, runtime });

  return {
    tool: guarded.tool,
    event: async ({ event }: any) => {
      try {
        runtime.onEvent(event);
      } catch (error) {
        const sessionID = event.properties?.info?.id ?? event.properties?.sessionID;
        const lease = store.findBySession(sessionID) ?? store.active()[0];
        if (lease) store.abort(lease.run_id, error instanceof Error ? error.message : String(error));
        throw error;
      }
    },
    "chat.message": async (input: any, output: any) => {
      try {
        runtime.onChatMessage(input, Array.isArray(output?.parts) ? output.parts : []);
      } catch (error) {
        const lease = store.findBySession(input.sessionID) ?? store.active()[0];
        if (lease) store.abort(lease.run_id, error instanceof Error ? error.message : String(error));
        throw error;
      }
    },
    "tool.execute.before": async (input: any, output: any) => {
      try {
        guarded.beforeTool(input.tool, input.sessionID, input.callID, output.args);
      } catch (error) {
        const lease = store.findBySession(input.sessionID) ?? store.active()[0];
        if (lease) store.abort(lease.run_id, error instanceof Error ? error.message : String(error));
        throw error;
      }
    },
    "tool.execute.after": async (input: any, output: any) => {
      guarded.afterTool(input.tool, input.sessionID, input.callID, output);
    },
  };
}) satisfies Plugin;
