import { createHash, randomUUID } from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

export const SUPPORTED_OPENCODE_VERSION = "1.18.18";
export const PROTOCOL_VERSION = "design-gate.v1";
const BUILD_ID_PATH = path.join(path.dirname(fileURLToPath(import.meta.url)), "dist", "build-id");
export const BUILD_READY = fs.existsSync(BUILD_ID_PATH);
export const BUILD_ID = BUILD_READY ? fs.readFileSync(BUILD_ID_PATH, "utf8").trim() : "UNBUILT";
if (BUILD_READY && !/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/.test(BUILD_ID)) throw new Error("invalid pre-build BUILD_ID");
export const GENERATED_BEGIN = "<!-- BEGIN GENERATED DESIGN CRITIQUE EVIDENCE -->";
export const GENERATED_END = "<!-- END GENERATED DESIGN CRITIQUE EVIDENCE -->";
const SHA256_PATTERN = /^[a-f0-9]{64}$/;
const SAFE_ID_PATTERN = /^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$/;
const CHANGE_ID_PATTERN = /^[a-z0-9][a-z0-9-]{0,127}$/;
const AUTHOR_AGENTS = new Set(["design-planner"]);
const CRITIC_AGENTS = new Set(["design-critic-readonly"]);
const AUTHOR_STAGES = new Set<DesignStage>(["proposal", "design-specs", "tasks", "critique-synthesis"]);
const CRITIC_STAGES = new Set<DesignStage>(["critique-a", "critique-b"]);

export type DesignStage =
  | "proposal"
  | "design-specs"
  | "tasks"
  | "critique-a"
  | "critique-b"
  | "critique-synthesis";

export type SourceEntry = {
  logical_path: string;
  encoding: "base64";
  bytes: string;
  sha256: string;
};

export type RunManifest = {
  schema: "design-authoring-manifest.v1";
  run_id: string;
  change_id: string;
  card_id: string;
  stage: DesignStage;
  nonce: string;
  parent_session_id: string;
  worktree: string;
  expected_agent: string;
  expected_model: { providerID: string; modelID: string };
  expected_variant: string;
  exact_write_paths: string[];
  expected_artifacts: Array<{ path: string; required: boolean }>;
  sources: SourceEntry[];
  critique_context?: {
    lineage_id: string;
    round: number;
    source_digest: string;
    inherited_blocking_findings: Array<{ finding_id: string; prior_source_digest: string }>;
  };
  dependency_run_ids: string[];
  packet_sha256: string;
  build_id: string;
  deployment_manifest_sha256: string;
  profile_sha256: string;
  config_sha256: string;
  schema_sha256: string;
  opencode_version: string;
  deadline_at: string;
  guard_process?: {
    pid: number;
    ppid: number;
    executable: string;
    executable_sha256: string;
    process_started_at: string;
    module_instance_id: string;
  };
  manifest_sha256?: string;
};

export type Finding = {
  finding_id: string;
  severity: "P0" | "P1" | "P2";
  source_digest: string;
  summary: string;
  disposition_required: boolean;
};

export type Resolution = {
  finding_id: string;
  prior_source_digest: string;
  source_digest: string;
  disposition: "resolved" | "open";
  rationale: string;
};

export type Assessment = {
  schema: string;
  assessment: "A" | "B";
  lineage_id: string;
  round: number;
  source_digest: string;
  resolutions: Resolution[];
  findings: Finding[];
};

function canonicalize(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(canonicalize);
  if (value && typeof value === "object") {
    return Object.fromEntries(
      Object.entries(value as Record<string, unknown>)
        .sort(([left], [right]) => left.localeCompare(right))
        .map(([key, item]) => [key, canonicalize(item)]),
    );
  }
  return value;
}

export function canonicalJson(value: unknown): string {
  return JSON.stringify(canonicalize(value));
}

export function sha256(value: string | Buffer): string {
  return createHash("sha256").update(value).digest("hex");
}

export function decodeBase64(value: string): Buffer {
  if (typeof value !== "string" || value.length % 4 !== 0 || !/^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$/.test(value)) {
    throw new Error("invalid canonical base64");
  }
  const bytes = Buffer.from(value, "base64");
  if (bytes.toString("base64") !== value) throw new Error("invalid canonical base64");
  return bytes;
}

export function newNonce(): string {
  return randomUUID();
}

export function manifestDigest(manifest: RunManifest): string {
  const { manifest_sha256: _ignored, ...unsigned } = manifest;
  return sha256(canonicalJson(unsigned));
}

export function validateManifest(input: unknown): RunManifest {
  if (!input || typeof input !== "object") throw new Error("manifest must be an object");
  const manifest = input as RunManifest;
  if (!BUILD_READY) throw new Error("Design gate is unbuilt; run npm --prefix .opencode run build and start a fresh OpenCode process");
  if (manifest.schema !== "design-authoring-manifest.v1") throw new Error("unsupported manifest schema");
  for (const field of [
    "run_id",
    "change_id",
    "card_id",
    "nonce",
    "parent_session_id",
    "worktree",
    "expected_agent",
    "expected_variant",
    "packet_sha256",
    "build_id",
    "deployment_manifest_sha256",
    "profile_sha256",
    "config_sha256",
    "schema_sha256",
    "opencode_version",
    "deadline_at",
  ] as const) {
    if (typeof manifest[field] !== "string" || !manifest[field]) throw new Error(`manifest.${field} is required`);
  }
  if (!manifest.expected_model?.providerID || !manifest.expected_model.modelID) {
    throw new Error("manifest.expected_model is required");
  }
  if (!SAFE_ID_PATTERN.test(manifest.run_id) || !SAFE_ID_PATTERN.test(manifest.nonce)) throw new Error("unsafe manifest identifier");
  if (!CHANGE_ID_PATTERN.test(manifest.change_id) || !/^\d+$/.test(manifest.card_id)) throw new Error("invalid change or card identifier");
  if (![...AUTHOR_STAGES, ...CRITIC_STAGES].includes(manifest.stage)) throw new Error("unsupported Design stage");
  const expectedAgents = AUTHOR_STAGES.has(manifest.stage) ? AUTHOR_AGENTS : CRITIC_AGENTS;
  if (!expectedAgents.has(manifest.expected_agent)) throw new Error("agent is not allowed for stage");
  if (manifest.expected_model.providerID !== "openai" || manifest.expected_model.modelID !== "gpt-5.6-sol") {
    throw new Error("Design stages require openai/gpt-5.6-sol");
  }
  if (manifest.expected_variant !== "high") throw new Error("Design stages require variant high");
  if (![manifest.packet_sha256, manifest.deployment_manifest_sha256, manifest.profile_sha256, manifest.config_sha256, manifest.schema_sha256].every((item) => SHA256_PATTERN.test(item))) {
    throw new Error("invalid manifest digest");
  }
  if (!Array.isArray(manifest.exact_write_paths) || !Array.isArray(manifest.expected_artifacts)) {
    throw new Error("manifest path lists are required");
  }
  if (!Array.isArray(manifest.sources) || !Array.isArray(manifest.dependency_run_ids)) throw new Error("manifest sources and dependencies are required");
  if (new Set(manifest.dependency_run_ids).size !== manifest.dependency_run_ids.length || manifest.dependency_run_ids.some((item) => !SAFE_ID_PATTERN.test(item))) {
    throw new Error("unsafe or duplicate dependency run ID");
  }
  if (manifest.build_id !== BUILD_ID) throw new Error("build_id mismatch");
  if (manifest.opencode_version !== SUPPORTED_OPENCODE_VERSION) throw new Error("OpenCode version mismatch");
  if (!Number.isFinite(Date.parse(manifest.deadline_at)) || Date.parse(manifest.deadline_at) <= Date.now()) throw new Error("invalid or expired deadline");

  const root = path.resolve(manifest.worktree);
  const changeRoot = path.join(root, "openspec", "changes", manifest.change_id);
  const prototypeRoots = [
    path.join(changeRoot, "prototype"),
    path.join(root, "frontend", "public", "prototypes", manifest.change_id),
  ];
  const allowedForStage = (candidate: string): boolean => {
    const resolved = path.resolve(candidate);
    if (manifest.stage === "proposal") return resolved === path.join(changeRoot, "proposal.md");
    if (manifest.stage === "tasks") return resolved === path.join(changeRoot, "tasks.md");
    if (manifest.stage === "critique-synthesis") return resolved === path.join(changeRoot, "design.md");
    if (manifest.stage === "design-specs") {
      if (resolved === path.join(changeRoot, "design.md")) return true;
      const specRelative = path.relative(path.join(changeRoot, "specs"), resolved);
      if (specRelative && !specRelative.startsWith("..") && !path.isAbsolute(specRelative) && specRelative.endsWith("/spec.md")) return true;
      return prototypeRoots.some((prototypeRoot) => {
        const relative = path.relative(prototypeRoot, resolved);
        return Boolean(relative) && !relative.startsWith("..") && !path.isAbsolute(relative);
      });
    }
    return false;
  };
  for (const candidate of [...manifest.exact_write_paths, ...manifest.expected_artifacts.map((item) => item.path)]) {
    const resolved = path.resolve(candidate);
    const relative = path.relative(root, resolved);
    if (!relative || relative.startsWith("..") || path.isAbsolute(relative)) {
      throw new Error(`path outside worktree: ${candidate}`);
    }
    if (!allowedForStage(resolved)) throw new Error(`path is not allowed for stage ${manifest.stage}: ${candidate}`);
  }
  if (CRITIC_STAGES.has(manifest.stage) && (manifest.exact_write_paths.length || manifest.expected_artifacts.length)) {
    throw new Error("critic stages cannot declare artifacts");
  }
  const critiqueStage = CRITIC_STAGES.has(manifest.stage) || manifest.stage === "critique-synthesis";
  if (critiqueStage) {
    const critique = manifest.critique_context;
    if (!critique || !SAFE_ID_PATTERN.test(critique.lineage_id) || !Number.isInteger(critique.round) || critique.round < 0 || !SHA256_PATTERN.test(critique.source_digest)) {
      throw new Error("critique stage requires a valid critique_context");
    }
    const inherited = critique.inherited_blocking_findings;
    if (!Array.isArray(inherited) || new Set(inherited.map((item) => item.finding_id)).size !== inherited.length ||
        inherited.some((item) => !SAFE_ID_PATTERN.test(item.finding_id) || !SHA256_PATTERN.test(item.prior_source_digest))) {
      throw new Error("critique_context inherited findings are invalid");
    }
  } else if (manifest.critique_context !== undefined) {
    throw new Error("non-critique stage cannot declare critique_context");
  }
  if (AUTHOR_STAGES.has(manifest.stage)) {
    if (manifest.exact_write_paths.length === 0) throw new Error("author stage requires exact write paths");
    const required = new Set(manifest.expected_artifacts.filter((item) => item.required).map((item) => path.resolve(item.path)));
    if (manifest.expected_artifacts.length !== manifest.exact_write_paths.length || required.size !== manifest.exact_write_paths.length || manifest.exact_write_paths.some((item) => !required.has(path.resolve(item)))) {
      throw new Error("every author write path must be a required artifact");
    }
  }
  const exact = manifest.exact_write_paths.map((item) => path.resolve(item));
  if (new Set(exact).size !== exact.length) throw new Error("duplicate manifest path");
  const sourcePaths = new Set<string>();
  for (const source of manifest.sources) {
    if (source.encoding !== "base64") throw new Error("unsupported source encoding");
    if (!source.logical_path || path.isAbsolute(source.logical_path) || source.logical_path.split(/[\\/]/).includes("..") || sourcePaths.has(source.logical_path)) {
      throw new Error("unsafe or duplicate source path");
    }
    sourcePaths.add(source.logical_path);
    const bytes = decodeBase64(source.bytes);
    if (!SHA256_PATTERN.test(source.sha256) || sha256(bytes) !== source.sha256) throw new Error(`source digest mismatch: ${source.logical_path}`);
  }
  if (manifest.sources.some((item) => item.logical_path === "generated_block_bytes")) throw new Error("generated synthesis bytes must not be caller supplied");
  if (critiqueStage && normativeDigestFromSources(manifest) !== manifest.critique_context!.source_digest) throw new Error("critique normative digest mismatch");
  const digest = manifestDigest(manifest);
  if (manifest.manifest_sha256 && manifest.manifest_sha256 !== digest) throw new Error("manifest digest mismatch");
  return { ...manifest, manifest_sha256: digest };
}

export function buildPacket(manifest: RunManifest, packet: Buffer): string {
  if (sha256(packet) !== manifest.packet_sha256) throw new Error("packet digest mismatch");
  const packetText = packet.toString("utf8");
  if (!Buffer.from(packetText, "utf8").equals(packet)) throw new Error("packet must be canonical UTF-8");
  return [
    `<design-gate manifest_nonce="${manifest.nonce}" manifest_sha256="${manifest.manifest_sha256 ?? manifestDigest(manifest)}" packet_sha256="${manifest.packet_sha256}" />`,
    `<design-stage assignment="${manifest.stage}" />`,
    `<design-packet encoding="base64" byte_length="${packet.length}">${packet.toString("base64")}</design-packet>`,
    `<design-packet-content encoding="utf8-json">${JSON.stringify(packetText)}</design-packet-content>`,
  ].join("\n");
}

export function parsePacketText(text: string): {
  nonce: string;
  manifestSha256: string;
  packetSha256: string;
  packet: Buffer;
  stage: DesignStage;
} {
  const marker = /<design-gate manifest_nonce="([^"]+)" manifest_sha256="([a-f0-9]{64})" packet_sha256="([a-f0-9]{64})" \/>/.exec(text);
  const stageMatch = /<design-stage assignment="(proposal|design-specs|tasks|critique-a|critique-b|critique-synthesis)" \/>/.exec(text);
  const packetMatch = /<design-packet encoding="base64" byte_length="(\d+)">([A-Za-z0-9+/=]+)<\/design-packet>/.exec(text);
  const contentMatch = /<design-packet-content encoding="utf8-json">([\s\S]+?)<\/design-packet-content>/.exec(text);
  if (!marker || !stageMatch || !packetMatch || !contentMatch) throw new Error("guard marker, stage assignment, or complete packet missing");
  const packet = decodeBase64(packetMatch[2]);
  if (packet.length !== Number(packetMatch[1])) throw new Error("packet length mismatch");
  if (sha256(packet) !== marker[3]) throw new Error("packet hash mismatch");
  const accessible = Buffer.from(JSON.parse(contentMatch[1]), "utf8");
  if (!accessible.equals(packet)) throw new Error("accessible packet content mismatch");
  const parsed = { nonce: marker[1], manifestSha256: marker[2], packetSha256: marker[3], packet };
  const expected = [
    `<design-gate manifest_nonce="${parsed.nonce}" manifest_sha256="${parsed.manifestSha256}" packet_sha256="${parsed.packetSha256}" />`,
    `<design-stage assignment="${stageMatch[1]}" />`,
    `<design-packet encoding="base64" byte_length="${packet.length}">${packet.toString("base64")}</design-packet>`,
    `<design-packet-content encoding="utf8-json">${JSON.stringify(packet.toString("utf8"))}</design-packet-content>`,
  ].join("\n");
  if (text !== expected) throw new Error("input message is not the exact sealed packet envelope");
  return { ...parsed, stage: stageMatch[1] as DesignStage };
}

export function applySafePatch(
  original: Buffer,
  replacements: Array<{ start: number; end: number; expected_sha256: string; replacement_base64: string }>,
): Buffer {
  if (replacements.length === 0) throw new Error("safe patch must contain at least one effective replacement");
  let cursor = 0;
  const output: Buffer[] = [];
  for (const replacement of replacements) {
    if (!Number.isInteger(replacement.start) || !Number.isInteger(replacement.end)) throw new Error("patch offsets must be integers");
    if (replacement.start < cursor || replacement.end < replacement.start || replacement.end > original.length) {
      throw new Error("patch ranges must be ordered, non-overlapping, and in bounds");
    }
    const current = original.subarray(replacement.start, replacement.end);
    if (sha256(current) !== replacement.expected_sha256) throw new Error("patch source digest mismatch");
    output.push(original.subarray(cursor, replacement.start));
    output.push(decodeBase64(replacement.replacement_base64));
    cursor = replacement.end;
  }
  output.push(original.subarray(cursor));
  const patched = Buffer.concat(output);
  if (patched.equals(original)) throw new Error("safe patch must change artifact bytes");
  return patched;
}

export function normativeDigestFromSources(manifest: RunManifest): string {
  const prefix = `openspec/changes/${manifest.change_id}/`;
  const entries = manifest.sources.map((source) => ({
    logicalPath: source.logical_path.startsWith(prefix) ? source.logical_path.slice(prefix.length) : source.logical_path,
    bytes: decodeBase64(source.bytes),
  }));
  const exactlyOne = (logicalPath: string): Buffer => {
    const matches = entries.filter((entry) => entry.logicalPath === logicalPath);
    if (matches.length !== 1) throw new Error(`critique source must contain exactly one ${logicalPath}`);
    return matches[0].bytes;
  };
  const specs = entries.filter((entry) => entry.logicalPath.startsWith("specs/") && entry.logicalPath.endsWith("/spec.md"));
  if (specs.length === 0) throw new Error("critique sources require at least one spec");
  return normativeDigest({
    proposal: exactlyOne("proposal.md"),
    design: exactlyOne("design.md"),
    specs: specs.map((entry) => ({ path: entry.logicalPath, bytes: entry.bytes })),
    tasks: exactlyOne("tasks.md"),
  });
}

export function buildCritiquePacket(manifest: RunManifest): Buffer {
  if (!CRITIC_STAGES.has(manifest.stage) || !manifest.critique_context) throw new Error("critique packet requires a critic manifest");
  const prefix = `openspec/changes/${manifest.change_id}/`;
  const normative = manifest.sources.filter((source) => {
    const logicalPath = source.logical_path.startsWith(prefix) ? source.logical_path.slice(prefix.length) : source.logical_path;
    return logicalPath === "proposal.md" || logicalPath === "design.md" || logicalPath === "tasks.md" ||
      (logicalPath.startsWith("specs/") && logicalPath.endsWith("/spec.md"));
  }).sort((left, right) => left.logical_path.localeCompare(right.logical_path));
  return Buffer.from(canonicalJson({
    schema: "design-critique-packet.v1",
    change_id: manifest.change_id,
    card_id: manifest.card_id,
    critique_context: manifest.critique_context,
    normative_sources: normative,
  }), "utf8");
}

export function normativeDigest(input: {
  proposal: Buffer;
  design: Buffer;
  specs: Array<{ path: string; bytes: Buffer }>;
  tasks: Buffer;
}): string {
  const designText = input.design.toString("utf8");
  if (!Buffer.from(designText, "utf8").equals(input.design)) throw new Error("design must be canonical UTF-8");
  const begin = designText.indexOf(GENERATED_BEGIN);
  const end = designText.indexOf(GENERATED_END);
  if (begin < 0 || end < begin) throw new Error("generated critique markers are required");
  if (designText.indexOf(GENERATED_BEGIN, begin + GENERATED_BEGIN.length) >= 0 || designText.indexOf(GENERATED_END, end + GENERATED_END.length) >= 0) {
    throw new Error("generated critique markers must be unique");
  }
  const normalizedDesign = `${designText.slice(0, begin)}${GENERATED_BEGIN}\n<GENERATED_EVIDENCE>\n${GENERATED_END}${designText.slice(end + GENERATED_END.length)}`;
  const chunks: Buffer[] = [];
  const append = (logicalPath: string, bytes: Buffer) => {
    chunks.push(Buffer.from(`${logicalPath}\0${bytes.length}\0`, "utf8"), bytes, Buffer.from("\0"));
  };
  append("proposal.md", input.proposal);
  append("design.md", Buffer.from(normalizedDesign));
  for (const spec of [...input.specs].sort((a, b) => a.path.localeCompare(b.path))) append(spec.path, spec.bytes);
  append("tasks.md", input.tasks);
  return sha256(Buffer.concat(chunks));
}

export function parseAssessment(text: string): Assessment {
  const parsed = JSON.parse(text) as Assessment;
  const envelopeKeys = ["assessment", "findings", "lineage_id", "resolutions", "round", "schema", "source_digest"];
  if (!parsed || Object.keys(parsed).sort().join("\0") !== envelopeKeys.join("\0")) throw new Error("invalid assessment envelope fields");
  if (text !== canonicalJson(parsed)) throw new Error("assessment JSON is not canonical");
  if (parsed.schema !== "design-critique-assessment.v1" || !["A", "B"].includes(parsed.assessment)) throw new Error("invalid assessment identity");
  if (!SAFE_ID_PATTERN.test(parsed.lineage_id) || !SHA256_PATTERN.test(parsed.source_digest) || !Number.isInteger(parsed.round) || parsed.round < 0) {
    throw new Error("invalid assessment envelope");
  }
  if (!Array.isArray(parsed.findings) || !Array.isArray(parsed.resolutions)) throw new Error("invalid assessment collections");
  const findingIds = new Set<string>();
  for (const finding of parsed.findings) {
    const keys = ["disposition_required", "finding_id", "severity", "source_digest", "summary"];
    if (!finding || Object.keys(finding).sort().join("\0") !== keys.join("\0")) throw new Error("invalid finding fields");
    if (!SAFE_ID_PATTERN.test(finding.finding_id) || findingIds.has(finding.finding_id) || !finding.summary || typeof finding.disposition_required !== "boolean") {
      throw new Error("duplicate or invalid finding ID");
    }
    if (!["P0", "P1", "P2"].includes(finding.severity) || finding.source_digest !== parsed.source_digest || !SHA256_PATTERN.test(finding.source_digest)) {
      throw new Error("invalid finding");
    }
    findingIds.add(finding.finding_id);
  }
  const resolutionIds = new Set<string>();
  for (const resolution of parsed.resolutions) {
    const keys = ["disposition", "finding_id", "prior_source_digest", "rationale", "source_digest"];
    if (!resolution || Object.keys(resolution).sort().join("\0") !== keys.join("\0")) throw new Error("invalid resolution fields");
    if (!SAFE_ID_PATTERN.test(resolution.finding_id) || resolutionIds.has(resolution.finding_id) || !resolution.rationale) {
      throw new Error("duplicate or invalid resolution ID");
    }
    if (!["resolved", "open"].includes(resolution.disposition) || !SHA256_PATTERN.test(resolution.prior_source_digest) || resolution.source_digest !== parsed.source_digest) {
      throw new Error("invalid resolution");
    }
    resolutionIds.add(resolution.finding_id);
  }
  return parsed;
}

export function mergeAssessments(input: {
  assessmentA: Assessment;
  assessmentB: Assessment;
  inheritedBlockingIds: string[];
}): { verdict: "PASS" | "BLOCKED"; openBlockingIds: string[]; findings: Finding[] } {
  const { assessmentA: a, assessmentB: b } = input;
  if (a.assessment !== "A" || b.assessment !== "B") throw new Error("assessment identity mismatch");
  if (a.lineage_id !== b.lineage_id || a.round !== b.round || a.source_digest !== b.source_digest) {
    throw new Error("assessment lineage mismatch");
  }
  const resolutions = (assessment: Assessment) => new Map(assessment.resolutions.map((item) => [item.finding_id, item]));
  const aResolutions = resolutions(a);
  const bResolutions = resolutions(b);
  const inherited = new Set(input.inheritedBlockingIds);
  if ([...aResolutions.keys(), ...bResolutions.keys()].some((id) => !inherited.has(id))) throw new Error("assessment resolved an unknown finding");
  const open = new Set<string>();
  for (const id of input.inheritedBlockingIds) {
    const aResolution = aResolutions.get(id);
    const bResolution = bResolutions.get(id);
    if (aResolution?.disposition !== "resolved" || bResolution?.disposition !== "resolved" ||
        aResolution.prior_source_digest !== bResolution.prior_source_digest ||
        aResolution.prior_source_digest === a.source_digest) open.add(id);
  }
  const findings = [...a.findings, ...b.findings];
  if (new Set(findings.map((item) => item.finding_id)).size !== findings.length) throw new Error("duplicate finding ID across assessments");
  for (const finding of findings) if (finding.severity === "P0" || finding.severity === "P1") open.add(finding.finding_id);
  return { verdict: open.size === 0 ? "PASS" : "BLOCKED", openBlockingIds: [...open].sort(), findings };
}
