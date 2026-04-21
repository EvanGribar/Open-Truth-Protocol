import type { Octokit } from "@octokit/rest";

export async function upsertPullRequestComment(
  octokit: Octokit,
  owner: string,
  repo: string,
  pullNumber: number,
  body: string
): Promise<void> {
  const comments = await octokit.paginate(
    octokit.rest.issues.listComments,
    { owner, repo, issue_number: pullNumber, per_page: 100 },
    (response) => response.data
  );

  const existingComment = [...comments].reverse().find((comment) => comment.body?.startsWith("## swarm-review"));

  if (existingComment) {
    await octokit.rest.issues.updateComment({
      owner,
      repo,
      comment_id: existingComment.id,
      body,
    });
    return;
  }

  await octokit.rest.issues.createComment({
    owner,
    repo,
    issue_number: pullNumber,
    body,
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

  const numericCheckRunId = Number(checkRunId);
  if (!Number.isFinite(numericCheckRunId)) {
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