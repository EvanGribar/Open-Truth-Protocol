## Summary
Describe what changed and why. Link related issue(s): `Closes #...`.

## Change Type
- [ ] Feature
- [ ] Bugfix
- [ ] Refactor
- [ ] Chore
- [ ] Documentation

## Scope
- [ ] Orchestrator
- [ ] Provenance
- [ ] Heuristics
- [ ] Web Consensus
- [ ] Shared
- [ ] Infra/CI
- [ ] Docs

## AGENTS.md Contract Compliance
- [ ] I updated AGENTS.md when changing contracts, schema, scoring, or verdict behavior.
- [ ] I preserved backward compatibility or documented breaking behavior.
- [ ] I added tests for behavioral changes.

## Quality Gate
- [ ] `uv run ruff check .`
- [ ] `uv run ruff format --check .`
- [ ] `uv run mypy .`
- [ ] `uv run pytest`

## Benchmark Evidence (required for scoring/model logic changes)
If this PR changes scoring or detector logic, include benchmark output from `/eval/benchmark.py`.

```text
Paste benchmark output here.
```

## Security and Secrets
- [ ] No secrets committed.
- [ ] New env vars are documented in AGENTS.md and README where relevant.

## Documentation
- [ ] Updated README/CONTRIBUTING/CHANGELOG as needed.

## Reviewer Checklist
- [ ] Contract changes reviewed.
- [ ] Tests are meaningful and pass.
- [ ] Scope matches linked issue.
