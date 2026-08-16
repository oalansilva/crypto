import { spawnSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { sha256 } from "./contract.js";
import { BUILD_ID, PROTOCOL_VERSION } from "./contract.js";

export type NativeWriterResult = {
  before_sha256: string | null;
  after_sha256: string;
  bytes: number;
  pid: number;
  ppid: number;
  build_id: string;
  protocol_version: string;
};

const HERE = path.dirname(fileURLToPath(import.meta.url));
export const DEFAULT_WRITER_PATH = path.join(HERE, "dist", "design-writer");

function u32(value: number): Buffer {
  const output = Buffer.alloc(4);
  output.writeUInt32BE(value);
  return output;
}

function u64(value: number): Buffer {
  const output = Buffer.alloc(8);
  output.writeBigUInt64BE(BigInt(value));
  return output;
}

export function encodeWriterRequest(input: {
  worktree: string;
  relativePath: string;
  expectedBaseSha256: string | null;
  content: Buffer;
}): Buffer {
  const root = Buffer.from(path.resolve(input.worktree));
  const relative = Buffer.from(input.relativePath);
  const base = Buffer.from(input.expectedBaseSha256 ?? "-");
  return Buffer.concat([
    Buffer.from("DGW1"),
    u32(root.length),
    u32(relative.length),
    u32(base.length),
    u64(input.content.length),
    root,
    relative,
    base,
    input.content,
  ]);
}

export function runNativeWriter(input: {
  worktree: string;
  exactPath: string;
  expectedBaseSha256: string | null;
  content: Buffer;
  executable?: string;
  expectedExecutableSha256?: string;
  timeoutMs?: number;
}): NativeWriterResult {
  const root = path.resolve(input.worktree);
  const exact = path.resolve(input.exactPath);
  const relativePath = path.relative(root, exact);
  if (!relativePath || relativePath.startsWith("..") || path.isAbsolute(relativePath)) {
    throw new Error("writer path is outside the worktree");
  }
  const executable = input.executable ?? DEFAULT_WRITER_PATH;
  const status = fs.statSync(executable);
  const currentUID = typeof process.getuid === "function" ? process.getuid() : status.uid;
  if (!status.isFile() || status.uid !== currentUID) throw new Error("unsafe native writer executable");
  if (input.expectedExecutableSha256 && sha256(fs.readFileSync(executable)) !== input.expectedExecutableSha256) {
    throw new Error("native writer executable digest mismatch");
  }
  const request = encodeWriterRequest({
    worktree: root,
    relativePath,
    expectedBaseSha256: input.expectedBaseSha256,
    content: input.content,
  });
  const result = spawnSync(executable, [], {
    input: request,
    cwd: root,
    env: { PATH: "/usr/bin:/bin", LANG: "C", LC_ALL: "C" },
    encoding: "utf8",
    shell: false,
    maxBuffer: 1024 * 1024,
    timeout: input.timeoutMs ?? 30_000,
  });
  if (result.error) throw result.error;
  if (result.status !== 0) throw new Error(`native writer failed (${result.status}): ${result.stderr.trim()}`);
  const parsed = JSON.parse(result.stdout) as NativeWriterResult;
  if (!/^[a-f0-9]{64}$/.test(parsed.after_sha256) || parsed.bytes !== input.content.length) {
    throw new Error("invalid native writer result");
  }
  if (!Number.isInteger(parsed.pid) || !Number.isInteger(parsed.ppid) || parsed.build_id !== BUILD_ID || parsed.protocol_version !== PROTOCOL_VERSION) {
    throw new Error("native writer identity mismatch");
  }
  return parsed;
}
