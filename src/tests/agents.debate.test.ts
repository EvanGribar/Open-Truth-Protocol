import assert from "node:assert/strict";
import test from "node:test";

import { runDebateRounds } from "../agents/debate.js";
import type { AgentConfig, FileDiff, Finding } from "../types.js";

test("runDebateRounds appends each debate round to transcript", async (t) => {
  const originalFetch = globalThis.fetch;
  t.after(() => {
    globalThis.fetch = originalFetch;
  });

  const responses = [
    [
      {
        agent: "security",
        severity: "warning",
        file: "src/app.ts",
        line: 6,
        claim: "Input validation should be centralized.",
        confidence: 0.88,
        rebuttal_to: "review-security-1",
      },
    ],
    [],
  ];

  globalThis.fetch = (async () => {
    const payload = responses.shift() ?? [];
    return new Response(
      JSON.stringify({ content: [{ type: "text", text: JSON.stringify(payload) }] }),
      { status: 200 }
    );
  }) as typeof fetch;

  const agents: AgentConfig[] = [{ name: "security", mandate: "Focus on security." }];
  const diff: FileDiff[] = [
    {
      path: "src/app.ts",
      status: "modified",
      additions: 8,
      deletions: 3,
      changes: 11,
      patch: "@@ -1,1 +1,2 @@",
    },
  ];
  const initialFindings: Finding[] = [
    {
      id: "review-security-1",
      agent: "security",
      severity: "blocking",
      file: "src/app.ts",
      line: 4,
      claim: "User input reaches SQL layer unsafely.",
      confidence: 0.93,
    },
  ];

  const transcript = await runDebateRounds({
    agents,
    diff,
    initialFindings,
    rounds: 2,
    apiKey: "test-key",
    model: "global-model",
    minConfidence: 0.6,
  });

  assert.equal(transcript.rounds.length, 3);
  assert.equal(transcript.rounds[0]?.length, 1);
  assert.equal(transcript.rounds[1]?.length, 1);
  assert.equal(transcript.rounds[2]?.length, 0);
  assert.equal(transcript.rounds[1]?.[0]?.id, "debate-1-security-1");
});
