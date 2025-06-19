import os
from gitmini_core.utils import compute_sha1
from tests.test_helpers import GitMiniTestCase, GITMINI_DIR


class TestAdd(GitMiniTestCase):

    def setUp(self):
        super().setUp()
        self.run_gitmini(['init'])

    def test_help(self):
        """ Test that 'gitmini add --help'  print usage info. """
        result = self.run_gitmini(['add', '--help'])
        self.assertIn('usage: gitmini add', result.stdout)

    def test_add_single_file_creates_blob_and_index(self):
        """ Ensure that blob is created and index is updated appropriately. """
        filename = 'file.txt'
        content = b'hello world'
        with open(filename, 'wb') as f:
            f.write(content)

        self.run_gitmini(['add', filename])

        expected_hash = compute_sha1(content)
        blob_path = os.path.join(GITMINI_DIR, 'objects', expected_hash)
        self.assertTrue(os.path.exists(blob_path))

        with open(os.path.join(GITMINI_DIR, 'index'), 'r') as f:
            index_content = f.read()
        self.assertIn(f'{expected_hash} {filename}', index_content)

    def test_add_dot_stages_all_files(self):
        """ Adding '.' stages all files in CWD """
        with open('a.txt', 'w') as f:
            f.write('A')
        with open('b.txt', 'w') as f:
            f.write('B')
        os.makedirs('sub', exist_ok=True)
        with open('sub/c.txt', 'w') as f:
            f.write('C')

        self.run_gitmini(['add', '.'])

        with open(os.path.join(GITMINI_DIR, 'index'), 'r') as f:
            lines = f.read().splitlines()

        indexed_paths = [line.split(" ", 1)[1] for line in lines]

        self.assertIn('a.txt', indexed_paths)
        self.assertIn('b.txt', indexed_paths)
        self.assertIn(os.path.normpath('sub/c.txt'), map(os.path.normpath, indexed_paths))
        self.assertTrue(all('.gitmini' not in path for path in indexed_paths if path != '.gitmini-ignore'))

    def test_add_from_subdirectory_with_dot(self):
        """ Ensure that running 'gitmini add .' from subdirectory adds only CWD and nested files. """
        os.makedirs('nested/inner', exist_ok=True)
        with open('nested/file1.txt', 'w') as f:
            f.write('one')
        with open('nested/inner/file2.txt', 'w') as f:
            f.write('two')

        os.chdir('nested')
        self.run_gitmini(['add', '.'])
        os.chdir('..')

        with open(os.path.join(GITMINI_DIR, 'index'), 'r') as f:
            lines = f.read().splitlines()
        paths = [line.split(" ", 1)[1] for line in lines]

        self.assertIn(os.path.normpath('nested/file1.txt'), map(os.path.normpath, paths))
        self.assertIn(os.path.normpath('nested/inner/file2.txt'), map(os.path.normpath, paths))


    def test_gitmini_dir_is_not_staged(self):
        """ Check that nothing .gitmini/ related is staged """
        os.makedirs(os.path.join(GITMINI_DIR, 'internal'), exist_ok=True)
        with open(os.path.join(GITMINI_DIR, 'internal', 'temp.txt'), 'w') as f:
            f.write('secret')

        self.run_gitmini(['add', '.'])

        with open(os.path.join(GITMINI_DIR, 'index'), 'r') as f:
            index_data = f.read()

        self.assertNotIn('internal/temp.txt', index_data)

    def test_gitmini_ignore_excludes_files(self):
        """ Check that .gitmini-ignore works """
        with open('.gitmini-ignore', 'w') as f:
            f.write('ignored.txt\n*.log')

        with open('ignored.txt', 'w') as f:
            f.write('skip me')
        with open('include.txt', 'w') as f:
            f.write('include me')
        with open('debug.log', 'w') as f:
            f.write('nope')

        self.run_gitmini(['add', '.'])

        with open(os.path.join(GITMINI_DIR, 'index'), 'r') as f:
            staged = f.read()

        self.assertIn('include.txt', staged)
        self.assertNotIn('ignored.txt', staged)
        self.assertNotIn('debug.log', staged)

    def test_adding_same_file_twice_does_not_duplicate(self):
        """ Adding the same file twice shouldn't create duplicate index entries. """
        with open('dup.txt', 'w') as f:
            f.write('dupe')

        self.run_gitmini(['add', 'dup.txt'])
        self.run_gitmini(['add', 'dup.txt'])

        with open(os.path.join(GITMINI_DIR, 'index'), 'r') as f:
            lines = f.read().splitlines()

        matches = [line for line in lines if 'dup.txt' in line]
        self.assertEqual(len(matches), 1)

    def test_add_nonexistent_file_fails(self):
        """ Adding a nonexistent file should throw an error message but not crash. """
        result = self.run_gitmini(['add', 'nope.txt'])
        self.assertEqual(result.returncode, 0)
        self.assertIn("did not match any files", result.stderr.lower())

        with open(os.path.join(GITMINI_DIR, 'index'), 'r') as f:
            index_data = f.read()
        self.assertNotIn('nope.txt', index_data)

