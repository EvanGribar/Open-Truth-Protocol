import assert from "node:assert/strict";
import test from "node:test";

import { runAgentFindingRound } from "../agents/shared.js";

test("runAgentFindingRound normalizes findings and filters by confidence", async (t) => {
  const originalFetch = globalThis.fetch;
  t.after(() => {
    globalThis.fetch = originalFetch;
  });

  globalThis.fetch = (async () =>
    new Response(
      JSON.stringify({
        content: [
          {
            type: "text",
            text: JSON.stringify([
              {
                agent: "   ",
                severity: "warning",
                file: "src/auth.ts",
                line: 8,
                claim: "Token parsing should validate issuer.",
                confidence: 0.8,
              },
              {
                agent: "security",
                severity: "suggestion",
                file: "src/auth.ts",
                line: 19,
                claim: "Consider centralizing token expiry handling.",
                confidence: 0.2,
              },
            ]),
          },
        ],
      }),
      { status: 200 }
    )) as typeof fetch;

  const findings = await runAgentFindingRound({
    apiKey: "test-key",
    model: "test-model",
    system: "test-system",
    prompt: "test-prompt",
    agentName: "fallback-agent",
    idPrefix: "review-fallback",
    minConfidence: 0.5,
  });

  assert.equal(findings.length, 1);
  assert.equal(findings[0]?.id, "review-fallback-1");
  assert.equal(findings[0]?.agent, "fallback-agent");
});
