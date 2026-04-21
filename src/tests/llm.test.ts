import assert from "node:assert/strict";
import test from "node:test";

import { extractJsonText } from "../llm.js";

test("extractJsonText accepts fenced JSON", () => {
  const extracted = extractJsonText("```json\n[{\"id\":\"1\"}]\n```");

  assert.equal(extracted, "[{\"id\":\"1\"}]");
});

test("extractJsonText extracts embedded JSON from surrounding text", () => {
  const extracted = extractJsonText("Here is the payload: {\"ok\":true}");

  assert.equal(extracted, "{\"ok\":true}");
});