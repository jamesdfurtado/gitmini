import os
import sys
import json
import hashlib
import httpx
from gitmini.api_config import API_URL
from gitmini_core.utils import find_gitmini_root
from gitmini_core.classes.Repo import Repo

CONFIG_FILENAME = "config.json"
REMOTE_BRANCHES_FILENAME = "remote_branches.json"


def handle_remote_add(args):
    repo_name = args.repository
    repo_root = find_gitmini_root()
    repo = Repo(repo_root)
    config_path = os.path.join(repo.gitmini_dir, CONFIG_FILENAME)
    refs_dir = os.path.join(repo.gitmini_dir, "refs")
    remote_branches_path = os.path.join(refs_dir, REMOTE_BRANCHES_FILENAME)

    # Check config exists
    if not os.path.exists(config_path):
        print(f"fatal: {config_path} not found. Please run 'gitmini init' and 'gitmini login' first.", file=sys.stderr)
        sys.exit(1)

    # Load config
    with open(config_path, "r") as f:
        config = json.load(f)
    username = config.get("username") or config.get("user")
    raw_api_key = config.get("api_key")
    if not username or not raw_api_key:
        print(f"fatal: config.json missing 'username' or 'api_key'. Please run 'gitmini login' again.", file=sys.stderr)
        sys.exit(1)

    # Hash the API key
    hashed_api_key = hashlib.sha256(raw_api_key.encode()).hexdigest()

    # Prepare payload
    payload = {
        "user": username,
        "api_key": hashed_api_key,
        "repo": repo_name
    }

    # Send API request
    try:
        resp = httpx.post(f"{API_URL}/api/remote/add", json=payload, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"fatal: Failed to connect to remote: {e}", file=sys.stderr)
        sys.exit(1)

    # Handle response
    if data.get("status") == "ok":
        # Add repo to config.json
        config["repo"] = repo_name
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
            
        # Write branches to remote_branches.json
        branches = data.get("branches", {})
        os.makedirs(refs_dir, exist_ok=True)
        with open(remote_branches_path, "w") as f:
            json.dump(branches, f, indent=2)
        print(f"[SUCCESS] Connected to remote '{repo_name}'. Branches saved.")
    else:
        print(f"fatal: {data.get('message', 'Unknown error')}", file=sys.stderr)
        sys.exit(1) 