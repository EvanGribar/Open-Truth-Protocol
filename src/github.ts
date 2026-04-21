import type { Octokit } from "@octokit/rest";

const MANAGED_COMMENT_MARKER = "<!-- swarm-review:managed-comment -->";

function withManagedCommentMarker(body: string): string {
  if (body.includes(MANAGED_COMMENT_MARKER)) {
    return body;
  }

  return `${body}\n\n${MANAGED_COMMENT_MARKER}`;
}

export async function upsertPullRequestComment(
  octokit: Octokit,
  owner: string,
  repo: string,
  pullNumber: number,
  body: string
): Promise<void> {
  const managedBody = withManagedCommentMarker(body);

  const comments = await octokit.paginate(
    octokit.rest.issues.listComments,
    { owner, repo, issue_number: pullNumber, per_page: 100 },
    (response) => response.data
  );

  const existingComment = [...comments].reverse().find(
    (comment) =>
      comment.body?.includes(MANAGED_COMMENT_MARKER) ||
      (comment.body?.startsWith("## swarm-review") && comment.user?.type === "Bot")
  );

  if (existingComment) {
    await octokit.rest.issues.updateComment({
      owner,
      repo,
      comment_id: existingComment.id,
      body: managedBody,
    });
    return;
  }

  await octokit.rest.issues.createComment({
    owner,
    repo,
    issue_number: pullNumber,
    body: managedBody,
  });
}

export async function updateCheckRun(
  octokit: Octokit,
  owner: string,
  repo: string,
  checkRunId: string | undefined,
  summary: string
): Promise<void> {
  if (!checkRunId) {
    return;
  }

  if (!/^\d+$/.test(checkRunId)) {
    return;
  }

  const numericCheckRunId = Number(checkRunId);
  if (!Number.isSafeInteger(numericCheckRunId) || numericCheckRunId <= 0) {
    return;
  }

  await octokit.rest.checks.update({
    owner,
    repo,
    check_run_id: numericCheckRunId,
    status: "completed",
    conclusion: "neutral",
    output: {
      title: "swarm-review",
      summary,
    },
  });
}