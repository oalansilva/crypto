import { GENERATED_BEGIN, GENERATED_END, canonicalJson, mergeAssessments, parseAssessment, sha256, type Assessment } from "./contract.js";

export function synthesizeAssessments(input: {
  assessmentABytes: Buffer;
  assessmentBBytes: Buffer;
  inheritedBlockingIds: string[];
}): {
  assessmentA: Assessment;
  assessmentB: Assessment;
  verdict: "PASS" | "BLOCKED";
  generatedBlockBytes: Buffer;
  digest: string;
} {
  const assessmentA = parseAssessment(input.assessmentABytes.toString("utf8"));
  const assessmentB = parseAssessment(input.assessmentBBytes.toString("utf8"));
  const merged = mergeAssessments({ assessmentA, assessmentB, inheritedBlockingIds: input.inheritedBlockingIds });
  const generated = {
    schema: "design-critique-synthesis.v1",
    lineage_id: assessmentA.lineage_id,
    round: assessmentA.round,
    source_digest: assessmentA.source_digest,
    assessment_a: { sha256: sha256(input.assessmentABytes), payload_base64: input.assessmentABytes.toString("base64") },
    assessment_b: { sha256: sha256(input.assessmentBBytes), payload_base64: input.assessmentBBytes.toString("base64") },
    inherited_blocking_ids: [...input.inheritedBlockingIds].sort(),
    open_blocking_ids: merged.openBlockingIds,
    findings: merged.findings,
    verdict: merged.verdict,
  };
  const generatedBlockBytes = Buffer.from(`${canonicalJson(generated)}\n`);
  return {
    assessmentA,
    assessmentB,
    verdict: merged.verdict,
    generatedBlockBytes,
    digest: sha256(generatedBlockBytes),
  };
}

export function insertGeneratedBlock(design: Buffer, generatedBlockBytes: Buffer): Buffer {
  const text = design.toString("utf8");
  if (!Buffer.from(text, "utf8").equals(design)) throw new Error("design must be canonical UTF-8");
  const begin = text.indexOf(GENERATED_BEGIN);
  const end = text.indexOf(GENERATED_END);
  if (begin < 0 || end < begin || text.indexOf(GENERATED_BEGIN, begin + GENERATED_BEGIN.length) >= 0 || text.indexOf(GENERATED_END, end + GENERATED_END.length) >= 0) {
    throw new Error("generated critique markers must exist exactly once");
  }
  const replacementStart = begin + GENERATED_BEGIN.length;
  return Buffer.from(`${text.slice(0, replacementStart)}\n${generatedBlockBytes.toString("utf8")}${text.slice(end)}`, "utf8");
}

export function assertGeneratedBlock(design: Buffer, expected: Buffer): void {
  const text = design.toString("utf8");
  const begin = text.indexOf(GENERATED_BEGIN);
  const end = text.indexOf(GENERATED_END);
  if (begin < 0 || end < begin) throw new Error("generated critique markers are required");
  const actual = Buffer.from(text.slice(begin + GENERATED_BEGIN.length + 1, end), "utf8");
  if (!actual.equals(expected)) throw new Error("generated critique block differs from deterministic bytes");
}
