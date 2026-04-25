import { callLLMStructured } from "../llm.js";
import { buildPrincipalPrompt } from "../prompts.js";
import { PrincipalSummarySchema, type DebateTranscript, type PrincipalConfig, type PrincipalSummary, type ProviderConfig } from "../types.js";

export type PrincipalRoundInput = {
  principal: PrincipalConfig;
  transcript: DebateTranscript;
  providerConfig: ProviderConfig;
};

export async function synthesizePrincipalSummary(input: PrincipalRoundInput): Promise<PrincipalSummary> {
  return callLLMStructured(
    input.providerConfig,
    input.principal.mandate,
    buildPrincipalPrompt(input.principal, input.transcript),
    PrincipalSummarySchema
  );
}