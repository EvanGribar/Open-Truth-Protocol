import { Octokit } from "@octokit/rest";

import { FileDiffSchema, type FileDiff } from "./types.js";

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

export function formatFileDiffs(files: FileDiff[]): string {
  return files
    .map((file) => {
      const header = [
        `### ${file.path}`,
        `status: ${file.status}`,
        `additions: ${file.additions}`,
        `deletions: ${file.deletions}`,
        file.previousPath ? `previous path: ${file.previousPath}` : null,
      ]
        .filter(Boolean)
        .join("\n");

      const patch = file.patch ?? "PATCH UNAVAILABLE";
      return `${header}\n\n\`\`\`diff\n${patch}\n\`\`\``;
    })
    .join("\n\n---\n\n");
}