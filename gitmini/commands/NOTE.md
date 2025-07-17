# Push

When GitMini CLI makes a push, we do:

"POST /api/remote/push", with the following payload as multipart/form-data:

Form fields:
- user: james
- api_key: abc123xyz
- repo: my-repo
- branch: main
- last_known_remote_commit: def456...
- new_commit: abc123...

File field:
- objects: new_objects.tar.gz (compressed file containing ONLY the new objects needed)

Responses:

Successful push:
{
  "status": "ok",
  "message": "Push successful.",
  "branch": "<current-remote-branch>",
  "most_recent_remote_branch_commit": "ghi789..."  // the current remote branch's most recent commit (should be the commit we just pushed up)
}

rejected- non-fast forward push.
This happens when last_known_remote_commit does not match the current commit at refs/heads/<branch>
on the server.
{
  "status": "error",
  "message": "Non-fast-forward push rejected. Remote branch has diverged.",
  "branch": "<current-remote-branch>",
  "most_recent_remote_branch_commit": "ghi789..."  // actual current remote branch's most recent commit
}

Could not find specified branch
{
  "status": "error",
  "message": "Remote branch not found."
}

Auth failure
{
  "status": "error",
  "message": "Authentication failed"
}

Repo not found or unauthorized access
{
  "status": "error",
  "message": "Repository not found or access denied"
}

Malformed Payload
{
  "status": "error",
  "message": "Invalid push payload"
}

Corrupt or Missing Archive file (if new_objects.tar.gz is missing/unreadable)
{
  "status": "error",
  "message": "Object archive missing or corrupt"
}