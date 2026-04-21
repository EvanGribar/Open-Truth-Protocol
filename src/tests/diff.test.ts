import assert from "node:assert/strict";
import test from "node:test";

import { formatFileDiffs } from "../diff.js";
import type { FileDiff } from "../types.js";

test("formatFileDiffs renders multiple files and large patches", () => {
  const files: FileDiff[] = [
    {
      path: "src/large.ts",
      status: "modified",
      additions: 10,
      deletions: 1,
      changes: 11,
      patch: "x".repeat(80),
    },
    {
      path: "src/extra.ts",
      status: "added",
      additions: 5,
      deletions: 0,
      changes: 5,
      patch: "+const a = 1;",
    },
  ];

  const rendered = formatFileDiffs(files);

  assert.match(rendered, /### src\/large\.ts/);
  assert.match(rendered, /### src\/extra\.ts/);
  assert.match(rendered, /```diff\nx{80}\n```/);
  assert.match(rendered, /```diff\n\+const a = 1;\n```/);
});

