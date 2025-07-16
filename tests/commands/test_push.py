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

    @mock.patch('gitmini.commands.push.httpx.post')
    def test_successful_push_with_explicit_branch(self, mock_post):
        """ Successful push with explicit branch argument. """

        os.makedirs(GITMINI_DIR, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump({'username': 'testuser', 'api_key': 'rawkey', 'repo': 'my-repo'}, f)
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            'status': 'ok',
            'message': 'Push successful'
        }
        class Args: branch = 'main:main'
        handle_push(Args())

    @mock.patch('gitmini.commands.push.httpx.post')
    def test_successful_push_with_default_branch(self, mock_post):
        """ Successful push with no branch argument uses current branch from HEAD. """

        os.makedirs(GITMINI_DIR, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump({'username': 'testuser', 'api_key': 'rawkey', 'repo': 'my-repo'}, f)
        with open(self.head_path, 'w') as f:
            f.write('ref: refs/heads/dev')
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            'status': 'ok',
            'message': 'Push successful'
        }
        class Args: branch = None
        handle_push(Args())

    @mock.patch('gitmini.commands.push.httpx.post')
    def test_error_response(self, mock_post):
        """ Error response from server causes fatal error. """

        os.makedirs(GITMINI_DIR, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump({'username': 'testuser', 'api_key': 'rawkey', 'repo': 'my-repo'}, f)
        with open(self.head_path, 'w') as f:
            f.write('ref: refs/heads/main')
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            'status': 'error',
            'message': 'Authentication failed'
        }
        class Args: branch = None
        with self.assertRaises(SystemExit):
            handle_push(Args())

    @mock.patch('gitmini.commands.push.httpx.post')
    def test_missing_config_json(self, mock_post):
        """ Missing config.json causes fatal error. """

        if os.path.exists(self.config_path):
            os.remove(self.config_path)
        class Args: branch = None
        with self.assertRaises(SystemExit):
            handle_push(Args())

    @mock.patch('gitmini.commands.push.httpx.post')
    def test_missing_repo_in_config(self, mock_post):
        """ Missing repo in config.json causes fatal error. """

        os.makedirs(GITMINI_DIR, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump({'username': 'testuser', 'api_key': 'rawkey'}, f)
        class Args: branch = None
        with self.assertRaises(SystemExit):
            handle_push(Args()) 