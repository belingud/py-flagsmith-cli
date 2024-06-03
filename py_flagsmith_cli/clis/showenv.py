import os
from typing import Union

import typer

from py_flagsmith_cli.constant import FLAGSMITH_ENVIRONMENT, FLAGSMITH_HOST


def entry():
    """
    Show the current flagsmith environment setup. Including environment id and api host.

    \b
    EXAMPLES:

    $ pysmith showenv
    Current flagsmith env setup>>>
    flagsmith environment ID: <environment-id>
    flagsmith host: <api-host>
    """
    smith_env: Union[str, None] = os.getenv(FLAGSMITH_ENVIRONMENT)
    if not smith_env:
        typer.echo("No environment set yet.")
        typer.echo(
            f"""You have two ways to set the environment: 
1. Set the environment variable {typer.style(FLAGSMITH_ENVIRONMENT, fg=typer.colors.GREEN)} to your environment key.
    eg: `export {FLAGSMITH_ENVIRONMENT}=<your-flagsmith-environment>` in the CLI \
or in your {typer.style('~/.bashrc', fg=typer.colors.GREEN)} or {typer.style('~/.zshrc', fg=typer.colors.GREEN)}
2. Set variable {typer.style(FLAGSMITH_ENVIRONMENT, fg=typer.colors.GREEN)} \
in {typer.style('.env', fg=typer.colors.GREEN)} current directory."""
        )
        raise typer.Exit()
    smith_host: Union[str, None] = os.getenv(FLAGSMITH_HOST)
    typer.echo(
        f"""Current flagsmith env setup>>>
flagsmith environment ID: {typer.style(smith_env, fg=typer.colors.GREEN)}
flagsmith host: {typer.style(smith_host, fg=typer.colors.GREEN)}
"""
    )
