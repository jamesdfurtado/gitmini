import os
import datetime
import hashlib
from gitmini.utils import find_gitmini_root

def handle_commit(args, _test_timestamp=None):
    """ Handles the 'commit' command to record a new commit from staged files. """

    # Locate the GitMini repo root
    repo_root = find_gitmini_root()
    print(f"Located .gitmini repo at: {repo_root}")

    # Check for existing index
    index_path = os.path.join(repo_root, ".gitmini", "index")
    if not os.path.exists(index_path):
        print("Nothing to commit: staging area is missing.")
        return

    # Read index and ensure it has content
    with open(index_path, "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    if not lines:
        print("Nothing to commit: staging area is empty.")
        return

    print("Staged files found. Proceeding with commit...")

    # Parse index lines into (hash, path) pairs
    staged_entries = []
    for line in lines:
        try:
            hash_val, rel_path = line.split(" ", 1)
            staged_entries.append((hash_val, rel_path))
        except ValueError:
            print(f"Skipping malformed index entry: {line}")

    # Get parent commit hash if HEAD exists
    head_path = os.path.join(repo_root, ".gitmini", "HEAD")
    parent_hash = None
    if os.path.exists(head_path):
        with open(head_path, "r") as f:
            parent_hash = f.read().strip()

    # Get current timestamp (allow override for testing)
    timestamp = _test_timestamp or datetime.datetime.now().isoformat()

    # Get commit message
    import sys
    if args.message:
        message = args.message.strip()
    else:
        if not sys.stdin.isatty():
            print("Error: commit message required in non-interactive mode.")
            return
        message = input("Enter commit message: ").strip()

    if not message:
        print("Aborting commit: empty message.")
        return

    # Construct commit object as a string
    lines = []
    if parent_hash:
        lines.append(f"parent {parent_hash}")
    lines.append(f"date {timestamp}")
    lines.append(f"message {message}")
    lines.append("")  # blank line
    for hash_val, path in staged_entries:
        lines.append(f"{hash_val} {path}")

    commit_contents = "\n".join(lines)
    print("\n--- Commit Content Preview ---")
    print(commit_contents)
    print("------------------------------")

    # Encode commit contents and compute SHA-1 hash
    commit_bytes = commit_contents.encode('utf-8')
    commit_hash = hashlib.sha1(commit_bytes).hexdigest()

    # Determine commit object path
    objects_dir = os.path.join(repo_root, ".gitmini", "objects")
    commit_path = os.path.join(objects_dir, commit_hash)
    os.makedirs(objects_dir, exist_ok=True)

    # Write commit object if it doesn't already exist
    if not os.path.exists(commit_path):
        with open(commit_path, "wb") as f:
            f.write(commit_bytes)
        print(f"Commit object written to: {commit_path}")


        with open(head_path, "w") as f:
            f.write(commit_hash)
        print(f"HEAD updated to: {commit_hash}")

        try:
            os.remove(index_path)
            print("Staging area cleared.")
        except Exception as e:
            print(f"Warning: Failed to clear staging area – {e}")

    else:
        print("Commit already exists in object store.")
