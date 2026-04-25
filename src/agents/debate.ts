import { DEFAULT_ANTHROPIC_MODEL, DEFAULT_API_ENDPOINT } from "../llm.js";
import { buildDebatePrompt } from "../prompts.js";
import type { AgentConfig, DebateTranscript, FileDiff, Finding, DiffConfig } from "../types.js";
import { runAgentFindingRound } from "./shared.js";

export type DebateRoundInput = {
  agents: AgentConfig[];
  diff: FileDiff[];
  initialFindings: Finding[];
  rounds: number;
  apiKey: string;
  model?: string;
  minConfidence: number;
  apiEndpoint?: string;
  diffConfig?: DiffConfig;
};

export async function runDebateRounds(input: DebateRoundInput): Promise<DebateTranscript> {
  const transcript: DebateTranscript = {
    rounds: [input.initialFindings],
    agents: input.agents,
  };

  const system =
    "You are a reviewer in the debate phase of a pull request review swarm. Respond to the transcript, challenge weak claims, and add new findings only when justified. Return only JSON.";

  for (let debateRound = 1; debateRound <= input.rounds; debateRound += 1) {
    const currentTranscript: DebateTranscript = {
      rounds: transcript.rounds,
      agents: transcript.agents,
    };

    const roundFindings = await Promise.all(
      input.agents.map((agent) =>
        runAgentFindingRound({
          apiKey: input.apiKey,
          model: agent.model ?? input.model ?? DEFAULT_ANTHROPIC_MODEL,
          system,
          prompt: buildDebatePrompt(agent, input.diff, currentTranscript, debateRound, input.diffConfig),
          agentName: agent.name,
          idPrefix: `debate-${debateRound}-${agent.name}`,
          minConfidence: input.minConfidence,
          apiEndpoint: input.apiEndpoint ?? DEFAULT_API_ENDPOINT,
        })
      )
    );

    transcript.rounds.push(roundFindings.flat());
  }

  return transcript;
}