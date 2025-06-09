import os
import sys

class Repo:
    """
    Holds all of the .gitmini repository's goodies.
    Contains a method to initialize a new .gitmini repository.
    """

    def __init__(self, path=None):
        # If path is given, use it as repo root
        if path:
            self.root = path
        else:
            from gitmini.utils import find_gitmini_root
            self.root = find_gitmini_root()

        self.gitmini_dir = os.path.join(self.root, ".gitmini")
        self.objects_dir = os.path.join(self.gitmini_dir, "objects")
        self.index_file = os.path.join(self.gitmini_dir, "index")
        self.head_file = os.path.join(self.gitmini_dir, "HEAD")

    @staticmethod
    def init(path):
        """
        Set up a .gitmini/ repository with a default 'main' branch.
        Will fail if one already exists.
        """
        gitmini_dir = os.path.join(path, ".gitmini")
        if os.path.exists(gitmini_dir):
            print(f"fatal: reinitialized existing GitMini repository in {gitmini_dir}")
            sys.exit(1)

        # Setting up .gitmini folder structure
        os.makedirs(gitmini_dir)
        os.makedirs(os.path.join(gitmini_dir, "objects"))
        os.makedirs(os.path.join(gitmini_dir, "refs", "heads"))

        open(os.path.join(gitmini_dir, "index"), "w").close()

        # Immediately create "main" branch by default
        main_ref = os.path.join(gitmini_dir, "refs", "heads", "main")
        open(main_ref, "w").close()

        # Point HEAD to refs/heads/main
        with open(os.path.join(gitmini_dir, "HEAD"), "w") as f:
            f.write("ref: refs/heads/main")

        # Create default .gitmini-ignore at repo root
        ignore_path = os.path.join(path, ".gitmini-ignore")
        with open(ignore_path, "w") as f:
            f.write("# GitMini ignore file\n")
            f.write(".venv/\n")
            f.write("__pycache__/\n")
            f.write("*.pyc\n")


        print(f"Initialized empty GitMini repository in {gitmini_dir}")

