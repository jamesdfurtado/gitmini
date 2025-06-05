import os
from tests.test_helpers import GitMiniTestCase, GITMINI_DIR


class TestAddCommand1(GitMiniTestCase):


    def test_help(self):
        """ Test that 'gitmini add --help' shows help msg """

        result = self.run_gitmini(['add', '--help'])
        self.assertIn("usage: gitmini add", result.stdout)
        self.assertIn("Add specified files to GitMini's staging area for the next commit.", result.stdout)


    def test_without_repo(self):
        """ Test that 'gitmini add' fails when .gitmini is missing """

        result = self.run_gitmini(['add'])
        self.assertIn("fatal: not a gitmini repository", result.stderr)


    def test_with_repo(self):
        """ Test that 'gitmini add' finds .gitmini root """

        self.run_gitmini(['init'])
        result = self.run_gitmini(['add'])
        self.assertIn("Located .gitmini repo at:", result.stdout)


    def test_with_gitmini_in_parent_directory(self):
        """ Test that 'gitmini add' locates .gitmini in a parent directory """

        os.makedirs("nested/dir", exist_ok=True)
        self.run_gitmini(['init'])
        os.chdir("nested/dir")
        result = self.run_gitmini(['add'])
        self.assertIn("Located .gitmini repo at:", result.stdout)


    def test_from_inside_gitmini_directory(self):
        """ Test that 'gitmini add' can be run inside .gitmini directory """

        self.run_gitmini(['init'])
        os.chdir(".gitmini")
        result = self.run_gitmini(['add', '.'])
        self.assertIn("Located .gitmini repo at:", result.stdout)

        # Ensure no file in .gitmini was staged
        for line in result.stdout.splitlines():
            if line.startswith("Added "):
                self.assertNotIn(".gitmini", line)


