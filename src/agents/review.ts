import { buildReviewPrompt } from "../prompts.js";
import type { AgentConfig, FileDiff, Finding, ProviderConfig, DiffConfig } from "../types.js";
import { runAgentFindingRound } from "./shared.js";

export type ReviewRoundInput = {
  agents: AgentConfig[];
  diff: FileDiff[];
  providerConfig: ProviderConfig;
  minConfidence: number;
  diffConfig?: DiffConfig;
};

export async function runReviewRound(input: ReviewRoundInput): Promise<Finding[]> {
  const system =
    "You are an independent reviewer in the first round of a pull request review swarm. Return only JSON and focus on real, reviewable issues.";

  const findings = await Promise.all(
    input.agents.map((agent) => {
      // Use agent-specific model override if provided
      let providerConfig = input.providerConfig;
      if (agent.model) {
        if (input.providerConfig.type === "anthropic") {
          providerConfig = {
            type: "anthropic",
            config: { ...input.providerConfig.config, model: agent.model },
          };
        } else if (input.providerConfig.type === "openai") {
          providerConfig = {
            type: "openai",
            config: { ...input.providerConfig.config, model: agent.model },
          };
        } else if (input.providerConfig.type === "openrouter") {
          providerConfig = {
            type: "openrouter",
            config: { ...input.providerConfig.config, model: agent.model },
          };
        } else if (input.providerConfig.type === "openclaw") {
          providerConfig = {
            type: "openclaw",
            config: { ...input.providerConfig.config, model: agent.model },
          };
        } else if (input.providerConfig.type === "hermes") {
          providerConfig = {
            type: "hermes",
            config: { ...input.providerConfig.config, model: agent.model },
          };
        } else if (input.providerConfig.type === "groq") {
          providerConfig = {
            type: "groq",
            config: { ...input.providerConfig.config, model: agent.model },
          };
        } else if (input.providerConfig.type === "together") {
          providerConfig = {
            type: "together",
            config: { ...input.providerConfig.config, model: agent.model },
          };
        } else if (input.providerConfig.type === "mistral") {
          providerConfig = {
            type: "mistral",
            config: { ...input.providerConfig.config, model: agent.model },
          };
        } else if (input.providerConfig.type === "cohere") {
          providerConfig = {
            type: "cohere",
            config: { ...input.providerConfig.config, model: agent.model },
          };
        } else if (input.providerConfig.type === "perplexity") {
          providerConfig = {
            type: "perplexity",
            config: { ...input.providerConfig.config, model: agent.model },
          };
        } else if (input.providerConfig.type === "hyperbolic") {
          providerConfig = {
            type: "hyperbolic",
            config: { ...input.providerConfig.config, model: agent.model },
          };
        } else if (input.providerConfig.type === "custom") {
          providerConfig = {
            type: "custom",
            config: { ...input.providerConfig.config, model: agent.model },
          };
        }
      }

      return runAgentFindingRound({
        providerConfig,
        system,
        prompt: buildReviewPrompt(agent, input.diff, input.diffConfig),
        agentName: agent.name,
        idPrefix: `review-${agent.name}`,
        minConfidence: input.minConfidence,
      });
    })
  );

  return findings.flat();
}