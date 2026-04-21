import { existsSync } from "node:fs";
import { readFile } from "node:fs/promises";

import { createOctokit, fetchPullRequestDiff } from "./diff.js";
import { loadSwarmConfig } from "./config.js";
import { runDebateRounds } from "./agents/debate.js";
import { runReviewRound } from "./agents/review.js";
import { synthesizePrincipalSummary } from "./agents/principal.js";
import { upsertPullRequestComment, updateCheckRun } from "./github.js";
import { DEFAULT_ANTHROPIC_MODEL } from "./llm.js";
import { renderDebateTranscriptMarkdown } from "./format.js";

function readInput(name: string): string | undefined {
  const candidates = [
    `INPUT_${name.toUpperCase()}`,
    `INPUT_${name.replace(/-/g, "_").toUpperCase()}`,
    name.toUpperCase(),
    name.replace(/-/g, "_").toUpperCase(),
  ];

  for (const candidate of candidates) {
    const value = process.env[candidate]?.trim();
    if (value && value.length > 0) {
      return value;
    }
  }

  return undefined;
}

function resolveRepository(): { owner: string; repo: string } {
  const repository = process.env.GITHUB_REPOSITORY;
  if (!repository) {
    throw new Error("GITHUB_REPOSITORY is required.");
  }

  const [owner, repo] = repository.split("/");
  if (!owner || !repo) {
    throw new Error(`Invalid GITHUB_REPOSITORY value: ${repository}`);
  }

  return { owner, repo };
}

async function resolvePullRequestNumber(): Promise<number> {
  const eventPath = process.env.GITHUB_EVENT_PATH;
  if (eventPath && existsSync(eventPath)) {
    const eventPayload = JSON.parse(await readFile(eventPath, "utf8")) as {
      pull_request?: { number?: number };
      issue?: { number?: number };
    };

    const pullNumber = eventPayload.pull_request?.number ?? eventPayload.issue?.number;
    if (typeof pullNumber === "number") {
      return pullNumber;
    }
  }

  const fallback = readInput("pull-number") ?? process.env.PULL_NUMBER;
  if (fallback) {
    const parsed = Number(fallback);
    if (Number.isFinite(parsed)) {
      return parsed;
    }
  }

  throw new Error("Unable to resolve the pull request number from the GitHub event payload.");
}

async function main(): Promise<void> {
  const githubToken = readInput("github-token") ?? process.env.GITHUB_TOKEN;
  const anthropicApiKey = readInput("anthropic-api-key") ?? process.env.ANTHROPIC_API_KEY;
  const anthropicModel = readInput("anthropic-model") ?? process.env.ANTHROPIC_MODEL ?? DEFAULT_ANTHROPIC_MODEL;
  const configPath = readInput("config-path") ?? process.env.CONFIG_PATH ?? ".swarm.yml";
  const checkRunId = readInput("check-run-id") ?? process.env.CHECK_RUN_ID;

  if (!githubToken) {
    throw new Error("GitHub token is required.");
  }

  if (!anthropicApiKey) {
    throw new Error("Anthropic API key is required.");
  }

  const workspaceRoot = process.cwd();
  const swarmConfig = await loadSwarmConfig(workspaceRoot, configPath);
  const octokit = createOctokit(githubToken);
  const { owner, repo } = resolveRepository();
  const pullNumber = await resolvePullRequestNumber();

  console.log(`Running swarm-review for ${owner}/${repo}#${pullNumber}`);

  const diff = await fetchPullRequestDiff(octokit, owner, repo, pullNumber);
  const reviewFindings = await runReviewRound({
    agents: swarmConfig.agents,
    diff,
    apiKey: anthropicApiKey,
    model: anthropicModel,
    minConfidence: swarmConfig.debate.min_confidence,
  });

  const transcript = await runDebateRounds({
    agents: swarmConfig.agents,
    diff,
    initialFindings: reviewFindings,
    rounds: swarmConfig.debate.rounds,
    apiKey: anthropicApiKey,
    model: anthropicModel,
    minConfidence: swarmConfig.debate.min_confidence,
  });

  const summary = await synthesizePrincipalSummary({
    principal: swarmConfig.principal,
    transcript,
    apiKey: anthropicApiKey,
    model: anthropicModel,
  });

  const headlineSummary = summary.summary.startsWith("## swarm-review")
    ? summary.summary
    : `## swarm-review\n\n${summary.summary}`;

  const commentBody =
    swarmConfig.output.mode === "full"
      ? `${headlineSummary}${renderDebateTranscriptMarkdown(transcript)}`
      : headlineSummary;

  await upsertPullRequestComment(octokit, owner, repo, pullNumber, commentBody);
  await updateCheckRun(octokit, owner, repo, checkRunId, commentBody);

  console.log("swarm-review completed successfully.");
}

void main().catch((error: unknown) => {
  console.error(error);
  process.exitCode = 1;
});