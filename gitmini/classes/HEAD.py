import os

class HEAD:
    """
    Manages HEAD pointer: either a symbolic ref (e.g., 'ref: refs/heads/main')
    or a raw commit hash (detached).
    """

    def __init__(self, repo):
        self.repo = repo
        self.head_file = os.path.join(repo.gitmini_dir, "HEAD")
        self.value = None
        if os.path.exists(self.head_file):
            with open(self.head_file, "r") as f:
                raw = f.read().strip()
            self.value = raw or None

    def is_detached(self):
        return not self.value or not self.value.startswith("ref: ")

    def get_ref(self):
        # e.g. returns "refs/heads/main" or None
        if self.value and self.value.startswith("ref: "):
            return self.value.split(" ", 1)[1]
        return None

    def get_commit(self):
        # resolve symbolic ref → commit hash, or return raw hash
        ref = self.get_ref()
        if ref:
            ref_path = os.path.join(self.repo.gitmini_dir, ref)
            return open(ref_path, "r").read().strip()
        return self.value

    def set_ref(self, branch):
        # switch HEAD to point at a branch
        content = f"ref: refs/heads/{branch}"
        with open(self.head_file, "w") as f:
            f.write(content)
        self.value = content

    def set_commit(self, sha1):
        # detach HEAD to a specific commit
        with open(self.head_file, "w") as f:
            f.write(sha1)
        self.value = sha1

    def update(self, sha1):
        # update the branch pointer that HEAD refers to
        ref = self.get_ref()
        if not ref:
            raise RuntimeError("Cannot update branch in detached HEAD state")
        ref_path = os.path.join(self.repo.gitmini_dir, ref)
        with open(ref_path, "w") as f:
            f.write(sha1)
