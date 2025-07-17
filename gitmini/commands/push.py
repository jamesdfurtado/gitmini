import os
import sys
import json
import hashlib
import httpx
from gitmini.api_config import API_URL
from gitmini_core.utils import find_gitmini_root
from gitmini_core.classes.Repo import Repo

CONFIG_FILENAME = "config.json"
HEAD_FILENAME = "HEAD"


def handle_push(args):
    # Determine local and remote branch names
    branch_arg = args.branch
    repo_root = find_gitmini_root()
    repo = Repo(repo_root)
    config_path = os.path.join(repo.gitmini_dir, CONFIG_FILENAME)
    head_path = os.path.join(repo.gitmini_dir, HEAD_FILENAME)
    heads_dir = os.path.join(repo.gitmini_dir, "refs", "heads")

    # Check config exists
    if not os.path.exists(config_path):
        print(f"fatal: {config_path} not found. Please run 'gitmini init' and 'gitmini login' first.", file=sys.stderr)
        sys.exit(1)

    # Load config
    with open(config_path, "r") as f:
        config = json.load(f)
    username = config.get("username") or config.get("user")
    raw_api_key = config.get("api_key")
    repo_name = config.get("repo")
    if not username or not raw_api_key or not repo_name:
        print(f"fatal: config.json missing 'username', 'api_key', or 'repo'. Please run 'gitmini login' and 'gitmini remote add' first.", file=sys.stderr)
        sys.exit(1)

    # Parse branch argument
    if branch_arg:
        if ":" in branch_arg:
            local_branch, remote_branch = branch_arg.split(":", 1)
            if not local_branch:
                # If user does ':remote', treat local as current branch
                local_branch = None
        else:
            local_branch = remote_branch = branch_arg
    else:
        local_branch = remote_branch = None

    # If local_branch is None, get current branch from HEAD
    if not local_branch:
        if not os.path.exists(head_path):
            print(f"fatal: {head_path} not found. Cannot determine current branch.", file=sys.stderr)
            sys.exit(1)
        with open(head_path) as f:
            head_content = f.read().strip()
        if head_content.startswith("ref: refs/heads/"):
            local_branch = remote_branch = head_content.split("/")[-1]
        else:
            print("fatal: HEAD is detached or invalid. Cannot push.", file=sys.stderr)
            sys.exit(1)

    # Check that the local branch exists
    local_branch_path = os.path.join(heads_dir, local_branch)
    if not os.path.exists(local_branch_path):
        print(f"fatal: local branch '{local_branch}' does not exist.", file=sys.stderr)
        sys.exit(1)

    # Read new_commit from local branch file
    with open(local_branch_path, "r") as f:
        new_commit = f.read().strip()
    if not new_commit:
        print(f"fatal: local branch '{local_branch}' does not have a commit.", file=sys.stderr)
        sys.exit(1)

    # Read last_known_remote_commit from remote_branches.json
    remote_branches_path = os.path.join(repo.gitmini_dir, "refs", "remote_branches.json")
    if not os.path.exists(remote_branches_path):
        print(f"fatal: {remote_branches_path} not found. Please run 'gitmini remote add' first.", file=sys.stderr)
        sys.exit(1)
    with open(remote_branches_path, "r") as f:
        remote_branches = json.load(f)
    last_known_remote_commit = remote_branches.get(remote_branch)
    if last_known_remote_commit is None:
        print(f"fatal: remote branch '{remote_branch}' not found in remote_branches.json.", file=sys.stderr)
        sys.exit(1)

    # Hash the API key
    hashed_api_key = hashlib.sha256(raw_api_key.encode()).hexdigest()

    # Prepare payload
    payload = {
        "user": username,
        "api_key": hashed_api_key,
        "repo": repo_name,
        "branch": remote_branch,
        "last_known_remote_commit": last_known_remote_commit,
        "new_commit": new_commit
    }

    # DEBG TOOL: Print payload for manual inspection
    # print("DEBUG PAYLOAD:", payload)

    # Send API request
    try:
        resp = httpx.post(f"{API_URL}/api/remote/push", json=payload, timeout=10)
        try:
            data = resp.json()
        except Exception:
            data = None
        if resp.status_code == 200:
            if data and data.get("status") == "ok":
                print(f"[SUCCESS] {data.get('message', 'Push successful.')}")
            else:
                print(f"fatal: {data.get('message', 'Unknown error') if data else 'Unknown error'}", file=sys.stderr)
                sys.exit(1)
        else:
            # Try to print error message from JSON
            if data and 'message' in data:
                print(f"fatal: {data['message']}", file=sys.stderr)
            else:
                print(f"fatal: Failed to connect to remote: HTTP {resp.status_code}", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"fatal: Failed to connect to remote: {e}", file=sys.stderr)
        sys.exit(1)
