import os
import sys
from gitmini.utils import find_gitmini_root
from gitmini.classes.Repo import Repo
from gitmini.classes.Blob import Blob
from gitmini.classes.Index import Index
from gitmini.classes.Ignore import Ignore

def handle_add(args):
    """
    Stages newly added, changed, or deleted files.
    Just like git, can be used with <file>, <dir>, or "."
    """
    repo_root = find_gitmini_root()
    repo = Repo(repo_root)
    ignore = Ignore(repo)
    index = Index(repo)

    targets = args.targets
    if not targets:
        print("Nothing specified, nothing added.")
        sys.exit(1)

    # Add all changed files with 'gitmini add .'
    to_stage = []
    for t in targets:
        abs_t = os.path.abspath(t if os.path.isabs(t) else os.path.join(os.getcwd(), t))

        if not is_within_repo(repo_root, abs_t):
            print(f"fatal: path '{t}' is outside repository", file=sys.stderr)
            continue

        if os.path.isdir(abs_t):
            for root, dirs, files in os.walk(abs_t):
                if ".gitmini" in dirs:
                    dirs.remove(".gitmini")
                for fname in files:
                    abs_file = os.path.join(root, fname)
                    if not is_within_repo(repo_root, abs_file):
                        continue
                    rel = os.path.relpath(abs_file, repo_root)
                    if rel.startswith(".gitmini" + os.sep) or rel == ".gitmini":
                        continue
                    if ignore.should_ignore(rel):
                        continue
                    to_stage.append(rel)
        elif os.path.isfile(abs_t):
            rel = os.path.relpath(abs_t, repo_root)
            if rel.startswith(".gitmini" + os.sep) or rel == ".gitmini":
                continue
            if ignore.should_ignore(rel):
                continue
            to_stage.append(rel)
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


# Patch to ensure users cannot add files outside the repository
def is_within_repo(repo_root, abs_path):
    abs_repo_root = os.path.abspath(repo_root)
    abs_target = os.path.abspath(abs_path)
    return os.path.commonpath([abs_repo_root]) == os.path.commonpath([abs_repo_root, abs_target])
