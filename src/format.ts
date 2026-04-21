import type { DebateTranscript, Finding, Severity } from "./types.js";

const SEVERITY_MARKER: Record<Severity, string> = {
  blocking: "[BLOCKING]",
  warning: "[WARNING]",
  suggestion: "[SUGGESTION]",
};

function findingLine(finding: Finding): string {
  const marker = SEVERITY_MARKER[finding.severity];
  const rebuttal = finding.rebuttal_to ? `, rebuttal to ${finding.rebuttal_to}` : "";
  return `- ${marker} **${finding.agent}** ${finding.file}:${finding.line} (${finding.severity}, ${finding.confidence.toFixed(2)}${rebuttal}) - ${finding.claim}`;
}

export function renderDebateTranscriptMarkdown(transcript: DebateTranscript): string {
  const lines: string[] = ["", "---", "", "### Debate Transcript"];

  transcript.rounds.forEach((round, index) => {
    lines.push("");
    lines.push(`#### Round ${index + 1}`);

    if (round.length === 0) {
      lines.push("- No findings in this round.");
      return;
    }

    round.forEach((finding) => lines.push(findingLine(finding)));
  });

  return lines.join("\n");
}
