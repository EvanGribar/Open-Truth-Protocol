import assert from "node:assert/strict";
import test from "node:test";

import { runReviewRound } from "../agents/review.js";
import type { AgentConfig, FileDiff } from "../types.js";

test("runReviewRound fans out to all agents and uses model overrides", async (t) => {
  const originalFetch = globalThis.fetch;
  t.after(() => {
    globalThis.fetch = originalFetch;
  });

  const requestBodies: Array<{ model?: string }> = [];
  const responses = [
    [
      {
        agent: "security",
        severity: "blocking",
        file: "src/db.ts",
        line: 22,
        claim: "Raw input is interpolated in SQL query text.",
        confidence: 0.9,
      },
    ],
    [
      {
        agent: "performance",
        severity: "warning",
        file: "src/api.ts",
        line: 13,
        claim: "Repeated parsing inside loop can be memoized.",
        confidence: 0.82,
      },
    ],
  ];

  globalThis.fetch = (async (_input, init) => {
    requestBodies.push(JSON.parse(String(init?.body ?? "{}")) as { model?: string });
    const payload = responses.shift() ?? [];

    return new Response(
      JSON.stringify({
        content: [{ type: "text", text: JSON.stringify(payload) }],
      }),
      { status: 200 }
    );
  }) as typeof fetch;

  const agents: AgentConfig[] = [
    { name: "security", mandate: "Find security issues." },
    { name: "performance", mandate: "Find performance issues.", model: "agent-model" },
  ];
  const diff: FileDiff[] = [
    {
      path: "src/db.ts",
      status: "modified",
      additions: 4,
      deletions: 1,
      changes: 5,
      patch: "@@ -1,1 +1,1 @@",
    },
  ];

  const findings = await runReviewRound({
    agents,
    diff,
    providerConfig: { type: "anthropic", config: { apiKey: "test-key", model: "global-model" } },
    minConfidence: 0.6,
  });

  assert.equal(findings.length, 2);
  assert.deepEqual(
    requestBodies.map((body) => body.model).sort(),
    ["agent-model", "global-model"].sort()
  );
  assert.match(findings[0]?.id ?? "", /^review-(security|performance)-1$/);
});
