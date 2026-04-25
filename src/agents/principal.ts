import { DEFAULT_ANTHROPIC_MODEL, DEFAULT_API_ENDPOINT, callAnthropicStructured } from "../llm.js";
import { buildPrincipalPrompt } from "../prompts.js";
import { PrincipalSummarySchema, type DebateTranscript, type PrincipalConfig, type PrincipalSummary } from "../types.js";

export type PrincipalRoundInput = {
  principal: PrincipalConfig;
  transcript: DebateTranscript;
  apiKey: string;
  model?: string;
  apiEndpoint?: string;
};

export async function synthesizePrincipalSummary(input: PrincipalRoundInput): Promise<PrincipalSummary> {
  return callAnthropicStructured(
    input.apiKey,
    input.model ?? DEFAULT_ANTHROPIC_MODEL,
    input.principal.mandate,
    buildPrincipalPrompt(input.principal, input.transcript),
    PrincipalSummarySchema,
    input.apiEndpoint ?? DEFAULT_API_ENDPOINT
  );
}