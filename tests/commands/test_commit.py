import os
from tests.test_helpers import GitMiniTestCase, GITMINI_DIR


class TestCommit(GitMiniTestCase):

    def test_help(self):
        """ 'gitmini commit --help' prints help msg. """
        result = self.run_gitmini(['commit', '--help'])
        self.assertIn('usage: gitmini commit', result.stdout)

    def test_without_repo_errors(self):
        """ Test that commit fails without .gitmini/ """
        result = self.run_gitmini(['commit', '-m', 'msg'])
        self.assertIn('fatal: not a gitmini repository', result.stderr)

    def test_commit_creates_object_and_updates_HEAD(self):
        """ Ensure committing updates HEAD correctly."""
        self.run_gitmini(['init'])

        with open('f.txt', 'wb') as f:
            f.write(b'X')
        self.run_gitmini(['add', 'f.txt'])

        result = self.run_gitmini(['commit', '-m', 'my commit'])
        self.assertIn('Commit object written to:', result.stdout)

        commit_path = result.stdout.strip().split(':')[-1].strip()
        self.assertTrue(os.path.exists(commit_path))

        with open(os.path.join(self.repo_dir, GITMINI_DIR, 'HEAD'), 'r') as f:
            head_val = f.read().strip()
        self.assertEqual(len(head_val), 40)
