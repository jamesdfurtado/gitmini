import os
import shutil
import subprocess
from tests.test_helpers import GitMiniTestCase, GITMINI_DIR


class TestInitCommand(GitMiniTestCase):

    def test_cli_init_stub(self):
        """ Test that 'gitmini init' initializes the correct folder structure and prints confirmation """
        result = subprocess.run(
            ['python', '-m', 'gitmini', 'init'],
            capture_output=True,
            text=True
        )
        self.assertIn("Initialized empty GitMini repository in .gitmini/", result.stdout)
        self.assertTrue(os.path.isdir(GITMINI_DIR))
        self.assertTrue(os.path.isdir(os.path.join(GITMINI_DIR, 'objects')))
        self.assertTrue(os.path.isdir(os.path.join(GITMINI_DIR, 'logs')))
        self.assertTrue(os.path.isfile(os.path.join(GITMINI_DIR, 'index')))

    def test_cli_init_already_initialized(self):
        """ Test that 'gitmini init' does not reinitialize an existing repository """

        subprocess.run(['python', '-m', 'gitmini', 'init'], capture_output=True, text=True)
        result = subprocess.run(
            ['python', '-m', 'gitmini', 'init'],
            capture_output=True,
            text=True
        )
        self.assertIn("GitMini repository already initialized.", result.stdout)

    def test_cli_init_help(self):
        """ Test that 'gitmini init --help' displays the help message """

        result = subprocess.run(
            ['python', '-m', 'gitmini', 'init', '--help'],
            capture_output=True,
            text=True
        )
        self.assertIn("usage: gitmini init", result.stdout)
        self.assertIn("Initialize a new GitMini repository in the current directory.", result.stdout)
