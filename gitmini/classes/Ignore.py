import os
import fnmatch

class Ignore:
    """ Responsible for handling .gitmini-ignore files (mimics .gitignore behavior). """

    def __init__(self, repo):
        self.repo = repo
        self.ignore_path = os.path.join(repo.root, ".gitmini-ignore")
        self.patterns = []

        if os.path.exists(self.ignore_path):
            with open(self.ignore_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    self.patterns.append(line)

    def should_ignore(self, rel_path):
        rel_path = rel_path.replace(os.sep, "/")  # Normalize for pattern matching
        for pattern in self.patterns:
            # Handle folder ignores
            if pattern.endswith("/"):
                if rel_path.startswith(pattern):
                    return True
                
            # Handle filetypes or specific files
            if fnmatch.fnmatch(rel_path, pattern):
                return True
            # Specific filename catches in subdirectories
            # Ex: (secrets.txt would catch a/b/secrets.txt)
            if fnmatch.fnmatch(os.path.basename(rel_path), pattern):
                return True
        return False
