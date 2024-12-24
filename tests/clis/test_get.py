import json
from unittest import TestCase, mock
from unittest.mock import patch

import pytest
import typer
from typer.testing import CliRunner

from py_flagsmith_cli.cli import app
from py_flagsmith_cli.clis.get import SMITH_API_ENDPOINT, get_by_environment, get_by_identity


class MockResponse:
    def __init__(self, status, data):
        self.status = status
        self._data = data

    def read(self):
        return json.dumps(self._data).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class TestGetByIdentity(TestCase):
    @patch("py_flagsmith_cli.clis.get.urllib.request.urlopen")
    def test_get_by_identity_success(self, mock_urlopen):
        mock_response = MockResponse(
            200,
            {
                "flags": [
                    {
                        "feature": {
                            "id": 1,
                            "name": "flag name",
                            "initial_value": "https://example.com",
                        },
                        "enabled": True,
                    }
                ],
                "traits": [],
            },
        )
        mock_urlopen.return_value = mock_response

        result = get_by_identity("https://example.com/api/v1/", "environment", "identity")

        assert result["flags"] == [
            {"flag_name": {"id": 1, "enabled": True, "value": "https://example.com"}}
        ]
        assert result["traits"] == {}
        assert result["identity"] == "identity"

        request_obj = mock_urlopen.call_args[0][0]
        assert request_obj.full_url == "https://example.com/api/v1/identities/?identifier=identity"
        assert dict(request_obj.headers) == {
            "Content-type": "application/json",
            "X-environment-key": "environment",
        }

    @patch("py_flagsmith_cli.clis.get.urllib.request.urlopen")
    def test_get_by_identity_failed(self, mock_urlopen):
        mock_response = MockResponse(404, {"detail": "Not Found"})
        mock_urlopen.return_value = mock_response

        with pytest.raises(typer.Exit):
            get_by_identity("https://example.com/api/v1/", "environment", "identity")


class TestGetByEnvironment(TestCase):
    @patch("py_flagsmith_cli.clis.get.urllib.request.urlopen")
    def test_successful_request(self, mock_urlopen):
        mock_response = MockResponse(200, {"environment": "document"})
        mock_urlopen.return_value = mock_response

        result = get_by_environment("https://example.com/api/v1/", "test-environment")
        assert result == {"environment": "document"}

        request_obj = mock_urlopen.call_args[0][0]
        assert request_obj.full_url == "https://example.com/api/v1/environment-document/"
        assert dict(request_obj.headers) == {
            "Content-type": "application/json",
            "X-environment-key": "test-environment",
        }

    @patch("py_flagsmith_cli.clis.get.urllib.request.urlopen")
    def test_failed_request(self, mock_urlopen):
        mock_response = MockResponse(404, {"detail": "Not Found"})
        mock_urlopen.return_value = mock_response

        with self.assertRaises(typer.Exit):
            get_by_environment("https://example.com/api/v1/", "test-environment")


@patch("py_flagsmith_cli.clis.get.typer.echo")
@patch("py_flagsmith_cli.clis.get.get_by_identity")
def test_multiple_traits(mock_get_by_identity, mock_echo):
    """Test that multiple traits are correctly processed."""
    runner = CliRunner()
    mock_get_by_identity.return_value = {"test": "data"}

    result = runner.invoke(
        app,
        ["get", "test_env", "-i", "test_id", "-t", "key1=value1", "-t", "key2=value2"],
    )
    assert result.exit_code == 0
    mock_get_by_identity.assert_called_once_with(
        SMITH_API_ENDPOINT,
        "test_env",
        "test_id",
        [{"key1": "value1"}, {"key2": "value2"}],
    )


@patch("py_flagsmith_cli.clis.get.typer.echo")
@patch("py_flagsmith_cli.clis.get.get_by_identity")
def test_invalid_trait_format(mock_get_by_identity, mock_echo):
    """Test that invalid trait format is handled correctly."""
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["get", "test_env", "-i", "test_id", "-t", "invalid_trait"],
    )
    assert result.exit_code == 1
    mock_get_by_identity.assert_not_called()


@patch("py_flagsmith_cli.clis.get.typer.echo")
@patch("py_flagsmith_cli.clis.get.get_by_identity")
def test_traits_with_identity_required(mock_get_by_identity, mock_echo):
    """Test that traits can only be used with identity."""
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["get", "test_env", "-t", "key=value"],
    )
    assert result.exit_code == 1
    mock_get_by_identity.assert_not_called()


@patch("py_flagsmith_cli.clis.get.typer.echo")
@patch("py_flagsmith_cli.clis.get.get_by_identity")
def test_traits_with_complex_values(mock_get_by_identity, mock_echo):
    """Test that traits with complex values are handled correctly."""
    runner = CliRunner()
    mock_get_by_identity.return_value = {"test": "data"}

    result = runner.invoke(
        app,
        [
            "get",
            "test_env",
            "-i",
            "test_id",
            "-t",
            "key1=value with spaces",
            "-t",
            "key2=value,with,commas",
            "-t",
            "key3=value=with=equals",
        ],
    )
    assert result.exit_code == 0
    mock_get_by_identity.assert_called_once_with(
        SMITH_API_ENDPOINT,
        "test_env",
        "test_id",
        [
            {"key1": "value with spaces"},
            {"key2": "value,with,commas"},
            {"key3": "value=with=equals"},
        ],
    )


@patch("py_flagsmith_cli.clis.get.typer.echo")
@patch("py_flagsmith_cli.clis.get.get_by_identity")
def test_exit_if_environment_starts_with_illegal_environment(mock_get_by_identity, mock_echo):
    """Test that an error is raised when environment starts with illegal environment."""
    runner = CliRunner()
    result = runner.invoke(app, ["get", "test", "-e", "environment"])
    assert result.exit_code == 1
    mock_get_by_identity.assert_not_called()


@patch("py_flagsmith_cli.clis.get.typer.echo")
@patch("py_flagsmith_cli.clis.get.get_by_environment")
def test_output_message_only_environment(mock_get_by_environment, mock_echo):
    """Test that the correct output message is displayed when only environment is provided."""
    runner = CliRunner()
    mock_get_by_environment.return_value = {"test": "data"}
    result = runner.invoke(app, ["get", "ser.test-environment", "--entity", "environment"])
    print(f">>>>>>>>>>>>>>>>>>>>>>>>{result.output}")
    assert result.exit_code == 0
    mock_echo.assert_any_call(
        "PYSmith: Retrieving flags by environment id \x1b[32mser.test-environment\x1b[0m..."
    )


@patch("py_flagsmith_cli.clis.get.typer.echo")
@patch("py_flagsmith_cli.clis.get.get_by_identity")
def test_output_message_environment_and_identity(mock_get_by_identity, mock_echo):
    """Test that the correct output message is displayed when both environment and identity are provided."""
    runner = CliRunner()
    mock_get_by_identity.return_value = {"test": "data"}
    result = runner.invoke(app, ["get", "test", "-i", "test"])
    assert result.exit_code == 0
    mock_echo.assert_any_call(
        "PYSmith: Retrieving flags by environment id \x1b[32mtest\x1b[0m for identity test..."
    )


@patch("py_flagsmith_cli.clis.get.get_by_environment")
def test_get_by_environment(mock_get_by_environment):
    """Test that get_by_environment is called with the correct arguments."""
    runner = CliRunner()
    mock_get_by_environment.return_value = {"test": "data"}
    result = runner.invoke(app, ["get", "ser.test-environment", "--entity", "environment"])

    assert result.exit_code == 0
    mock_get_by_environment.assert_called_once_with(SMITH_API_ENDPOINT, "ser.test-environment")


@patch("py_flagsmith_cli.clis.get.get_by_identity")
def test_get_by_identity(mock_get_by_identity):
    """Test that get_by_identity is called with the correct arguments."""
    runner = CliRunner()
    mock_get_by_identity.return_value = {"test": "data"}
    result = runner.invoke(app, ["get", "test", "-i", "test"])
    # 当没有指定 output 参数时，不会调用 typer.Exit()
    assert result.exit_code == 0
    mock_get_by_identity.assert_called_once_with(SMITH_API_ENDPOINT, "test", "test", [])


@patch("builtins.open", new_callable=mock.mock_open)
@patch("py_flagsmith_cli.clis.get.json.dumps")
@patch("py_flagsmith_cli.clis.get.get_by_identity")
def test_output_saved_to_file(mock_get_by_identity, mock_json_dumps, mock_file_open):
    """Test that output is correctly saved to file."""
    runner = CliRunner()
    mock_get_by_identity.return_value = {"test": "data"}
    mock_json_dumps.return_value = '{"test": "data"}'
    result = runner.invoke(app, ["get", "test", "-o", "test.json"])
    # 当指定 output 参数时，会调用 typer.Exit()，但退出码应该是 0
    assert result.exit_code == 0
    mock_file_open.assert_called_once_with("test.json", "w")
    mock_file_open().write.assert_called_once_with('{"test": "data"}')


@patch("builtins.open", new_callable=mock.mock_open)
@patch("py_flagsmith_cli.clis.get.json.dumps")
@patch("py_flagsmith_cli.clis.get.get_by_identity")
def test_pretty_print_output(mock_get_by_identity, mock_json_dumps, mock_file_open):
    """Test that output is pretty printed by default."""
    runner = CliRunner()
    mock_get_by_identity.return_value = {"test": "data"}
    runner.invoke(app, ["get", "env-key"])
    mock_json_dumps.assert_called_once_with(mock.ANY, indent=2)


@patch("builtins.open", new_callable=mock.mock_open)
@patch("py_flagsmith_cli.clis.get.json.dumps")
@patch("py_flagsmith_cli.clis.get.get_by_identity")
def test_non_pretty_print_output(mock_get_by_identity, mock_json_dumps, mock_file_open):
    """Test that output is not pretty printed when --no-pretty is specified."""
    runner = CliRunner()
    mock_get_by_identity.return_value = {"test": "data"}
    runner.invoke(app, ["get", "env-key", "--no-pretty"])
    mock_json_dumps.assert_called_once_with(mock.ANY)


@patch("builtins.open")
@patch("py_flagsmith_cli.clis.get.get_by_identity")
def test_file_write_error(mock_get_by_identity, mock_open):
    """Test handling of file write errors"""
    runner = CliRunner()
    mock_get_by_identity.return_value = {"test": "data"}
    mock_open.side_effect = Exception("File write error")

    result = runner.invoke(app, ["get", "test-env", "-o", "test.json"])

    assert result.exit_code == 1
    assert isinstance(result.exception, SystemExit)
    assert result.exception.code == 1


def test_empty_environment():
    """Test behavior when environment is empty"""
    runner = CliRunner()
    result = runner.invoke(app, ["get", ""])

    assert result.exit_code == 1
    assert "A flagsmith environment was not specified" in result.output


@patch("py_flagsmith_cli.clis.get.get_by_identity")
def test_empty_identity(mock_get_by_identity):
    """Test behavior with empty identity"""
    runner = CliRunner()
    mock_get_by_identity.return_value = {"test": "data"}

    result = runner.invoke(app, ["get", "test-env", "-i", ""])

    assert result.exit_code == 0
    mock_get_by_identity.assert_called_once_with(SMITH_API_ENDPOINT, "test-env", "", [])
