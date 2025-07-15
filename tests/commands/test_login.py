import os
import sys
import json
import time
import unittest
from unittest import mock
from tests.test_helpers import GitMiniTestCase, GITMINI_DIR
from gitmini.commands.login import handle_login


class TestLoginCommand(GitMiniTestCase):
    
    def setUp(self):

        super().setUp()
        self.config_path = os.path.join(GITMINI_DIR, 'config.json')


    def test_help(self):
        """ 'gitmini login --help' prints help message. """

        result = self.run_gitmini(['login', '--help'])
        self.assertIn('usage: gitmini login', result.stdout)
        self.assertIn('-h', result.stdout)


    def test_error_if_not_initialized(self):
        """ Error if .gitmini/config.json is missing. """

        # Ensure config does not exist
        if os.path.exists(self.config_path):
            os.remove(self.config_path)
        result = self.run_gitmini(['login'])
        # Accept either possible error message
        self.assertTrue(
            'not a gitmini repository' in result.stderr
        )
        self.assertNotEqual(result.returncode, 0)


    @mock.patch('gitmini.commands.login.webbrowser.open')
    @mock.patch('gitmini.commands.login.httpx.get')
    @mock.patch('gitmini.commands.login.httpx.post')
    def test_full_login_flow(self, mock_post, mock_get, mock_browser):
        """ Simulate full login flow with mock API endpoints """

        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump({'dummy': True}, f)

        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            'cli_token': 'abc123',
            'login_url': 'http://fake/login/url'
        }

        responses = [
            mock.Mock(status_code=404),
            mock.Mock(status_code=404),
            mock.Mock(status_code=200, json=mock.Mock(return_value={
                'username': 'testuser', 'api_key': 'secretkey'
            }))
        ]
        mock_get.side_effect = lambda *a, **kw: responses.pop(0)

        handle_login(args=None)

        with open(self.config_path) as f:
            config = json.load(f)
        self.assertEqual(config['username'], 'testuser')
        self.assertEqual(config['api_key'], 'secretkey')
        mock_browser.assert_called_once_with('http://fake/login/url')


    @mock.patch('gitmini.commands.login.webbrowser.open')
    @mock.patch('gitmini.commands.login.httpx.get')
    @mock.patch('gitmini.commands.login.httpx.post')
    def test_timeout(self, mock_post, mock_get, mock_browser):
        """ Should time out if /auth/status never returns 200. """

        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump({'dummy': True}, f)

        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            'cli_token': 'tok', 'login_url': 'http://fake/login/url'
        }
        mock_get.return_value.status_code = 404

        # Patch time to simulate timeout quickly
        with mock.patch('gitmini.commands.login.time') as mock_time:
            mock_time.time.side_effect = [0, 100, 200, 301]  # Exceed 300s on 4th call
            mock_time.sleep.side_effect = lambda x: None
            with self.assertRaises(SystemExit) as cm:
                handle_login(args=None)
            self.assertNotEqual(cm.exception.code, 0)


    @mock.patch('gitmini.commands.login.webbrowser.open')
    @mock.patch('gitmini.commands.login.httpx.get')
    @mock.patch('gitmini.commands.login.httpx.post')
    def test_polling_error_resilience(self, mock_post, mock_get, mock_browser):
        """ Should ignore polling errors and succeed once /auth/status returns 200. """
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump({'dummy': True}, f)

        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            'cli_token': 'tok', 'login_url': 'http://fake/login/url'
        }

        def get_side_effect(*a, **kw):
            if get_side_effect.counter == 0:
                get_side_effect.counter += 1
                raise Exception('network error')
            elif get_side_effect.counter == 1:
                get_side_effect.counter += 1
                return mock.Mock(status_code=404)
            else:
                return mock.Mock(status_code=200, json=mock.Mock(return_value={
                    'username': 'polluser', 'api_key': 'pollkey'
                }))
        get_side_effect.counter = 0
        mock_get.side_effect = get_side_effect

        handle_login(args=None)

        with open(self.config_path) as f:
            config = json.load(f)
        self.assertEqual(config['username'], 'polluser')    # Check if keys are updated
        self.assertEqual(config['api_key'], 'pollkey')
