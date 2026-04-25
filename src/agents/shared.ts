import { z } from "zod";

import { callLLMStructured, DEFAULT_ANTHROPIC_MODEL, normalizeFinding } from "../llm.js";
import { RawFindingSchema, type Finding, type RawFinding, type ProviderConfig } from "../types.js";

const RawFindingArraySchema = z.array(RawFindingSchema);

export type AgentRoundOptions = {
  providerConfig: ProviderConfig;
  system: string;
  prompt: string;
  agentName: string;
  idPrefix: string;
  minConfidence: number;
};

export async function runAgentFindingRound(options: AgentRoundOptions): Promise<Finding[]> {
  const rawFindings = await callLLMStructured<RawFinding[]>(
    options.providerConfig,
    options.system,
    options.prompt,
    RawFindingArraySchema
  );

  return rawFindings
    .map((finding, index) => normalizeFinding(finding, options.agentName, `${options.idPrefix}-${index + 1}`))
    .filter((finding) => finding.confidence >= options.minConfidence);
}