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
