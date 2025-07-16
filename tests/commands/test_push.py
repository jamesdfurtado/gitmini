import os
import json
import unittest
from unittest import mock
from tests.test_helpers import GitMiniTestCase, GITMINI_DIR
from gitmini.commands.push import handle_push

class TestPushCommand(GitMiniTestCase):
    def setUp(self):
        super().setUp()
        self.config_path = os.path.join(GITMINI_DIR, 'config.json')
        self.head_path = os.path.join(GITMINI_DIR, 'HEAD')
        self.heads_dir = os.path.join(GITMINI_DIR, 'refs', 'heads')
        os.makedirs(self.heads_dir, exist_ok=True)

    def _write_config(self, config):
        os.makedirs(GITMINI_DIR, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(config, f)

    def _write_head(self, ref):
        with open(self.head_path, 'w') as f:
            f.write(ref)

    def _write_branch(self, branch):
        with open(os.path.join(self.heads_dir, branch), 'w') as f:
            f.write('dummy commit hash')

    @mock.patch('gitmini.commands.push.httpx.post')
    def test_successful_push_with_explicit_branch(self, mock_post):
        """ Successful push with explicit branch argument. """
        self._write_config({'username': 'testuser', 'api_key': 'rawkey', 'repo': 'my-repo'})
        self._write_branch('main')
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'status': 'ok', 'message': 'Push successful'}
        class Args: branch = 'main:main'
        handle_push(Args())

    @mock.patch('gitmini.commands.push.httpx.post')
    def test_successful_push_with_default_branch(self, mock_post):
        """ Successful push with no branch argument uses current branch from HEAD. """
        self._write_config({'username': 'testuser', 'api_key': 'rawkey', 'repo': 'my-repo'})
        self._write_head('ref: refs/heads/dev')
        self._write_branch('dev')
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'status': 'ok', 'message': 'Push successful'}
        class Args: branch = None
        handle_push(Args())

    @mock.patch('gitmini.commands.push.httpx.post')
    def test_missing_config_json(self, mock_post):
        """ Missing config.json causes fatal error. """
        if os.path.exists(self.config_path):
            os.remove(self.config_path)
        class Args: branch = 'main:main'
        with self.assertRaises(SystemExit):
            handle_push(Args())

    @mock.patch('gitmini.commands.push.httpx.post')
    def test_missing_required_fields_in_config(self, mock_post):
        """ Missing username, api_key, or repo in config.json causes fatal error. """
        # Missing username
        self._write_config({'api_key': 'rawkey', 'repo': 'my-repo'})
        class Args: branch = 'main:main'
        with self.assertRaises(SystemExit):
            handle_push(Args())
        # Missing api_key
        self._write_config({'username': 'testuser', 'repo': 'my-repo'})
        with self.assertRaises(SystemExit):
            handle_push(Args())
        # Missing repo
        self._write_config({'username': 'testuser', 'api_key': 'rawkey'})
        with self.assertRaises(SystemExit):
            handle_push(Args())

    @mock.patch('gitmini.commands.push.httpx.post')
    def test_missing_head_file(self, mock_post):
        """ Missing HEAD file causes fatal error when no branch argument is given. """
        self._write_config({'username': 'testuser', 'api_key': 'rawkey', 'repo': 'my-repo'})
        if os.path.exists(self.head_path):
            os.remove(self.head_path)
        class Args: branch = None
        with self.assertRaises(SystemExit):
            handle_push(Args())

    @mock.patch('gitmini.commands.push.httpx.post')
    def test_detached_head(self, mock_post):
        """ Detached HEAD triggers fatal error. """
        self._write_config({'username': 'testuser', 'api_key': 'rawkey', 'repo': 'my-repo'})
        self._write_head('123456789abcdef')  # Not a ref
        class Args: branch = None
        with self.assertRaises(SystemExit):
            handle_push(Args())

    @mock.patch('gitmini.commands.push.httpx.post')
    def test_missing_local_branch(self, mock_post):
        """ Local branch file missing triggers fatal error. """
        self._write_config({'username': 'testuser', 'api_key': 'rawkey', 'repo': 'my-repo'})
        self._write_head('ref: refs/heads/main')
        # Do NOT create refs/heads/main
        class Args: branch = None
        with self.assertRaises(SystemExit):
            handle_push(Args())

    @mock.patch('gitmini.commands.push.httpx.post')
    def test_server_auth_error(self, mock_post):
        """ Server returns authentication error. """
        self._write_config({'username': 'testuser', 'api_key': 'rawkey', 'repo': 'my-repo'})
        self._write_head('ref: refs/heads/main')
        self._write_branch('main')
        mock_post.return_value.status_code = 401
        mock_post.return_value.json.return_value = {'status': 'error', 'message': 'Authentication failed'}
        class Args: branch = None
        with self.assertRaises(SystemExit):
            handle_push(Args())

    @mock.patch('gitmini.commands.push.httpx.post')
    def test_server_repo_not_found(self, mock_post):
        """ Server returns repo not found or access denied. """
        self._write_config({'username': 'testuser', 'api_key': 'rawkey', 'repo': 'my-repo'})
        self._write_head('ref: refs/heads/main')
        self._write_branch('main')
        mock_post.return_value.status_code = 404
        mock_post.return_value.json.return_value = {'status': 'error', 'message': 'Repository not found or access denied'}
        class Args: branch = None
        with self.assertRaises(SystemExit):
            handle_push(Args())

    @mock.patch('gitmini.commands.push.httpx.post')
    def test_server_branch_not_found(self, mock_post):
        """ Server returns branch not found. """
        self._write_config({'username': 'testuser', 'api_key': 'rawkey', 'repo': 'my-repo'})
        self._write_head('ref: refs/heads/main')
        self._write_branch('main')
        mock_post.return_value.status_code = 404
        mock_post.return_value.json.return_value = {'status': 'error', 'message': 'Remote branch not found.'}
        class Args: branch = None
        with self.assertRaises(SystemExit):
            handle_push(Args())

    @mock.patch('gitmini.commands.push.httpx.post')
    def test_server_malformed_payload(self, mock_post):
        """ Server returns malformed payload error. """
        self._write_config({'username': 'testuser', 'api_key': 'rawkey', 'repo': 'my-repo'})
        self._write_head('ref: refs/heads/main')
        self._write_branch('main')
        mock_post.return_value.status_code = 422
        mock_post.return_value.json.return_value = {'detail': [{'msg': 'field required', 'loc': ['body', 'branch']}]}
        class Args: branch = None
        with self.assertRaises(SystemExit):
            handle_push(Args())

    @mock.patch('gitmini.commands.push.httpx.post')
    def test_push_colon_remote_only(self, mock_post):
        """ gitmini push :remote uses current branch as local, checks existence. """
        self._write_config({'username': 'testuser', 'api_key': 'rawkey', 'repo': 'my-repo'})
        self._write_head('ref: refs/heads/main')
        self._write_branch('main')
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'status': 'ok', 'message': 'Push successful'}
        class Args: branch = ':remote'
        handle_push(Args())

    @mock.patch('gitmini.commands.push.httpx.post')
    def test_push_non_current_local_branch(self, mock_post):
        """ Pushes a local branch that is not HEAD, checks existence. """
        self._write_config({'username': 'testuser', 'api_key': 'rawkey', 'repo': 'my-repo'})
        self._write_head('ref: refs/heads/main')
        self._write_branch('feature')
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'status': 'ok', 'message': 'Push successful'}
        class Args: branch = 'feature:main'
        handle_push(Args())
