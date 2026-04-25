import { z } from "zod";

import { FindingSchema, RawFindingSchema, type Finding, type RawFinding, type ProviderConfig } from "./types.js";
import { createProvider, type LLMProvider } from "./providers.js";

const ANTHROPIC_MESSAGES_ENDPOINT = "https://api.anthropic.com/v1/messages";

export const DEFAULT_ANTHROPIC_MODEL = "claude-3-5-sonnet-latest";
export const DEFAULT_API_ENDPOINT = ANTHROPIC_MESSAGES_ENDPOINT;

function stripMarkdownFences(text: string): string {
  const trimmed = text.trim();

  if (!trimmed.startsWith("```")) {
    return trimmed;
  }

  const fenceMatch = trimmed.match(/^```(?:json)?\s*([\s\S]*?)\s*```$/i);
  return fenceMatch ? fenceMatch[1].trim() : trimmed;
}

export function extractJsonText(text: string): string {
  const trimmed = stripMarkdownFences(text);

  try {
    JSON.parse(trimmed);
    return trimmed;
  } catch {
    const firstObject = trimmed.indexOf("{");
    const firstArray = trimmed.indexOf("[");
    const start =
      firstObject === -1
        ? firstArray
        : firstArray === -1
          ? firstObject
          : Math.min(firstObject, firstArray);
    const endObject = trimmed.lastIndexOf("}");
    const endArray = trimmed.lastIndexOf("]");
    const end = Math.max(endObject, endArray);

    if (start >= 0 && end > start) {
      const candidate = trimmed.slice(start, end + 1);
      JSON.parse(candidate);
      return candidate;
    }

    throw new Error("LLM response did not contain parseable JSON.");
  }
}

export async function callLLM(
  providerConfig: ProviderConfig,
  system: string,
  prompt: string,
  maxTokens = 4096
): Promise<string> {
  const provider = createProvider(providerConfig);
  return provider.call(system, prompt, maxTokens);
}

export async function callLLMStructured<T>(
  providerConfig: ProviderConfig,
  system: string,
  prompt: string,
  schema: z.ZodType<T>
): Promise<T> {
  const rawText = await callLLM(providerConfig, system, prompt);
  const jsonText = extractJsonText(rawText);
  const parsed = JSON.parse(jsonText) as unknown;
  return schema.parse(parsed);
}

// Legacy functions for backward compatibility
export async function callAnthropic(
  apiKey: string,
  model: string,
  system: string,
  prompt: string,
  maxTokens = 4096,
  apiEndpoint = DEFAULT_API_ENDPOINT
): Promise<string> {
  return callLLM(
    { type: "anthropic", config: { apiKey, model } },
    system,
    prompt,
    maxTokens
  );
}

export async function callAnthropicStructured<T>(
  apiKey: string,
  model: string,
  system: string,
  prompt: string,
  schema: z.ZodType<T>,
  apiEndpoint = DEFAULT_API_ENDPOINT
): Promise<T> {
  return callLLMStructured(
    { type: "anthropic", config: { apiKey, model } },
    system,
    prompt,
    schema
  );
}

export function normalizeFinding(
  finding: RawFinding,
  fallbackAgent: string,
  idPrefix: string
): Finding {
  return FindingSchema.parse({
    id: finding.id?.trim() || idPrefix,
    agent: finding.agent?.trim() || fallbackAgent,
    severity: finding.severity,
    file: finding.file.trim(),
    line: finding.line,
    claim: finding.claim.trim(),
    confidence: finding.confidence,
    ...(finding.rebuttal_to ? { rebuttal_to: finding.rebuttal_to.trim() } : {}),
  });
}

export function ensureFindingArray(values: unknown): RawFinding[] {
  return z.array(RawFindingSchema).parse(values);
}