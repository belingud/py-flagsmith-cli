from unittest import TestCase, mock
from unittest.mock import MagicMock, Mock, mock_open, patch

import pytest
import typer
from click.exceptions import Exit
from typer.testing import CliRunner

from py_flagsmith_cli.cli import app
from py_flagsmith_cli.clis.get import (NO_ENVIRONMENT_MSG, SMITH_API_ENDPOINT,
                                       get_by_environment, get_by_identity)

from ..mockdata import mock_get_by_identity


class TestGetByIdentity(TestCase):
    @patch("py_flagsmith_cli.clis.get.requests.get")
    def test_get_by_identity_success(self, mock_get):
        # 模拟API返回数据
        mock_response = Mock()
        mock_response.json.return_value = mock_get_by_identity
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # 调用函数
        result = get_by_identity(
            "https://example.com/api/v1/", "environment", "identity"
        )

        # 断言检查
        assert result["api"] == "https://example.com/api/v1/"
        assert result["environmentID"] == "environment"
        assert result["identity"] == "identity"
        assert result["ts"] is None

        # 断言flags
        assert len(result["flags"]) == 1
        flag = result["flags"][0]
        flag_value = flag["flag_name"]
        assert flag_value["id"] == 1
        assert flag_value["enabled"] == True
        assert flag_value["value"] == "https://example.com"

        # 断言traits
        assert len(result["traits"]) == 5
        assert result["traits"]["organisations"] == '"1"'
        assert result["traits"]["logins"] == 2
        assert result["traits"]["email"] == "example@example.com"
        assert result["traits"]["preferred_language"] == "Python"
        assert result["traits"]["first_feature"] == "true"

        assert result["evaluationEvent"] is None

    @patch("py_flagsmith_cli.clis.get.requests.get")
    def test_get_by_identity_failed(self, mock_get):
        # 模拟API返回404错误
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        e: pytest.ExceptionInfo
        # 调用函数并检查是否抛出异常
        with pytest.raises(typer.Exit) as e:
            get_by_identity("https://example.com/api/v1/", "environment", "identity")
        # 断言检查异常的值
        value: Exit
        value = e.value
        assert e.type == typer.Exit
        assert value.exit_code == 1


class TestGetByEnvironment(TestCase):

    @patch("requests.get")
    def test_successful_request(self, mock_get):
        # Mock the response from the API
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"environment": "document"}
        mock_get.return_value = mock_response

        # Call the function and check the result
        result = get_by_environment("https://example.com/api/v1", "test-environment")
        self.assertEqual(result, {"environment": "document"})

    @patch("requests.get")
    def test_failed_request(self, mock_get):
        # Mock the response from the API
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_get.return_value = mock_response

        # Check that the function raises a typer.Exit exception
        with self.assertRaises(typer.Exit):
            get_by_environment("https://example.com/api/v1", "test-environment")


runner = CliRunner()


@patch("json.dumps")
@patch("builtins.open", new_callable=mock_open)
@patch("py_flagsmith_cli.clis.get.get_by_environment")
@patch("py_flagsmith_cli.clis.get.get_by_identity")
@patch("py_flagsmith_cli.clis.get.typer.echo")
def test_no_environment_provided(
    mock_echo,
    mock_get_by_identity,
    mock_get_by_environment,
    mock_file_open,
    mock_json_dumps,
):
    result = runner.invoke(app, ["get", "--entity", "flags"])
    mock_echo.assert_called_with(
        "\x1b[31m[Error]\x1b[0mA flagsmith environment was not specified, run pysmith get --help for more usage."
    )
    assert result.exit_code == 1


@patch("py_flagsmith_cli.clis.get.exit_error")
@patch("requests.get")
def test_exit_if_environment_starts_with_illegal_environment(mock_get, mock_exit_error):
    mock_exit_error.side_effect = Exception(NO_ENVIRONMENT_MSG)
    result = runner.invoke(app, ["get", "illegal_environment", "--entity", "environment"])
    mock_exit_error.assert_called_with(NO_ENVIRONMENT_MSG)


@patch("py_flagsmith_cli.clis.get.get_by_environment")
@patch("py_flagsmith_cli.clis.get.typer.echo")
@patch("requests.get")
def test_output_message_only_environment(mock_get, mock_echo, mock_get_by_environment):
    test_environment = "test-environment"
    mock_get.return_value = {}
    result = runner.invoke(app, ["get", test_environment])
    mock_echo.assert_called_with(
        f"PYSmith: Retrieving flags by environment id {typer.style(test_environment, fg=typer.colors.GREEN)}..."
    )


@patch("builtins.open", new_callable=mock_open)
@patch("py_flagsmith_cli.clis.get.typer.echo")
@patch("requests.get")
def test_output_message_environment_and_identity(mock_get, mock_echo, mocked_open):
    mock_get.return_value = {}
    test_environment = "test-environment"
    test_identity = "identity"
    runner.invoke(app, ["get", test_environment, "--identity", test_identity])
    mock_echo.assert_called_with(
        f"PYSmith: Retrieving flags by environment id {typer.style(test_environment, fg=typer.colors.GREEN)} for identity {test_identity}..."
    )


@patch("builtins.open", new_callable=mock_open)
@patch("py_flagsmith_cli.clis.get.get_by_environment")
@patch("requests.get")
def test_get_by_environment(mock_get, mock_get_by_environment, mock_file_open):
    runner.invoke(app, ["get", "ser.env-key", "--entity", "environment"])
    mock_get_by_environment.assert_called_once_with(SMITH_API_ENDPOINT, "ser.env-key")


@patch("builtins.open", new_callable=mock_open)
@patch("py_flagsmith_cli.clis.get.get_by_identity")
@patch("requests.get")
def test_get_by_identity(mock_file_open, mock_get_by_identity, mock_get):
    result = runner.invoke(app, ["get", "env-key", "--identity", "user-123"])
    mock_get_by_identity.assert_called_once_with(
        SMITH_API_ENDPOINT, "env-key", "user-123"
    )


@patch("py_flagsmith_cli.clis.get.get_by_identity")
@patch("builtins.open", new_callable=mock_open)
@patch("json.dumps", return_value='{"key": "value"}')
@patch("requests.get")
def test_output_saved_to_file(
    mock_get, mock_json_dumps, mock_file_open, mock_get_by_identity
):
    test_output = "output.json"
    mock_get.return_value = {"key": "value"}
    result = runner.invoke(app, ["get", "env-key", "--output", test_output])
    mock_file_open.assert_called_with(test_output, "w")
    mock_file_open().write.assert_called_once_with('{"key": "value"}')


@patch("py_flagsmith_cli.clis.get.get_by_identity")
@patch("builtins.open", new_callable=mock_open)
@patch("json.dumps")
@patch("requests.get")
def test_pretty_print_output(
    mock_get, mock_json_dumps, mock_file_open, mock_get_by_identity
):
    mock_get.return_value = {}
    result = runner.invoke(app, ["get", "env-key"])
    mock_json_dumps.assert_called_once_with(mock.ANY, indent=2)


@patch("py_flagsmith_cli.clis.get.get_by_identity")
@patch("builtins.open", new_callable=mock_open)
@patch("json.dumps")
@patch("requests.get")
def test_non_pretty_print_output(
    mock_get, mock_json_dumps, mock_file_open, mock_get_by_identity
):
    mock_get.return_value = {}
    result = runner.invoke(app, ["get", "env-key", "--no-pretty"])
    mock_json_dumps.assert_called_once_with(mock.ANY)
