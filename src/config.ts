import { existsSync } from "node:fs";
import { readFile } from "node:fs/promises";
import path from "node:path";
import yaml from "js-yaml";

import {
  DEFAULT_AGENTS,
  DEFAULT_DEBATE_CONFIG,
  DEFAULT_PRINCIPAL_MANDATE,
  SwarmConfigSchema,
  type SwarmConfig,
} from "./types.js";

export const DEFAULT_SWARM_CONFIG: SwarmConfig = SwarmConfigSchema.parse({
  agents: DEFAULT_AGENTS,
  debate: DEFAULT_DEBATE_CONFIG,
  principal: { mandate: DEFAULT_PRINCIPAL_MANDATE },
  output: { mode: "outcome" },
});

export async function loadSwarmConfig(
  workspaceRoot: string = process.cwd(),
  configPath = ".swarm.yml"
): Promise<SwarmConfig> {
  const resolvedConfigPath = path.isAbsolute(configPath)
    ? configPath
    : path.join(workspaceRoot, configPath);

  if (!existsSync(resolvedConfigPath)) {
    return DEFAULT_SWARM_CONFIG;
  }

  const rawConfig = await readFile(resolvedConfigPath, "utf8");
  const parsedConfig = yaml.load(rawConfig) ?? {};
  return SwarmConfigSchema.parse(parsedConfig);
}