import os
import io
import contextlib

from gitmini_core.classes.Repo import Repo
from gitmini_core.classes.Tree import Tree
from tests.test_helpers import GitMiniTestCase


class TestTree(GitMiniTestCase):

    def test_tree_generates_and_stores_content(self):
        """ Tree.write should save a snapshot of the index to objects/. """
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            Repo.init(self.repo_dir)
        repo = Repo(self.repo_dir)
        objects_dir = repo.objects_dir

        entries = {"aaa111": "a.txt", "bbb222": "b.txt"}
        tree = Tree(repo, entries)
        tree.write()

        self.assertRegex(tree.sha1, r"^[0-9a-f]{40}$")

        object_path = os.path.join(objects_dir, tree.sha1)
        self.assertTrue(os.path.exists(object_path))

        with open(object_path, "rb") as f:
            data = f.read().decode()
        for path, sha in entries.items():
            self.assertIn(f"{sha} {path}", data)
