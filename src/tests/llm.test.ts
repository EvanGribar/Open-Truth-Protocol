import assert from "node:assert/strict";
import test from "node:test";

import { callAnthropic, callLLM, extractJsonText } from "../llm.js";

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

test("callAnthropic sends requests to the configured apiEndpoint", async (t) => {
  const originalFetch = globalThis.fetch;
  t.after(() => {
    globalThis.fetch = originalFetch;
  });

  let requestedUrl: string | undefined;
  globalThis.fetch = (async (input) => {
    requestedUrl = String(input);
    return new Response(
      JSON.stringify({
        content: [{ type: "text", text: "[]" }],
      }),
      { status: 200 }
    );
  }) as typeof fetch;

  const endpoint = "https://example.invalid/custom-anthropic/messages";
  await callAnthropic("test-key", "test-model", "system", "prompt", 4096, endpoint);

  assert.equal(requestedUrl, endpoint);
});

test("callLLM preserves anthropic provider baseURL when configured", async (t) => {
  const originalFetch = globalThis.fetch;
  t.after(() => {
    globalThis.fetch = originalFetch;
  });

  let requestedUrl: string | undefined;
  globalThis.fetch = (async (input) => {
    requestedUrl = String(input);
    return new Response(
      JSON.stringify({
        content: [{ type: "text", text: "[]" }],
      }),
      { status: 200 }
    );
  }) as typeof fetch;

  const endpoint = "https://provider-config.example/v1/messages";
  await callLLM(
    { type: "anthropic", config: { apiKey: "test-key", model: "test-model", baseURL: endpoint } },
    "system",
    "prompt"
  );

  assert.equal(requestedUrl, endpoint);
});
