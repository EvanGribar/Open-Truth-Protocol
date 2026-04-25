import { DEFAULT_ANTHROPIC_MODEL, DEFAULT_API_ENDPOINT } from "../llm.js";
import { buildReviewPrompt } from "../prompts.js";
import type { AgentConfig, FileDiff, Finding, DiffConfig } from "../types.js";
import { runAgentFindingRound } from "./shared.js";

export type ReviewRoundInput = {
  agents: AgentConfig[];
  diff: FileDiff[];
  apiKey: string;
  model?: string;
  minConfidence: number;
  apiEndpoint?: string;
  diffConfig?: DiffConfig;
};

export async function runReviewRound(input: ReviewRoundInput): Promise<Finding[]> {
  const system =
    "You are an independent reviewer in the first round of a pull request review swarm. Return only JSON and focus on real, reviewable issues.";

  const findings = await Promise.all(
    input.agents.map((agent) =>
      runAgentFindingRound({
        apiKey: input.apiKey,
        model: agent.model ?? input.model ?? DEFAULT_ANTHROPIC_MODEL,
        system,
        prompt: buildReviewPrompt(agent, input.diff, input.diffConfig),
        agentName: agent.name,
        idPrefix: `review-${agent.name}`,
        minConfidence: input.minConfidence,
        apiEndpoint: input.apiEndpoint ?? DEFAULT_API_ENDPOINT,
      })
    )
  );

  return findings.flat();
}