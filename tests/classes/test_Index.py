import os
import io
import contextlib

from gitmini.classes.Repo import Repo
from gitmini.classes.Index import Index
from tests.test_helpers import GitMiniTestCase, GITMINI_DIR


class TestIndex(GitMiniTestCase):

    def test_add_and_write_entries(self):
        """ Index should save staged file to hash pairs into index file """
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            Repo.init(self.repo_dir)
        repo = Repo(self.repo_dir)
        index = Index(repo)

        index.add("foo.txt", "abc123")
        index.add("bar.txt", "def456")
        index.write()

        index_file = os.path.join(repo.gitmini_dir, "index")
        with open(index_file, "r") as f:
            lines = f.read().splitlines()
        self.assertIn("abc123 foo.txt", lines)
        self.assertIn("def456 bar.txt", lines)

    def test_init_loads_existing(self):
        """ Test that init loads existing index entries """
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            Repo.init(self.repo_dir)
        repo = Repo(self.repo_dir)
        index_file = os.path.join(repo.gitmini_dir, "index")

        with open("one.txt", "w"): pass
        with open("two.txt", "w"): pass
        with open(index_file, "w") as f:
            f.write("aaa111 one.txt\n")
            f.write("bbb222 two.txt\n")

        index = Index(repo)
        self.assertEqual(index.entries.get("one.txt"), "aaa111")
        self.assertEqual(index.entries.get("two.txt"), "bbb222")
