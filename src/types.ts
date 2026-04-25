import { z } from "zod";

export const SeveritySchema = z.enum(["blocking", "warning", "suggestion"]);
export type Severity = z.infer<typeof SeveritySchema>;

export const FindingBodySchema = z.object({
  agent: z.string().min(1),
  severity: SeveritySchema,
  file: z.string().min(1),
  line: z.number().int().positive(),
  claim: z.string().min(1),
  confidence: z.number().min(0).max(1),
  rebuttal_to: z.string().min(1).optional(),
});

export const RawFindingSchema = FindingBodySchema.extend({
  id: z.string().min(1).optional(),
});

export const FindingSchema = FindingBodySchema.extend({
  id: z.string().min(1),
});

export type Finding = z.infer<typeof FindingSchema>;
export type RawFinding = z.infer<typeof RawFindingSchema>;

export const AgentConfigSchema = z.object({
  name: z.string().min(1),
  mandate: z.string().min(1),
  model: z.string().min(1).optional(),
});

export type AgentConfig = z.infer<typeof AgentConfigSchema>;

export const DEFAULT_AGENTS: AgentConfig[] = [
  {
    name: "security",
    mandate:
      "Review for security vulnerabilities. Look for injection risks, exposed secrets, broken auth, insecure defaults, and unsafe data handling.",
  },
  {
    name: "performance",
    mandate:
      "Review for performance issues. Look for N+1 queries, unnecessary re-renders, expensive operations in hot paths, and missing pagination.",
  },
  {
    name: "architecture",
    mandate:
      "Review for architectural concerns. Look for separation of concerns violations, tight coupling, naming inconsistency, and patterns that do not fit the codebase.",
  },
  {
    name: "dx",
    mandate:
      "Review for developer experience. Look for missing tests, outdated docs, unclear variable names, and changes that will be hard to maintain.",
  },
];

export const DEFAULT_DEBATE_CONFIG = {
  rounds: 2,
  min_confidence: 0.6,
};

export const DEFAULT_PRINCIPAL_MANDATE =
  "You are the principal engineer. Read the full debate and make final calls. Be direct. Show your reasoning. Surface genuine disagreements clearly.";

export const DebateConfigSchema = z.object({
  rounds: z.number().int().min(0).default(DEFAULT_DEBATE_CONFIG.rounds),
  min_confidence: z
    .number()
    .min(0)
    .max(1)
    .default(DEFAULT_DEBATE_CONFIG.min_confidence),
});

export const PrincipalConfigSchema = z.object({
  mandate: z.string().min(1).default(DEFAULT_PRINCIPAL_MANDATE),
});

export const DiffConfigSchema = z.object({
  maxFiles: z.number().int().positive().default(80),
  maxPatchCharsPerFile: z.number().int().positive().default(12_000),
  maxTotalChars: z.number().int().positive().default(180_000),
  excludePatterns: z.array(z.string()).default([]),
});

export type DiffConfig = z.infer<typeof DiffConfigSchema>;

export const SwarmConfigSchema = z.object({
  agents: z.array(AgentConfigSchema).min(1).default(DEFAULT_AGENTS),
  debate: DebateConfigSchema.default(DEFAULT_DEBATE_CONFIG),
  principal: PrincipalConfigSchema.default({ mandate: DEFAULT_PRINCIPAL_MANDATE }),
  output: z
    .object({
      mode: z.enum(["outcome", "full"]).default("outcome"),
    })
    .default({ mode: "outcome" }),
  diff: DiffConfigSchema.default({
    maxFiles: 80,
    maxPatchCharsPerFile: 12_000,
    maxTotalChars: 180_000,
    excludePatterns: [],
  }),
});

export type DebateConfig = z.infer<typeof DebateConfigSchema>;
export type PrincipalConfig = z.infer<typeof PrincipalConfigSchema>;
export type SwarmConfig = z.infer<typeof SwarmConfigSchema>;

export const FileDiffSchema = z.object({
  path: z.string().min(1),
  status: z.string().min(1),
  additions: z.number().int().nonnegative(),
  deletions: z.number().int().nonnegative(),
  changes: z.number().int().nonnegative(),
  patch: z.string().optional(),
  previousPath: z.string().min(1).optional(),
});

export type FileDiff = z.infer<typeof FileDiffSchema>;

export const DebateTranscriptSchema = z.object({
  rounds: z.array(z.array(FindingSchema)),
  agents: z.array(AgentConfigSchema),
});

export type DebateTranscript = z.infer<typeof DebateTranscriptSchema>;

export const PrincipalDecisionSchema = z.object({
  finding: FindingSchema,
  decision: z.string().min(1),
});

export const PrincipalDisputeSchema = z.object({
  finding: FindingSchema,
  rebuttal: FindingSchema,
});

export const PrincipalSummarySchema = z.object({
  agreements: z.array(FindingSchema),
  disputes: z.array(PrincipalDisputeSchema),
  final_calls: z.array(PrincipalDecisionSchema),
  summary: z.string().min(1),
});

export type PrincipalSummary = z.infer<typeof PrincipalSummarySchema>;