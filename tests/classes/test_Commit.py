import os
import io
import contextlib

from gitmini.utils import compute_sha1
from gitmini.classes.Repo import Repo
from gitmini.classes.Index import Index
from gitmini.classes.Tree import Tree
from gitmini.classes.Commit import Commit
from gitmini.classes.HEAD import HEAD
from tests.test_helpers import GitMiniTestCase, GITMINI_DIR


class TestCommit(GitMiniTestCase):

    def test_commit_content_and_storage(self):
        """ Ensure all the metadata is logged when we create a Commit object."""

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            Repo.init(self.repo_dir)
        repo = Repo(self.repo_dir)

        # Create a mock index
        index = Index(repo)
        index.add("x.txt", "xxx000")
        index.write()

        # Manually create a tree SHA
        tree_hash = Tree(repo, index.entries).sha1

        # Set a fake HEAD
        head = HEAD(repo)
        head.set("parent123")

        # Write a commit
        msg = "Test commit"
        commit = Commit(repo, tree_hash, head.value, msg)
        sha = commit.write()

        object_path = os.path.join(repo.objects_dir, sha)
        self.assertTrue(os.path.exists(object_path))

        # Verify the content of the Commit object
        with open(object_path, "rb") as f:
            content = f.read().decode()

        self.assertIn(f"tree {tree_hash}", content)
        self.assertIn(f"parent {head.value}", content)
        self.assertIn(msg, content)
        self.assertEqual(sha, compute_sha1(content.encode()))
