import assert from "node:assert/strict";
import test from "node:test";

import { callAnthropic, extractJsonText } from "../llm.js";

test("extractJsonText accepts fenced JSON", () => {
  const extracted = extractJsonText("```json\n[{\"id\":\"1\"}]\n```");

  assert.equal(extracted, "[{\"id\":\"1\"}]");
});

test("extractJsonText extracts embedded JSON from surrounding text", () => {
  const extracted = extractJsonText("Here is the payload: {\"ok\":true}");

  assert.equal(extracted, "{\"ok\":true}");
});

test("callAnthropic retries once on retryable status and then succeeds", async (t) => {
  const originalFetch = globalThis.fetch;
  t.after(() => {
    globalThis.fetch = originalFetch;
  });

  let attempts = 0;
  globalThis.fetch = (async () => {
    attempts += 1;
    if (attempts === 1) {
      return new Response("retry", { status: 500 });
    }

    return new Response(
      JSON.stringify({
        content: [{ type: "text", text: "[]" }],
      }),
      { status: 200 }
    );
  }) as typeof fetch;

  const response = await callAnthropic("test-key", "test-model", "system", "prompt");

  assert.equal(response, "[]");
  assert.equal(attempts, 2);
});

test("callAnthropic throws on non-retryable status", async (t) => {
  const originalFetch = globalThis.fetch;
  t.after(() => {
    globalThis.fetch = originalFetch;
  });

  globalThis.fetch = (async () => new Response("bad request", { status: 400 })) as typeof fetch;

  await assert.rejects(
    () => callAnthropic("test-key", "test-model", "system", "prompt"),
    /Anthropic request failed with 400/
  );
});