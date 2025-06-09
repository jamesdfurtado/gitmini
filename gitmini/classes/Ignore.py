import os

class Ignore:
    """ Responsible for handling .gitmini-ignore files. """

    def __init__(self, repo):
        self.repo = repo
        self.ignore_path = os.path.join(repo.root, ".gitmini-ignore")
        self.patterns = set()

        if os.path.exists(self.ignore_path):
            with open(self.ignore_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    self.patterns.add(line)

    def should_ignore(self, rel_path):
        # For now, only support exact match
        return rel_path in self.patterns
