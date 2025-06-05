import os
from tests.test_helpers import GitMiniTestCase, GITMINI_DIR


class TestAddCommand2(GitMiniTestCase):


    def test_add_file_and_folder(self):
        """ Test that 'gitmini add <file.txt> <folder>' collects correct files """

        self.run_gitmini(['init'])
        result = self.run_gitmini(['add', 'file.txt', 'folder'])

        self.assertIn("file.txt", result.stdout)
        self.assertIn("folder\\infolder.txt", result.stdout)


    def test_dot(self):
        """ Test that 'gitmini add .' collects all files (besides .gitmini ones) """

        self.run_gitmini(['init'])
        result = self.run_gitmini(['add', '.'])

        self.assertIn("file.txt", result.stdout)
        self.assertIn("folder\\infolder.txt", result.stdout)

        # Ensure no staged file is in .gitmini
        for line in result.stdout.splitlines():
            if line.startswith("Added "):
                self.assertNotIn(".gitmini", line)


    def test_nonexistent_target(self):
        """ Test that 'gitmini add nonexistent.txt' shows a warning and doesnt crash """

        self.run_gitmini(['init'])
        result = self.run_gitmini(['add', 'nonexistent.txt'])
        self.assertIn("Warning: 'nonexistent.txt' is not a valid file or directory", result.stdout)


    def test_gitmini_files_excluded(self):
        """ Test that files inside .gitmini are not staged """

        self.run_gitmini(['init'])

        os.makedirs(os.path.join(GITMINI_DIR, "logs"), exist_ok=True)
        log_file_path = os.path.join(GITMINI_DIR, "logs", "event.log")
        with open(log_file_path, "w") as f:
            f.write("should not be added")

        result = self.run_gitmini(['add', '.'])

        # Ensure no staged file is inside .gitmini
        for line in result.stdout.splitlines():
            if line.startswith("Added "):
                self.assertNotIn(".gitmini", line)
                self.assertNotIn("event.log", line)


    def test_directory_only(self):
        """ Test that 'gitmini add folder/' adds all files within it """

        self.run_gitmini(['init'])
        result = self.run_gitmini(['add', 'folder'])
        self.assertIn("folder\\infolder.txt", result.stdout)


    def test_nested_files(self):
        """ Test that 'gitmini add nested/' includes deeply nested files """
        self.run_gitmini(['init'])
        result = self.run_gitmini(['add', 'nested'])

        self.assertIn("nested\\inner\\testfile.txt", result.stdout)


    def test_file_order(self):
        """ Test that 'gitmini add .' outputs files in consistent sorted order and handles skips """
        self.run_gitmini(['init'])

        result1 = self.run_gitmini(['add', '.'])
        result2 = self.run_gitmini(['add', '.'])

        added1 = sorted([line for line in result1.stdout.splitlines() if line.startswith("Added ")])
        skipped2 = sorted([line for line in result2.stdout.splitlines() if line.startswith("Skipped ")])

        paths1 = [line.split(" ", 1)[1] for line in added1]
        paths2 = [line.split(" ", 1)[1].rsplit(" ", 1)[0] for line in skipped2]

        self.assertEqual(paths1, paths2)

