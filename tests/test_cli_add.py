import os
import shutil
import subprocess
from tests.test_helpers import GitMiniTestCase, GITMINI_DIR


class TestAddCommand(GitMiniTestCase):

    def test_cli_add_without_repo(self):
        """ Test that 'gitmini add' fails when .gitmini is missing """
        result = subprocess.run(
            ['python', '-m', 'gitmini', 'add'],
            capture_output=True,
            text=True
        )
        self.assertIn("fatal: not a gitmini repository", result.stderr)

    def test_cli_add_with_repo(self):
        """ Test that 'gitmini add' finds the .gitmini root and prints success message """
        subprocess.run(['python', '-m', 'gitmini', 'init'], capture_output=True, text=True)

        result = subprocess.run(
            ['python', '-m', 'gitmini', 'add'],
            capture_output=True,
            text=True
        )
        self.assertIn("Located .gitmini repo at:", result.stdout)

    def test_cli_add_help(self):
        """ Test that 'gitmini add --help' displays the help message """
        result = subprocess.run(
            ['python', '-m', 'gitmini', 'add', '--help'],
            capture_output=True,
            text=True
        )
        self.assertIn("usage: gitmini add", result.stdout)
        self.assertIn("Add specified files to GitMini's staging area for the next commit.", result.stdout)
