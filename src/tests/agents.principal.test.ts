import assert from "node:assert/strict";
import test from "node:test";

import { synthesizePrincipalSummary } from "../agents/principal.js";
import type { DebateTranscript } from "../types.js";

test("synthesizePrincipalSummary returns validated principal summary", async (t) => {
  const originalFetch = globalThis.fetch;
  t.after(() => {
    globalThis.fetch = originalFetch;
  });

  const finding = {
    id: "review-security-1",
    agent: "security",
    severity: "blocking",
    file: "src/auth.ts",
    line: 17,
    claim: "User input is not escaped before query composition.",
    confidence: 0.94,
  } as const;

  globalThis.fetch = (async () =>
    new Response(
      JSON.stringify({
        content: [
          {
            type: "text",
            text: JSON.stringify({
              agreements: [finding],
              disputes: [],
              final_calls: [{ finding, decision: "Blocking until query is parameterized." }],
              summary: "## swarm-review\n\nPrincipal summary.",
            }),
          },
        ],
      }),
      { status: 200 }
    )) as typeof fetch;

  const transcript: DebateTranscript = {
    agents: [{ name: "security", mandate: "Find security risks." }],
    rounds: [[finding]],
  };

  const summary = await synthesizePrincipalSummary({
    principal: {
      mandate: "Make final calls.",
    },
    transcript,
    providerConfig: { type: "anthropic", config: { apiKey: "test-key", model: "test-model" } },
  });

  assert.equal(summary.agreements.length, 1);
  assert.equal(summary.final_calls.length, 1);
  assert.match(summary.summary, /swarm-review/);
});
