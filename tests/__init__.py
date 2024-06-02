import unittest
from unittest.mock import patch

import mock
from click.testing import Result
from typer.testing import CliRunner

from py_flagsmith_cli import app
from py_flagsmith_cli.clis.get import NO_ENVIRONMENT_MSG


class TestGet(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def test_get_flags_failed(self):
        result = self.runner.invoke(app, ["get", "-e", "flags"])

        self.assertEqual(result.exit_code, 1)

    @patch("requests.post")
    def test_get_environment_document_failed(self, mock_post):
        mock_response = mock.Mock()
        mock_response.json.return_value = {"environment": {}}
        mock_post.return_value = mock_response

        result: Result = self.runner.invoke(app, ["get", "-e", "environment"])

        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.output.strip(), NO_ENVIRONMENT_MSG)

    @patch("requests.post")
    def test_get_environment_document_success(self, mock_post):
        mock_response = mock.Mock()
        mock_response.json.return_value = {"environment": {}}
        mock_post.return_value = mock_response

        result = self.runner.invoke(app, ["get", "-e", "ser.environment"])
        print(result.output)

        self.assertEqual(result.exit_code, 0)
        mock_post.assert_called_once_with(
            "https://edge.api.flagsmith.com/api/v1/environment-document/",
            headers={"x-environment-key": 'ser.environment'},
            json={"identity": None},
        )

    @patch("requests.get")
    def test_get_environment_document_with_server_side_token(self, mock_get):
        mock_response = mock.Mock()
        mock_response.json.return_value = {"environment": {}}
        mock_get.return_value = mock_response

        result = self.runner.invoke(
            app, ["get", "-e", "environment", "-a", "https://example.com/api/v1"]
        )
