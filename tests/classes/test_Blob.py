import os
import io
import contextlib

from gitmini_core.utils import compute_sha1
from gitmini_core.classes.Blob import Blob
from gitmini_core.classes.Repo import Repo
from tests.test_helpers import GitMiniTestCase


class TestBlob(GitMiniTestCase):

    def test_sha1_is_computed_correctly(self):
        """ Test that the hashing is working correctly."""
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            Repo.init(self.repo_dir)
        repo = Repo(self.repo_dir)

        file_name = "sample.txt"
        content = b"Hello, GitMini Blob!"
        with open(file_name, "wb") as f:
            f.write(content)

        blob = Blob(repo, file_name)
        expected = compute_sha1(content)
        self.assertEqual(blob.sha1, expected)

    def test_write_creates_object_file(self):
        """Test that Blob.write() writes under objects/<sha1>."""
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            Repo.init(self.repo_dir)
        repo = Repo(self.repo_dir)

        file_name = "sample.txt"
        content = b"Hello, GitMini Blob!"
        with open(file_name, "wb") as f:
            f.write(content)

        blob = Blob(repo, file_name)
        object_path = os.path.join(repo.objects_dir, blob.sha1)

        self.assertFalse(os.path.exists(object_path))  # should not exist
        blob.write()
        self.assertTrue(os.path.exists(object_path))  # should now exist
        with open(object_path, "rb") as f:
            stored = f.read()
        self.assertEqual(stored, content)
