import os
from tests.test_helpers import GitMiniTestCase, GITMINI_DIR


class TestAddCommand4(GitMiniTestCase):


    def test_index_adds_new_file(self):
        """ Test that staged file is added to index w/ correct hash """

        self.run_gitmini(['init'])

        content = b"new content"
        file_path = "new.txt"
        with open(file_path, "wb") as f:
            f.write(content)

        from gitmini.utils import compute_sha1
        expected_hash = compute_sha1(content)

        self.run_gitmini(['add', file_path])

        index_path = os.path.join(GITMINI_DIR, "index")
        with open(index_path, "r") as f:
            index_lines = f.readlines()

        self.assertIn(f"{expected_hash} new.txt\n", index_lines)


    def test_index_skips_unchanged_file(self):
        """ Test that re-adding unchanged file doesn't touch index """

        self.run_gitmini(['init'])

        content = b"unchanged content"
        file_path = "unchanged.txt"
        with open(file_path, "wb") as f:
            f.write(content)

        self.run_gitmini(['add', file_path])

        index_path = os.path.join(GITMINI_DIR, "index")
        with open(index_path, "r") as f:
            index_lines_before = f.readlines()

        self.run_gitmini(['add', file_path])

        with open(index_path, "r") as f:
            index_lines_after = f.readlines()

        # Index content should remain identical
        self.assertEqual(index_lines_before, index_lines_after)


    def test_index_updates_modified_file(self):
        """ Test that changing a file updates its index entry """

        self.run_gitmini(['init'])

        file_path = "mod.txt"
        with open(file_path, "wb") as f:
            f.write(b"version 1")

        self.run_gitmini(['add', file_path])

        with open(file_path, "wb") as f:
            f.write(b"version 2")

        from gitmini.utils import compute_sha1
        expected_hash = compute_sha1(b"version 2")

        self.run_gitmini(['add', file_path])

        index_path = os.path.join(GITMINI_DIR, "index")
        with open(index_path, "r") as f:
            index_lines = f.readlines()

        self.assertIn(f"{expected_hash} mod.txt\n", index_lines)

    def test_index_handles_multiple_mixed_files(self):
        """ Test add with multiple files (some new, some changed, some unchanged) """

        self.run_gitmini(['init'])

        with open("a.txt", "wb") as f:
            f.write(b"keep")

        with open("b.txt", "wb") as f:
            f.write(b"change")

        self.run_gitmini(['add', 'a.txt', 'b.txt'])

        with open("b.txt", "wb") as f:
            f.write(b"changed")

        with open("c.txt", "wb") as f:
            f.write(b"new")

        result = self.run_gitmini(['add', 'a.txt', 'b.txt', 'c.txt'])

        self.assertIn("Skipped a.txt (unchanged)", result.stdout)
        self.assertIn("Added b.txt", result.stdout)
        self.assertIn("Added c.txt", result.stdout)

        index_path = os.path.join(GITMINI_DIR, "index")
        with open(index_path, "r") as f:
            lines = f.read()

        self.assertIn("a.txt", lines)
        self.assertIn("b.txt", lines)
        self.assertIn("c.txt", lines)


    def test_index_ignores_malformed_entries(self):
        """ Throw random lines into index to ensure proper cleanup """

        self.run_gitmini(['init'])

        index_path = os.path.join(GITMINI_DIR, "index")
        with open(index_path, "w") as f:
            f.write("badlinewithoutspace\n")

        with open("clean.txt", "wb") as f:
            f.write(b"clean")

        result = self.run_gitmini(['add', 'clean.txt'])

        self.assertIn("Added clean.txt", result.stdout)

        # Confirm that clean.txt is still added despite malformed line
        with open(index_path, "r") as f:
            lines = f.read()
        self.assertIn("clean.txt", lines)


    def test_index_empty_file_is_valid(self):
        """ Test that empty index file does not crash """

        self.run_gitmini(['init'])

        index_path = os.path.join(GITMINI_DIR, "index")
        with open(index_path, "w") as f:
            pass  # Create empty file

        with open("emptycase.txt", "wb") as f:
            f.write(b"some data")

        result = self.run_gitmini(['add', 'emptycase.txt'])

        self.assertIn("Added emptycase.txt", result.stdout)

        with open(index_path, "r") as f:
            contents = f.read()
        self.assertIn("emptycase.txt", contents)


    def test_relative_and_absolute_paths_resolve_same(self):
        """ Ensure adding relative and absolute paths do not duplicate entries """

        self.run_gitmini(['init'])

        file_path = "samefile.txt"
        with open(file_path, "wb") as f:
            f.write(b"same content")

        abs_path = os.path.abspath(file_path)

        self.run_gitmini(['add', file_path])
        self.run_gitmini(['add', abs_path])  # Should be treated the same

        index_path = os.path.join(GITMINI_DIR, "index")
        with open(index_path, "r") as f:
            lines = f.readlines()

        matches = [line for line in lines if "samefile.txt" in line]
        self.assertEqual(len(matches), 1)
