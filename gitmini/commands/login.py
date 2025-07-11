import os
import sys
import json
import time
import httpx
import webbrowser
from gitmini_core.utils import find_gitmini_root
from gitmini_core.classes.Repo import Repo
from gitmini.api_config import API_URL

CONFIG_FILENAME = "config.json"


def handle_login(args):
    """
    Implements the browser-based CLI authentication flow for 'gitmini login'.
    """
    repo_root = find_gitmini_root()
    repo = Repo(repo_root)
    config_path = os.path.join(repo.gitmini_dir, CONFIG_FILENAME)
    if not os.path.exists(config_path):
        print(f"fatal: {config_path} not found. Please run 'gitmini init' first.", file=sys.stderr)
        sys.exit(1)

    print("A browser window will open for you to log in or sign up.")
    try:
        # Start auth session
        resp = httpx.post(f"{API_URL}/auth/init", timeout=10)
        resp.raise_for_status()
        data = resp.json()
        cli_token = data["cli_token"]
        login_url = data["login_url"]
    except Exception as e:
        print(f"fatal: Failed to initiate authentication: {e}", file=sys.stderr)
        sys.exit(1)

    # Open browser
    webbrowser.open(login_url)
    print(f"If your browser did not open, visit: {login_url}")

    # Poll for status
    print("Waiting for authentication to complete...")
    start = time.time()
    while True:
        if time.time() - start > 300:  # 5 minute timeout
            print("fatal: Authentication timed out. Please try again.", file=sys.stderr)
            sys.exit(1)
        try:
            status_resp = httpx.get(f"{API_URL}/auth/status?cli_token={cli_token}", timeout=5)
            if status_resp.status_code == 200:
                status_data = status_resp.json()
                username = status_data["username"]
                api_key = status_data["api_key"]
                # Save config with RAW api key
                config = {"username": username, "api_key": api_key}
                with open(config_path, "w") as f:
                    json.dump(config, f, indent=2)
                print(f"[SUCCESS] Logged in as {username}.")
                return
        except Exception:
            pass  # Keep trying till it works
        time.sleep(2) 