import os

class HEAD:
    """
    The HEAD points to the latest commit in the current branch.
    """

    def __init__(self, repo):
        self.repo = repo
        self.head_file = os.path.join(repo.gitmini_dir, "HEAD")
        self.value = None
        if os.path.exists(self.head_file):
            with open(self.head_file, "r") as f:
                content = f.read().strip()
            self.value = content if content else None

    def set(self, sha1):
        with open(self.head_file, "w") as f:
            f.write(sha1)
        self.value = sha1
