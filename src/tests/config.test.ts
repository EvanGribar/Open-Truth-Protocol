import assert from "node:assert/strict";
import { mkdtemp, writeFile } from "node:fs/promises";
import path from "node:path";
import os from "node:os";
import test from "node:test";

import { loadSwarmConfig, DEFAULT_SWARM_CONFIG } from "../config.js";

test("loadSwarmConfig returns the default config when the file is missing", async () => {
  const config = await loadSwarmConfig(await mkdtemp(path.join(os.tmpdir(), "swarm-review-")), ".swarm.yml");

  assert.deepEqual(config, DEFAULT_SWARM_CONFIG);
});

test("loadSwarmConfig reads a local config file", async () => {
  const tempDir = await mkdtemp(path.join(os.tmpdir(), "swarm-review-"));
  const configPath = path.join(tempDir, ".swarm.yml");

  await writeFile(
    configPath,
    [
      "agents:",
      "  - name: custom",
      "    mandate: Review the change carefully.",
      "debate:",
      "  rounds: 1",
      "  min_confidence: 0.7",
      "principal:",
      "  mandate: Make the final call.",
      "output:",
      "  mode: full",
    ].join("\n"),
    "utf8"
  );

  const config = await loadSwarmConfig(tempDir);

  assert.equal(config.agents[0]?.name, "custom");
  assert.equal(config.debate.rounds, 1);
  assert.equal(config.debate.min_confidence, 0.7);
  assert.equal(config.principal.mandate, "Make the final call.");
  assert.equal(config.output.mode, "full");
});

test("loadSwarmConfig resolves exact $ENV_VAR references before validation", async (t) => {
  const tempDir = await mkdtemp(path.join(os.tmpdir(), "swarm-review-"));
  const configPath = path.join(tempDir, ".swarm.yml");
  const envName = "SWARM_REVIEW_TEST_API_KEY";

  const previousValue = process.env[envName];
  t.after(() => {
    if (previousValue === undefined) {
      delete process.env[envName];
      return;
    }
    process.env[envName] = previousValue;
  });
  process.env[envName] = "resolved-key";

  await writeFile(
    configPath,
    [
      "provider:",
      "  type: anthropic",
      "  config:",
      `    apiKey: $${envName}`,
      "    model: claude-3-5-sonnet-latest",
    ].join("\n"),
    "utf8"
  );

  const config = await loadSwarmConfig(tempDir);

  assert.equal(config.provider?.type, "anthropic");
  assert.equal(config.provider?.config.apiKey, "resolved-key");
});

test("loadSwarmConfig fails clearly when a referenced env var is missing", async () => {
  const tempDir = await mkdtemp(path.join(os.tmpdir(), "swarm-review-"));
  const configPath = path.join(tempDir, ".swarm.yml");
  const missingEnvName = "SWARM_REVIEW_TEST_MISSING_API_KEY";

  delete process.env[missingEnvName];

  await writeFile(
    configPath,
    [
      "provider:",
      "  type: anthropic",
      "  config:",
      `    apiKey: $${missingEnvName}`,
      "    model: claude-3-5-sonnet-latest",
    ].join("\n"),
    "utf8"
  );

  await assert.rejects(
    () => loadSwarmConfig(tempDir),
    new RegExp(`Missing environment variable "${missingEnvName}"`)
  );
});
