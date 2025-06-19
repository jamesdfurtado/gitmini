import os
from gitmini_core.utils import find_gitmini_root
from gitmini_core.classes.Repo import Repo
from gitmini_core.classes.HEAD import HEAD

def handle_log(args):
    """ Show commit history for the current branch. """
    repo_root = find_gitmini_root()
    repo = Repo(repo_root)
    head = HEAD(repo)

    commit_hash = head.get_commit()

    if not commit_hash:
        print("fatal: branch has no commits yet")
        return

    while commit_hash:
        obj_path = os.path.join(repo.objects_dir, commit_hash)
        if not os.path.exists(obj_path):
            print(f"error: commit object {commit_hash} not found")
            break

        with open(obj_path, "rb") as f:
            lines = f.read().decode(errors="ignore").splitlines()

        tree = parent = timestamp = message = ""
        reading_msg = False
        msg_lines = []

        for line in lines:
            if line.startswith("tree "):
                tree = line.split(" ", 1)[1]
            elif line.startswith("parent "):
                parent = line.split(" ", 1)[1]
            elif line.startswith("timestamp "):
                timestamp = line[len("timestamp "):]
            elif line.strip() == "":
                reading_msg = True
            elif reading_msg:
                msg_lines.append(line)

        message = "\n".join(msg_lines).strip()

        print("")
        print(f"commit {commit_hash}")
        if timestamp:
            print(f"Date:   {timestamp}")
        if message:
            print(f"\n    {message}")
        print()

        commit_hash = parent if parent else None
