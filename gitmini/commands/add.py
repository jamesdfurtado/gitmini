import os
import sys
from gitmini.utils import find_gitmini_root
from gitmini.classes.Repo import Repo
from gitmini.classes.Blob import Blob
from gitmini.classes.Index import Index

def handle_add(args):
    """
    Stages newly added, changed, or deleted files.
    Just like git, can be used with <file>, <dir>, or "."
    """
    repo_root = find_gitmini_root()
    repo = Repo(repo_root)
    index = Index(repo)

    targets = args.targets
    if not targets:
        print("Nothing specified, nothing added.")
        sys.exit(1)

    # Files that could be possible be staged
    to_stage = []
    if len(targets) == 1 and targets[0] == ".":
        for root, dirs, files in os.walk(repo_root):
            if ".gitmini" in dirs:
                dirs.remove(".gitmini")
            for fname in files:
                rel = os.path.relpath(os.path.join(root, fname), repo_root)
                to_stage.append(rel)
    else:
        for t in targets:
            abs_t = os.path.join(repo_root, t)
            if os.path.isdir(abs_t):
                for root, dirs, files in os.walk(abs_t):
                    if ".gitmini" in dirs:
                        dirs.remove(".gitmini")
                    for fname in files:
                        rel = os.path.relpath(os.path.join(root, fname), repo_root)
                        to_stage.append(rel)
            elif os.path.isfile(abs_t):
                to_stage.append(os.path.relpath(abs_t, repo_root))
            else:
                print(f"warning: pathspec '{t}' did not match any files", file=sys.stderr)

    changed = False

    # Stage new or modified files
    for rel_path in to_stage:
        abs_path = os.path.join(repo_root, rel_path)
        if not os.path.isfile(abs_path):
            continue

        blob = Blob(repo, rel_path)
        sha1 = blob.sha1

        if index.entries.get(rel_path) == sha1:
            continue

        blob.write()
        index.add(rel_path, sha1)
        changed = True

    # Detect deletions (files in index that no longer exist on disk)
    tracked_paths = set(index.entries.keys())
    existing_paths = set(to_stage)

    for tracked_path in tracked_paths:
        full_path = os.path.join(repo_root, tracked_path)
        if not os.path.isfile(full_path):
            del index.entries[tracked_path]
#            print(f"deleted: {tracked_path}")  # optional message for tracking file deletions
            changed = True

    if not changed:
        print("nothing to add")
        sys.exit(0)


    index.write()
