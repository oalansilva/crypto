/**
 * vision-router — roteamento automático de análise de imagem para o agente
 * vision (gpt-5.6-luna).
 *
 * O modelo default da sessão (deepseek-v4-flash) não aceita imagens. Quando
 * uma imagem entra no contexto (anexo no chat, screenshot de tool, imagem
 * baixada de card/issue do GitHub, artifact de CI, baseline/diff do QA
 * visual), o plugin:
 *
 *   - persiste o anexo em `.impeccable/attachments/` e marca a sessão;
 *   - substitui image parts por placeholder de texto com o caminho do
 *     arquivo (o request do modelo sem visão nunca recebe pixels);
 *   - injeta instrução de sistema para delegar o julgamento visual ao
 *     subagent `vision` (Luna);
 *   - registra evidência em `.impeccable/vision-router.jsonl`.
 *
 * Contract: nunca quebra o turno. Falhas são registradas e engolidas.
 */

import type { Plugin } from "@opencode-ai/plugin";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PROJECT_ROOT = path.resolve(__dirname, "..", "..");
const ATTACHMENTS_DIR = path.join(PROJECT_ROOT, ".impeccable", "attachments");
const LOG_FILE = path.join(PROJECT_ROOT, ".impeccable", "vision-router.jsonl");

const IMAGE_EXTS = new Set([".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".tiff", ".heic"]);
const VISION_MODEL_ID = "gpt-5.6-luna";

/** sessões com imagem detectada no turno corrente */
const SESSIONS_WITH_IMAGE = new Set<string>();

function log(entry: Record<string, unknown>): void {
  try {
    fs.mkdirSync(path.dirname(LOG_FILE), { recursive: true });
    fs.appendFileSync(
      LOG_FILE,
      JSON.stringify({ ts: new Date().toISOString(), ...entry }) + "\n",
    );
  } catch { /* swallow */ }
}

function isImageName(name: string | undefined | null): boolean {
  if (!name) return false;
  return IMAGE_EXTS.has(path.extname(name).toLowerCase());
}

function isImagePart(part: any): boolean {
  if (!part || typeof part !== "object") return false;
  if (part.type === "image") return true;
  if (part.type === "file") {
    return isImageName(part.file?.path) || isImageName(part.filename) || isImageName(part.path);
  }
  return false;
}

/** Extrai a imagem (data URL base64) de uma part e grava em attachments. */
function persistImagePart(part: any): string | null {
  if (!part || typeof part !== "object") return null;
  const raw = part.data ?? part.image ?? (part.image_url && part.image_url.url);
  if (typeof raw !== "string") return null;
  const m = /^data:image\/(png|jpe?g|webp|gif|bmp);base64,(.+)$/.exec(raw);
  if (!m) return null;
  const ext = m[1] === "jpeg" ? "jpg" : m[1];
  try {
    fs.mkdirSync(ATTACHMENTS_DIR, { recursive: true });
    const filename = `attachment-${Date.now()}-${Math.random().toString(36).slice(2, 8)}.${ext}`;
    const out = path.join(ATTACHMENTS_DIR, filename);
    fs.writeFileSync(out, Buffer.from(m[2], "base64"));
    return out;
  } catch {
    return null;
  }
}

/** Caminho legível para o placeholder (arquivo de anexo/part file). */
function imageFilePath(part: any): string | null {
  if (!part || typeof part !== "object") return null;
  const p = part.file?.path ?? part.path ?? part.filename ?? null;
  return typeof p === "string" && p ? p : null;
}

export default (async () => {
  return {
    "chat.message": async (
      input: { sessionID: string; model?: { providerID: string; modelID: string } },
      output: { parts?: any[] },
    ) => {
      const parts = output?.parts;
      if (!Array.isArray(parts) || parts.length === 0) return;
      const images = parts.filter(isImagePart);
      if (images.length === 0) return;
      const saved: string[] = [];
      for (const p of images) {
        const persisted = persistImagePart(p);
        if (persisted) saved.push(persisted);
        else {
          const filePath = imageFilePath(p);
          if (filePath) saved.push(filePath);
        }
      }
      SESSIONS_WITH_IMAGE.add(input.sessionID);
      log({
        event: "chat-image",
        sessionID: input.sessionID,
        source: "chat",
        files: saved,
        model: input.model ? `${input.model.providerID}/${input.model.modelID}` : null,
      });
    },

    "tool.execute.after": async (input: { tool: string; sessionID: string; args: any }) => {
      const args = input.args && typeof input.args === "object" ? input.args : {};
      let visual = false;
      const touched: string[] = [];
      if (input.tool === "write" || input.tool === "edit") {
        const p = args.filePath ?? args.path ?? null;
        if (typeof p === "string" && isImageName(p)) {
          visual = true;
          touched.push(p);
        }
      }
      if (input.tool === "bash" && typeof args.command === "string") {
        const cmd = args.command;
        if (
          /(screenshot|playwright|run download|upload-artifact|artifacts|\.png|\.jpg|\.webp|--update-snapshots)/i.test(cmd)
        ) {
          visual = true;
        }
      }
      if (!visual) return;
      SESSIONS_WITH_IMAGE.add(input.sessionID);
      log({
        event: "tool-image",
        sessionID: input.sessionID,
        source: "tool",
        tool: input.tool,
        files: touched,
      });
    },

    "experimental.chat.messages.transform": async (_input: {}, output: any) => {
      const messages = output?.messages;
      if (!Array.isArray(messages)) return;
      for (const msg of messages) {
        const parts = msg?.parts;
        if (!Array.isArray(parts)) continue;
        for (let i = 0; i < parts.length; i++) {
          const part = parts[i];
          if (!isImagePart(part)) continue;
          const filePath = imageFilePath(part) ?? persistImagePart(part);
          parts[i] = {
            type: "text",
            text: filePath
              ? `[imagem anexada: ${filePath} — não analisar pixels aqui; delegar o julgamento visual ao subagent vision (gpt-5.6-luna)]`
              : "[imagem anexada — não analisar pixels aqui; delegar o julgamento visual ao subagent vision (gpt-5.6-luna)]",
          };
        }
      }
    },

    "experimental.chat.system.transform": async (
      input: { sessionID?: string; model?: { providerID: string; modelID: string } },
      output: { system: string[] },
    ) => {
      if (!input.sessionID || !SESSIONS_WITH_IMAGE.has(input.sessionID)) return;
      const isVision = input.model?.modelID === VISION_MODEL_ID;
      if (isVision) return;
      output.system.push(
        [
          "[vision-router] Uma imagem está no contexto desta sessão e o modelo atual não tem visão.",
          "Regra obrigatória: NUNCA interprete pixels nem descreva a imagem a partir de suposições.",
          "Delegue o julgamento visual ao subagent `vision` (model gpt-5.6-luna) via a ferramenta task e retorne o resultado ao usuário.",
          "Use o caminho do arquivo informado no placeholder da imagem para o subagent vision abrir o arquivo real.",
        ].join("\n"),
      );
    },
  };
}) satisfies Plugin;
