import { z } from "zod";

import { callAnthropicStructured, DEFAULT_ANTHROPIC_MODEL, DEFAULT_API_ENDPOINT, normalizeFinding } from "../llm.js";
import { RawFindingSchema, type Finding, type RawFinding } from "../types.js";

const RawFindingArraySchema = z.array(RawFindingSchema);

export type AgentRoundOptions = {
  apiKey: string;
  model: string;
  system: string;
  prompt: string;
  agentName: string;
  idPrefix: string;
  minConfidence: number;
  apiEndpoint?: string;
};

export async function runAgentFindingRound(options: AgentRoundOptions): Promise<Finding[]> {
  const rawFindings = await callAnthropicStructured<RawFinding[]>(
    options.apiKey,
    options.model || DEFAULT_ANTHROPIC_MODEL,
    options.system,
    options.prompt,
    RawFindingArraySchema,
    options.apiEndpoint || DEFAULT_API_ENDPOINT
  );

  return rawFindings
    .map((finding, index) => normalizeFinding(finding, options.agentName, `${options.idPrefix}-${index + 1}`))
    .filter((finding) => finding.confidence >= options.minConfidence);
}