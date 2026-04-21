import assert from "node:assert/strict";
import test from "node:test";

import { renderDebateTranscriptMarkdown } from "../format.js";
import type { DebateTranscript } from "../types.js";

test("renderDebateTranscriptMarkdown formats rounds and findings", () => {
  const transcript: DebateTranscript = {
    agents: [{ name: "security", mandate: "Review security." }],
    rounds: [
      [
        {
          id: "r1",
          agent: "security",
          severity: "blocking",
          file: "src/app.ts",
          line: 12,
          claim: "Unsafe string concatenation in query building.",
          confidence: 0.92,
        },
      ],
      [],
    ],
  };

  const markdown = renderDebateTranscriptMarkdown(transcript);

  assert.match(markdown, /### Debate Transcript/);
  assert.match(markdown, /#### Round 1/);
  assert.match(markdown, /\[BLOCKING\].*src\/app\.ts:12/);
  assert.match(markdown, /#### Round 2/);
  assert.match(markdown, /No findings in this round\./);
});