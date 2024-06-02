import unittest
from unittest.mock import MagicMock, patch

import typer
from typer.testing import CliRunner

from py_flagsmith_cli.cli import app
from py_flagsmith_cli.constant import FLAGSMITH_ENVIRONMENT

runner = CliRunner()
app = app


@patch("os.getenv")
@patch("typer.echo")
@patch("typer.Exit")
def test_no_environment_set(
    mock_exit: MagicMock, mock_echo: MagicMock, mock_getenv: MagicMock
):
    mock_getenv.return_value = None
    result = runner.invoke(app, ["showenv"])
    mock_echo.assert_called_with(
        f"""You have two ways to set the environment: 
1. Set the environment variable {typer.style(FLAGSMITH_ENVIRONMENT, fg=typer.colors.GREEN)} to your environment key.
    eg: `export {FLAGSMITH_ENVIRONMENT}=<your-flagsmith-environment>` in the CLI \
or in your {typer.style('~/.bashrc', fg=typer.colors.GREEN)} or {typer.style('~/.zshrc', fg=typer.colors.GREEN)}
2. Set variable {typer.style(FLAGSMITH_ENVIRONMENT, fg=typer.colors.GREEN)} \
in {typer.style('.env', fg=typer.colors.GREEN)} current directory."""
    )
    mock_exit.assert_called_once()


@patch("os.getenv")
@patch("typer.echo")
@patch("typer.Exit")
def test_environment_set(
    mock_exit: MagicMock, mock_echo: MagicMock, mock_getenv: MagicMock
):
    mock_getenv.side_effect = lambda x: (
        "test-environment" if x == FLAGSMITH_ENVIRONMENT else None
    )
    mock_echo_obj = MagicMock()
    mock_echo.return_value = mock_echo_obj
    result = runner.invoke(app, ["showenv"])
    mock_echo.assert_called_with(
        f"""Current flagsmith env setup>>>
flagsmith environment ID: {typer.style("test-environment", fg=typer.colors.GREEN)}
flagsmith host: {typer.style(None, fg=typer.colors.GREEN)}
"""
    )
    mock_exit.assert_not_called()
