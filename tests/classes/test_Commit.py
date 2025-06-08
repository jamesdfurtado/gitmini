import os
import unittest
from gitmini.classes.Commit import Commit
from gitmini.classes.Repo import Repo
from gitmini.classes.HEAD import HEAD
from gitmini.classes.Index import Index
from gitmini.classes.Tree import Tree
from gitmini.utils import compute_sha1
from tests.test_helpers import GitMiniTestCase


class TestCommit(GitMiniTestCase):
    """ Ensure all the metadata is logged when we create a Commit object. """

    def test_commit_content_and_storage(self):
        self.run_gitmini(['init'])
        self.repo = Repo(self.repo_dir)

        file_path = os.path.join(self.repo_dir, "test.txt")
        with open(file_path, "w") as f:
            f.write("Hello, commit")

        self.run_gitmini(["add", "."])
        self.run_gitmini(["commit", "-m", "Commit test"])

        head = HEAD(self.repo)
        commit_hash = head.get_commit()

        self.assertIsNotNone(commit_hash)
        obj_path = os.path.join(self.repo.objects_dir, commit_hash)
        self.assertTrue(os.path.exists(obj_path))

        with open(obj_path, "rb") as f:
            contents = f.read().decode()
        self.assertIn("tree", contents)
        self.assertIn("timestamp", contents)
        self.assertIn("Commit test", contents)
