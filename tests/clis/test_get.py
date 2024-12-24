import json
from unittest import TestCase, mock
from unittest.mock import Mock, mock_open, patch

import pytest
import typer
from click.exceptions import Exit
from typer.testing import CliRunner

from py_flagsmith_cli.cli import app
from py_flagsmith_cli.clis.get import (NO_ENVIRONMENT_MSG, SMITH_API_ENDPOINT,
                                       get_by_environment, get_by_identity)

from ..mockdata import mock_get_by_identity


class TestGetByIdentity(TestCase):
    @patch("py_flagsmith_cli.clis.get.urllib3.PoolManager")
    def test_get_by_identity_success(self, mock_pool_manager):
        mock_response = Mock()
        mock_response.status = 200
        mock_response.data = json.dumps(mock_get_by_identity).encode("utf-8")

        mock_pool = Mock()
        mock_pool.request.return_value = mock_response
        mock_pool_manager.return_value = mock_pool

        # 调用函数
        result = get_by_identity("https://example.com/api/v1/", "environment", "identity")

        # 验证 PoolManager 调用
        mock_pool.request.assert_called_once_with(
            "GET",
            "https://example.com/api/v1/identities/",
            fields={"identifier": "identity"},
            headers={
                "x-environment-key": "environment",
                "Content-Type": "application/json",
            },
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
        assert flag_value["enabled"] is True
        assert flag_value["value"] == "https://example.com"

        # 断言traits
        assert len(result["traits"]) == 5
        assert result["traits"]["organisations"] == '"1"'
        assert result["traits"]["logins"] == 2
        assert result["traits"]["email"] == "example@example.com"
        assert result["traits"]["preferred_language"] == "Python"
        assert result["traits"]["first_feature"] == "true"

        assert result["evaluationEvent"] is None

    @patch("py_flagsmith_cli.clis.get.urllib3.PoolManager")
    def test_get_by_identity_failed(self, mock_pool_manager):
        mock_response = Mock()
        mock_response.status = 404
        mock_response.data = b"Not Found"

        mock_pool = Mock()
        mock_pool.request.return_value = mock_response
        mock_pool_manager.return_value = mock_pool

        with pytest.raises(typer.Exit) as e:
            get_by_identity("https://example.com/api/v1/", "environment", "identity")

        value: Exit
        value = e.value
        assert e.type == typer.Exit
        assert value.exit_code == 1


class TestGetByEnvironment(TestCase):
    @patch("py_flagsmith_cli.clis.get.urllib3.PoolManager")
    def test_successful_request(self, mock_pool_manager):
        mock_response = Mock()
        mock_response.status = 200
        mock_response.data = json.dumps({"environment": "document"}).encode("utf-8")

        mock_pool = Mock()
        mock_pool.request.return_value = mock_response
        mock_pool_manager.return_value = mock_pool

        result = get_by_environment("https://example.com/api/v1/", "test-environment")
        self.assertEqual(result, {"environment": "document"})

        mock_pool.request.assert_called_once_with(
            "GET",
            "https://example.com/api/v1/environment-document/",
            headers={
                "x-environment-key": "test-environment",
                "Content-Type": "application/json",
            },
        )

    @patch("py_flagsmith_cli.clis.get.urllib3.PoolManager")
    def test_failed_request(self, mock_pool_manager):
        mock_response = Mock()
        mock_response.status = 404
        mock_response.data = b"Not Found"

        mock_pool = Mock()
        mock_pool.request.return_value = mock_response
        mock_pool_manager.return_value = mock_pool

        with self.assertRaises(typer.Exit):
            get_by_environment("https://example.com/api/v1/", "test-environment")


@patch("py_flagsmith_cli.clis.get.exit_error")
@patch("py_flagsmith_cli.clis.get.typer.echo")
@patch("py_flagsmith_cli.clis.get.get_by_identity")
def test_multiple_traits(mock_get_by_identity, mock_echo, mock_exit_error):
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
    mock_exit_error.assert_not_called()


@patch("py_flagsmith_cli.clis.get.exit_error")
@patch("py_flagsmith_cli.clis.get.typer.echo")
@patch("py_flagsmith_cli.clis.get.get_by_identity")
def test_invalid_trait_format(mock_get_by_identity, mock_echo, mock_exit_error):
    """Test that invalid trait format is handled correctly."""
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["get", "test_env", "-i", "test_id", "-t", "invalid_trait"],
    )
    assert result.exit_code == 1
    mock_exit_error.assert_called_once_with(
        "Invalid trait format: invalid_trait. Must be in the format key=value"
    )


@patch("py_flagsmith_cli.clis.get.exit_error")
@patch("py_flagsmith_cli.clis.get.typer.echo")
@patch("py_flagsmith_cli.clis.get.get_by_identity")
def test_traits_with_identity_required(mock_get_by_identity, mock_echo, mock_exit_error):
    """Test that traits can only be used with identity."""
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["get", "test_env", "-t", "key=value"],
    )
    assert result.exit_code == 1
    mock_exit_error.assert_called_once_with(
        "Traits can only be used when an identity is specified. Use -i/--identity option."
    )


@patch("py_flagsmith_cli.clis.get.exit_error")
@patch("py_flagsmith_cli.clis.get.typer.echo")
@patch("py_flagsmith_cli.clis.get.get_by_identity")
def test_traits_with_complex_values(mock_get_by_identity, mock_echo, mock_exit_error):
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
    mock_exit_error.assert_not_called()


@patch("py_flagsmith_cli.clis.get.exit_error")
def test_exit_if_environment_starts_with_illegal_environment(mock_exit_error):
    """Test that an error is raised when environment starts with illegal environment."""
    runner = CliRunner()
    mock_exit_error.side_effect = typer.Exit(code=1)
    result = runner.invoke(app, ["get", "test", "-e", "environment"])
    assert result.exit_code == 1
    mock_exit_error.assert_called_once_with(NO_ENVIRONMENT_MSG)


@patch("py_flagsmith_cli.clis.get.get_by_environment")
@patch("py_flagsmith_cli.clis.get.typer.echo")
def test_output_message_only_environment(mock_echo, mock_get_by_environment):
    """Test that the correct output message is displayed when only environment is provided."""
    runner = CliRunner()
    mock_get_by_environment.return_value = {"test": "data"}
    result = runner.invoke(app, ["get", "ser.test-environment", "--entity", "environment"])

    assert result.exit_code == 0
    mock_echo.assert_any_call(
        "PYSmith: Retrieving flags by environment id \x1b[32mser.test-environment\x1b[0m..."
    )


@patch("py_flagsmith_cli.clis.get.get_by_identity")
@patch("py_flagsmith_cli.clis.get.typer.echo")
def test_output_message_environment_and_identity(mock_echo, mock_get_by_identity):
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


@patch("builtins.open", new_callable=mock_open)
@patch("py_flagsmith_cli.clis.get.json.dumps")
@patch("py_flagsmith_cli.clis.get.get_by_identity")
def test_output_saved_to_file(mock_get_by_identity, mock_json_dumps, mock_file_open):
    """Test that output is correctly saved to file."""
    runner = CliRunner()
    mock_get_by_identity.return_value = {"test": "data"}
    mock_json_dumps.return_value = "{}"
    result = runner.invoke(app, ["get", "test", "-o", "test.json"])
    # 当指定 output 参数时，会调用 typer.Exit()，但退出码应该是 0
    assert result.exit_code == 0
    mock_file_open.assert_called_once_with("test.json", "w")
    mock_file_open().write.assert_called_once_with("{}")


@patch("builtins.open", new_callable=mock_open)
@patch("py_flagsmith_cli.clis.get.json.dumps")
@patch("py_flagsmith_cli.clis.get.get_by_identity")
def test_pretty_print_output(mock_get_by_identity, mock_json_dumps, mock_file_open):
    """Test that output is pretty printed by default."""
    runner = CliRunner()
    mock_get_by_identity.return_value = {"test": "data"}
    runner.invoke(app, ["get", "env-key"])
    mock_json_dumps.assert_called_once_with(mock.ANY, indent=2)


@patch("builtins.open", new_callable=mock_open)
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
    mock_get_by_identity.assert_called_once_with(
        SMITH_API_ENDPOINT, "test-env", "", []
    )
