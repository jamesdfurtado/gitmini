import os
from tests.test_helpers import GitMiniTestCase, GITMINI_DIR

class TestAddCommand(GitMiniTestCase):

    def test_cli_add_without_repo(self):
        """ Test that 'gitmini add' fails when .gitmini is missing """
        result = self.run_gitmini(['add'])
        self.assertIn("fatal: not a gitmini repository", result.stderr)

    def test_cli_add_with_repo(self):
        """ Test that 'gitmini add' finds the .gitmini root and prints success message """
        self.run_gitmini(['init'])
        result = self.run_gitmini(['add'])
        self.assertIn("Located .gitmini repo at:", result.stdout)

    def test_cli_add_help(self):
        """ Test that 'gitmini add --help' displays the help message """
        result = self.run_gitmini(['add', '--help'])
        self.assertIn("usage: gitmini add", result.stdout)
        self.assertIn("Add specified files to GitMini's staging area for the next commit.", result.stdout)

    def test_cli_add_specific_file_and_folder(self):
        """ Test that 'gitmini add <file.txt> <folder>' collects the correct files """
        self.run_gitmini(['init'])
        result = self.run_gitmini(['add', 'file.txt', 'folder'])

        self.assertIn("file.txt", result.stdout)
        self.assertIn("folder\\infolder.txt", result.stdout)

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


