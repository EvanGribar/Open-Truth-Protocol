# swarm-review

swarm-review is a GitHub Action that turns one pull request into a multi-agent review session.

Each configured agent reads the diff independently, flags issues, and then enters a structured debate with the rest of the swarm. A principal agent reads the full transcript and posts the final PR comment, so the output looks like a real engineering review instead of a single flat model response.

## Why it exists

Most AI review tools give you one opinion. swarm-review gives you a review process.

- Different agents can specialize in security, performance, architecture, or whatever your team needs.
- Agents can challenge each other before the final comment is posted.
- Teams can choose whether to show only the final outcome or the full debate transcript.

## How it works

1. The action fetches the pull request diff from GitHub.
2. Every agent performs an independent first-pass review in parallel.
3. The agents debate each other for the configured number of rounds.
4. The principal agent synthesizes the transcript into a final summary.
5. The action updates the PR comment and, optionally, the check run.

## Quick Start

Add this workflow to your repository:

```yaml
name: swarm-review

on:
  pull_request:
    types: [opened, synchronize, reopened]

permissions:
  contents: read
  pull-requests: write
  checks: write

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Run swarm-review
        uses: ./
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          anthropic-api-key: ${{ secrets.ANTHROPIC_API_KEY }}
          anthropic-model: claude-3-5-sonnet-latest
          config-path: .swarm.yml
```

Then add a `.swarm.yml` file at the repository root if you want to customize the swarm.

## Configuration

If `.swarm.yml` is missing, the action uses the default config bundled with this repository.

```yaml
agents:
  - name: security
    mandate: >
      Review for security vulnerabilities. Look for injection risks, exposed secrets,
      broken auth, insecure defaults, and unsafe data handling.

  - name: performance
    mandate: >
      Review for performance issues. Look for N+1 queries, unnecessary re-renders,
      expensive operations in hot paths, and missing pagination.

  - name: architecture
    mandate: >
      Review for architectural concerns. Look for separation of concerns violations,
      tight coupling, naming inconsistency, and patterns that do not fit the codebase.

  - name: dx
    mandate: >
      Review for developer experience. Look for missing tests, outdated docs,
      unclear variable names, and changes that will be hard to maintain.

debate:
  rounds: 2
  min_confidence: 0.6

principal:
  mandate: >
    You are the principal engineer. Read the full debate and make final calls.
    Be direct. Show your reasoning. Surface genuine disagreements clearly.

output:
  mode: outcome
```

### Output modes

- `outcome`: posts only the principal summary.
- `full`: posts the principal summary plus the full round-by-round transcript.

### Config fields

- `agents`: list of reviewer agents, each with a `name`, `mandate`, and optional `model`.
- `debate.rounds`: how many debate rounds to run after the first-pass review.
- `debate.min_confidence`: findings below this threshold are filtered out.
- `principal.mandate`: instructions for the synthesis agent.
- `output.mode`: controls whether the transcript is included in the PR comment.

## Action Inputs

- `github-token`: GitHub token with permission to comment on pull requests.
- `anthropic-api-key`: Anthropic or compatible API key.
- `anthropic-model`: optional model override for all agents.
- `config-path`: optional path to the swarm config file.
- `check-run-id`: optional existing check run ID to update after the review.

## Example Result

The final comment is designed to read like a human review thread:

```text
## swarm-review

security flagged src/api/users.ts:47 — raw user input is passed into a query string.
performance disagreed — the path is currently low traffic but still has avoidable overhead.
principal: the security concern is valid. Use a parameterized query.
```

## Local Development

```bash
npm install
npm run build
npm test
```

## Release Process

v0.0.2 is delivered in four stage-specific pull requests so each risk domain is reviewed independently:

1. Stability and safety hardening.
2. Diff scaling and runtime reliability.
3. Coverage expansion for key helpers.
4. Documentation and release metadata.

This keeps reviews focused and makes rollback decisions straightforward.

## Project Layout

- `src/types.ts`: shared schemas and data contracts.
- `src/config.ts`: config loading and validation.
- `src/diff.ts`: pull request diff fetching and formatting.
- `src/prompts.ts`: all LLM prompt templates.
- `src/agents/`: review, debate, and synthesis rounds.
- `src/index.ts`: action entrypoint.

## Notes

The implementation is intentionally small and explicit. The system is built around a strict data contract so agent output can be validated before it is passed to the next stage.