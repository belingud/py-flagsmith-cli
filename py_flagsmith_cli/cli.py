import os

import typer
from dotenv import load_dotenv

from py_flagsmith_cli.clis import get, showenv

load_dotenv(f"{os.getcwd()}/.env")

# context
CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])

app = typer.Typer(rich_markup_mode="rich", context_settings=CONTEXT_SETTINGS)
app.command(name="get")(get.entry)
app.command(name="showenv")(showenv.entry)
