import os
import sys
import json
import time
import hashlib
import httpx
import webbrowser
from gitmini_core.utils import find_gitmini_root
from gitmini_core.classes.Repo import Repo

DEFAULT_API_URL = "http://localhost:8000"
API_URL_ENV = "GITMINI_API_URL"
CONFIG_FILENAME = "config.json"


def resolve_api_url(repo, cli_url=None):
    """
    Resolve the API base URL using priority:
    1. CLI flag (cli_url)
    2. Environment variable (GITMINI_API_URL)
    3. config.json (if present)
    4. Default
    """
    if cli_url:
        return cli_url
    env_url = os.environ.get(API_URL_ENV)
    if env_url:
        return env_url
    config_path = os.path.join(repo.gitmini_dir, CONFIG_FILENAME)
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
            if "api_url" in config:
                return config["api_url"]
        except Exception:
            pass
    return DEFAULT_API_URL


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

    api_url = resolve_api_url(repo, getattr(args, "api_url", None))

    print("A browser window will open for you to log in or sign up.")
    try:
        # 1. Start auth session
        resp = httpx.post(f"{api_url}/auth/init", timeout=10)
        resp.raise_for_status()
        data = resp.json()
        cli_token = data["cli_token"]
        login_url = data["login_url"]
    except Exception as e:
        print(f"fatal: Failed to initiate authentication: {e}", file=sys.stderr)
        sys.exit(1)

    # 2. Open browser
    webbrowser.open(login_url)
    print(f"If your browser did not open, visit: {login_url}")

    # 3. Poll for status
    print("Waiting for authentication to complete...")
    start = time.time()
    while True:
        if time.time() - start > 300:  # 5 minutes
            print("fatal: Authentication timed out. Please try again.", file=sys.stderr)
            sys.exit(1)
        try:
            status_resp = httpx.get(f"{api_url}/auth/status?cli_token={cli_token}", timeout=5)
            if status_resp.status_code == 200:
                status_data = status_resp.json()
                username = status_data["username"]
                api_key = status_data["api_key"]
                # Save config with RAW api key
                config = {"username": username, "api_key": api_key, "api_url": api_url}
                with open(config_path, "w") as f:
                    json.dump(config, f, indent=2)
                print(f"[SUCCESS] Logged in as {username}.")
                return
        except Exception:
            pass  # Ignore polling errors, keep trying
        time.sleep(2) 