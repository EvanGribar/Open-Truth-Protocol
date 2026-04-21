import { Octokit } from "@octokit/rest";

import { FileDiffSchema, type FileDiff } from "./types.js";

type DiffFormatOptions = {
  maxFiles?: number;
  maxPatchCharsPerFile?: number;
  maxTotalChars?: number;
};

const DEFAULT_DIFF_FORMAT_OPTIONS: Required<DiffFormatOptions> = {
  maxFiles: 80,
  maxPatchCharsPerFile: 12_000,
  maxTotalChars: 180_000,
};

export function createOctokit(token: string): Octokit {
  return new Octokit({
    auth: token,
    userAgent: "swarm-review",
  });
}

export async function fetchPullRequestDiff(
  octokit: Octokit,
  owner: string,
  repo: string,
  pullNumber: number
): Promise<FileDiff[]> {
  const files = await octokit.paginate(
    octokit.rest.pulls.listFiles,
    { owner, repo, pull_number: pullNumber, per_page: 100 },
    (response) => response.data
  );

  return files.map((file) =>
    FileDiffSchema.parse({
      path: file.filename,
      status: file.status,
      additions: file.additions,
      deletions: file.deletions,
      changes: file.changes,
      patch: file.patch ?? undefined,
      previousPath: file.previous_filename ?? undefined,
    })
  );
}

export function formatFileDiffs(files: FileDiff[], options: DiffFormatOptions = {}): string {
  const settings = {
    ...DEFAULT_DIFF_FORMAT_OPTIONS,
    ...options,
  };

  const SEPARATOR = "\n\n---\n\n";

  // Pre-calculate metadata to establish the initial budget overhead.
  // We use placeholder counts that won't significantly change the length.
  const metadataPlaceholder = [
    "### Diff Budget",
    `- total_files: ${files.length}`,
    `- included_files: 888`,
    `- omitted_files: 888`,
    `- max_files: ${settings.maxFiles}`,
    `- max_patch_chars_per_file: ${settings.maxPatchCharsPerFile}`,
    `- max_total_chars: ${settings.maxTotalChars}`,
  ].join("\n");

  let remainingChars = settings.maxTotalChars - metadataPlaceholder.length - SEPARATOR.length;
  const selectedFiles = files.slice(0, settings.maxFiles);
  const renderedFiles: string[] = [];

  for (const file of selectedFiles) {
    const header = [
      `### ${file.path}`,
      `status: ${file.status}`,
      `additions: ${file.additions}`,
      `deletions: ${file.deletions}`,
      file.previousPath ? `previous path: ${file.previousPath}` : null,
    ]
      .filter(Boolean)
      .join("\n");

    const rawPatch = file.patch ?? "PATCH UNAVAILABLE";
    const patchTruncated = rawPatch.length > settings.maxPatchCharsPerFile;
    const patch = patchTruncated
      ? `${rawPatch.slice(0, settings.maxPatchCharsPerFile)}\n... [PATCH TRUNCATED]`
      : rawPatch;
    const rendered = `${header}\n\n\`\`\`diff\n${patch}\n\`\`\``;

    // Account for the file content and the separator that will follow it.
    if (rendered.length + SEPARATOR.length > remainingChars) {
      break;
    }

    renderedFiles.push(rendered);
    remainingChars -= rendered.length + SEPARATOR.length;
  }

  const omittedByFileLimit = Math.max(0, files.length - selectedFiles.length);
  const omittedByCharBudget = Math.max(0, selectedFiles.length - renderedFiles.length);
  const omittedCount = omittedByFileLimit + omittedByCharBudget;

  const metadata = [
    "### Diff Budget",
    `- total_files: ${files.length}`,
    `- included_files: ${renderedFiles.length}`,
    `- omitted_files: ${omittedCount}`,
    `- max_files: ${settings.maxFiles}`,
    `- max_patch_chars_per_file: ${settings.maxPatchCharsPerFile}`,
    `- max_total_chars: ${settings.maxTotalChars}`,
  ].join("\n");

  return [metadata, ...renderedFiles].join(SEPARATOR);
}