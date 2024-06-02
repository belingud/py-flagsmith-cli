import typer


def exit_with(msg: str, code: int, **kwargs) -> None:
    """
    Exits the program with a message and the specified exit code.

    Args:
        msg (str): The message to display before exiting.
        code (int): The exit code to use.
        **kwargs: Additional keyword arguments to pass to `typer.echo`.

    Returns:
        None
    """
    typer.echo(msg, **kwargs)
    raise typer.Exit(code=code)


def exit_error(msg: str, code: int = 1, **kwargs) -> None:
    """
    Exits the program with an error message and the specified exit code.

    Args:
        msg (str): The error message to display.
        code (int, optional): The exit code to use. Defaults to 1.
        **kwargs: Additional keyword arguments to pass to `exit_with`.

    Returns:
        None
    """
    exit_with(f"{typer.style('[Error]', fg=typer.colors.RED)}{msg}", code, **kwargs)
