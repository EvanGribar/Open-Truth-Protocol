import { z } from "zod";

import { FindingSchema, RawFindingSchema, type Finding, type RawFinding } from "./types.js";

const ANTHROPIC_MESSAGES_ENDPOINT = "https://api.anthropic.com/v1/messages";
const DEFAULT_REQUEST_TIMEOUT_MS = 90_000;
const MAX_RETRY_ATTEMPTS = 3;

export const DEFAULT_ANTHROPIC_MODEL = "claude-3-5-sonnet-latest";
export const DEFAULT_API_ENDPOINT = ANTHROPIC_MESSAGES_ENDPOINT;

function shouldRetry(statusCode: number): boolean {
  return statusCode === 408 || statusCode === 409 || statusCode === 429 || statusCode >= 500;
}

function waitFor(ms: number): Promise<void> {
  return new Promise((resolve) => {
    setTimeout(resolve, ms);
  });
}

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

    throw new Error("Anthropic response did not contain parseable JSON.");
  }
}

export async function callAnthropic(
  apiKey: string,
  model: string,
  system: string,
  prompt: string,
  maxTokens = 4096,
  apiEndpoint = DEFAULT_API_ENDPOINT
): Promise<string> {
  let lastError: Error | undefined;

  for (let attempt = 1; attempt <= MAX_RETRY_ATTEMPTS; attempt += 1) {
    const abortController = new AbortController();
    const timeout = setTimeout(() => abortController.abort(), DEFAULT_REQUEST_TIMEOUT_MS);
    let retryableFailure = false;
    let retryDelayMs = 500 * 2 ** (attempt - 1);

    try {
      const response = await fetch(apiEndpoint, {
        method: "POST",
        headers: {
          "content-type": "application/json",
          "x-api-key": apiKey,
          "anthropic-version": "2023-06-01",
        },
        body: JSON.stringify({
          model,
          max_tokens: maxTokens,
          temperature: 0.2,
          system,
          messages: [{ role: "user", content: prompt }],
        }),
        signal: abortController.signal,
      });

      if (!response.ok) {
        const retryAfterHeader = response.headers.get("retry-after");
        const retryAfterSeconds = retryAfterHeader ? Number(retryAfterHeader) : NaN;
        if (Number.isFinite(retryAfterSeconds) && retryAfterSeconds > 0) {
          retryDelayMs = Math.max(retryDelayMs, retryAfterSeconds * 1000);
        }

        const error = new Error(
          `Anthropic request failed with ${response.status}: ${await response.text()}`
        );
        retryableFailure = shouldRetry(response.status);
        throw error;
      }

      const payload: {
        content?: Array<{ type: string; text?: string }>;
      } = await response.json();

      return (payload.content ?? [])
        .filter(
          (block): block is { type: string; text: string } =>
            block.type === "text" && typeof block.text === "string"
        )
        .map((block) => block.text)
        .join("");
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));
      if (lastError.name === "AbortError" || lastError instanceof TypeError) {
        retryableFailure = true;
      }

      if (attempt < MAX_RETRY_ATTEMPTS && retryableFailure) {
        await waitFor(retryDelayMs);
        continue;
      }
      throw lastError;
    } finally {
      clearTimeout(timeout);
    }
  }

  throw lastError ?? new Error("Anthropic request failed unexpectedly.");
}

export async function callAnthropicStructured<T>(
  apiKey: string,
  model: string,
  system: string,
  prompt: string,
  schema: z.ZodType<T>,
  apiEndpoint = DEFAULT_API_ENDPOINT
): Promise<T> {
  const rawText = await callAnthropic(apiKey, model, system, prompt, 4096, apiEndpoint);
  const jsonText = extractJsonText(rawText);
  const parsed = JSON.parse(jsonText) as unknown;
  return schema.parse(parsed);
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