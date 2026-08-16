import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { spawnSync } from "node:child_process";
import { BUILD_ID, PROTOCOL_VERSION, sha256 } from "../contract.js";
import { runNativeWriter } from "../native-writer.js";

const executable = path.resolve(import.meta.dirname, "..", "dist", "design-writer");

test("native writer creates and atomically replaces an exact file", { skip: !fs.existsSync(executable) }, () => {
  const worktree = fs.mkdtempSync(path.join(os.tmpdir(), "design-writer-"));
  const artifact = path.join(worktree, "proposal.md");
  const created = runNativeWriter({ worktree, exactPath: artifact, expectedBaseSha256: null, content: Buffer.from("first\n"), executable });
  assert.equal(created.before_sha256, null);
  assert.equal(fs.readFileSync(artifact, "utf8"), "first\n");
  const replaced = runNativeWriter({
    worktree,
    exactPath: artifact,
    expectedBaseSha256: sha256(Buffer.from("first\n")),
    content: Buffer.from("second\n"),
    executable,
  });
  assert.equal(replaced.before_sha256, sha256(Buffer.from("first\n")));
  assert.equal(fs.readFileSync(artifact, "utf8"), "second\n");
});

test("native writer verifies existing files larger than one hash chunk", { skip: !fs.existsSync(executable) }, () => {
  const worktree = fs.mkdtempSync(path.join(os.tmpdir(), "design-writer-large-"));
  const artifact = path.join(worktree, "design.md");
  const existing = Buffer.alloc(33_077, "a");
  const replacement = Buffer.from("replacement\n");
  fs.writeFileSync(artifact, existing);
  const result = runNativeWriter({
    worktree,
    exactPath: artifact,
    expectedBaseSha256: sha256(existing),
    content: replacement,
    executable,
  });
  assert.equal(result.before_sha256, sha256(existing));
  assert.deepEqual(fs.readFileSync(artifact), replacement);
});

test("native writer rejects stale digests and symlink parents", { skip: !fs.existsSync(executable) }, () => {
  const worktree = fs.mkdtempSync(path.join(os.tmpdir(), "design-writer-negative-"));
  const artifact = path.join(worktree, "artifact.md");
  fs.writeFileSync(artifact, "current");
  assert.throws(
    () => runNativeWriter({ worktree, exactPath: artifact, expectedBaseSha256: "0".repeat(64), content: Buffer.from("bad"), executable }),
    /base digest mismatch/,
  );
  assert.throws(
    () => runNativeWriter({ worktree, exactPath: artifact, expectedBaseSha256: sha256(Buffer.from("current")), content: Buffer.from("bad"), executable, expectedExecutableSha256: "0".repeat(64) }),
    /executable digest mismatch/,
  );
  const outside = fs.mkdtempSync(path.join(os.tmpdir(), "design-writer-outside-"));
  fs.symlinkSync(outside, path.join(worktree, "linked"));
  assert.throws(
    () => runNativeWriter({ worktree, exactPath: path.join(worktree, "linked", "escape.md"), expectedBaseSha256: null, content: Buffer.from("bad"), executable }),
    /openat2 parent/,
  );
});

test("native writer helper is terminated at its configured timeout", () => {
  const worktree = fs.mkdtempSync(path.join(os.tmpdir(), "design-writer-timeout-"));
  const slowHelper = path.join(worktree, "slow-helper");
  fs.writeFileSync(slowHelper, "#!/bin/sh\nsleep 2\n", { mode: 0o700 });
  assert.throws(() => runNativeWriter({
    worktree,
    exactPath: path.join(worktree, "artifact.md"),
    expectedBaseSha256: null,
    content: Buffer.from("content"),
    executable: slowHelper,
    timeoutMs: 20,
  }), /ETIMEDOUT|timed out/i);
});

test("native writer fails closed on injected fsync and rename failures", () => {
  const source = path.resolve(import.meta.dirname, "..", "native", "design_writer.c");
  for (const [macro, expected] of [
    ["DESIGN_TEST_FAIL_TEMP_FSYNC", /fsync temporary destination/],
    ["DESIGN_TEST_FAIL_RENAME", /atomic rename destination/],
    ["DESIGN_TEST_FAIL_DIRECTORY_FSYNC", /fsync destination directory/],
  ] as const) {
    const worktree = fs.mkdtempSync(path.join(os.tmpdir(), "design-writer-fault-"));
    const helper = path.join(worktree, "fault-helper");
    const compile = spawnSync("/usr/bin/gcc", [
      "-O0", "-std=c11", "-Wall", "-Wextra", `-D${macro}`,
      `-DDESIGN_BUILD_ID=\"${BUILD_ID}\"`, `-DDESIGN_PROTOCOL_VERSION=\"${PROTOCOL_VERSION}\"`, source, "-o", helper,
    ], { encoding: "utf8", shell: false });
    assert.equal(compile.status, 0, compile.stderr);
    assert.throws(() => runNativeWriter({
      worktree,
      exactPath: path.join(worktree, "artifact.md"),
      expectedBaseSha256: null,
      content: Buffer.from("content"),
      executable: helper,
    }), expected);
  }
});
