import os
from tests.test_helpers import GitMiniTestCase, GITMINI_DIR


class TestAddCommand3(GitMiniTestCase):


    def test_blob_created_for_added_file(self):
        """ Test that 'gitmini add <file>' creates a blob in .gitmini/objects/ """
        self.run_gitmini(['init'])

        # Write file with known contents
        content = b"Blob me up, Scotty."
        file_path = os.path.join(os.getcwd(), "blobfile.txt")
        with open(file_path, "wb") as f:
            f.write(content)


        # Dynamically compute expected hash
        from gitmini.utils import compute_sha1
        expected_hash = compute_sha1(content)

        self.run_gitmini(['add', 'blobfile.txt'])

        blob_path = os.path.join(GITMINI_DIR, "objects", expected_hash)
        self.assertTrue(os.path.exists(blob_path))

        # Confirm contents match
        with open(blob_path, "rb") as f:
            blob_data = f.read()
        self.assertEqual(blob_data, content)


    def test_blob_idempotent_on_readd(self):
        """ Test that re-adding the same file does not duplicate or modify the blob """
        self.run_gitmini(['init'])

        content = b"Blobbed once."
        file_path = os.path.join(os.getcwd(), "repeat.txt")
        with open(file_path, "wb") as f:
            f.write(content)

        from gitmini.utils import compute_sha1
        expected_hash = compute_sha1(content)
        blob_path = os.path.join(GITMINI_DIR, "objects", expected_hash)

        self.run_gitmini(['add', 'repeat.txt'])

        # Record timestamp before re-adding
        mtime_before = os.path.getmtime(blob_path)

        self.run_gitmini(['add', 'repeat.txt'])

        # Confirm blob still exists and timestamp unchanged (i.e., not rewritten)
        self.assertTrue(os.path.exists(blob_path))
        mtime_after = os.path.getmtime(blob_path)
        self.assertEqual(mtime_before, mtime_after)


    def test_blob_add_existing_blob_from_another_file(self):
        """ Test that adding a different file with identical content reuses the same blob """
        self.run_gitmini(['init'])

        content = b"Shared content."
        file_a = "a.txt"
        file_b = "b.txt"
        with open(file_a, "wb") as f:
            f.write(content)
        with open(file_b, "wb") as f:
            f.write(content)

        from gitmini.utils import compute_sha1
        expected_hash = compute_sha1(content)
        blob_path = os.path.join(GITMINI_DIR, "objects", expected_hash)

        self.run_gitmini(['add', file_a])
        self.assertTrue(os.path.exists(blob_path))

        # Confirm re-adding identical content under different path doesn't rewrite blob
        mtime_before = os.path.getmtime(blob_path)
        self.run_gitmini(['add', file_b])
        mtime_after = os.path.getmtime(blob_path)
        self.assertEqual(mtime_before, mtime_after)


    def test_blob_error_on_unreadable_file(self):
        """ Test that adding a file that is removed or unreadable mid-process reports error cleanly """
        self.run_gitmini(['init'])

        file_path = "ghost.txt"
        with open(file_path, "w") as f:
            f.write("will vanish")

        # Delete before add
        os.remove(file_path)

        result = self.run_gitmini(['add', file_path])
        self.assertIn("Warning: 'ghost.txt' is not a valid file or directory. Skipping.", result.stdout)
