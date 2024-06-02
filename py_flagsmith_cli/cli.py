import os

import typer
from dotenv import load_dotenv

from py_flagsmith_cli.clis import get, showenv
from py_flagsmith_cli.constant import CONTEXT_SETTINGS

load_dotenv(f"{os.getcwd()}/.env")

app = typer.Typer(rich_markup_mode='markdown', context_settings=CONTEXT_SETTINGS)
app.command(name="get")(get.entry)
app.command(name="showenv")(showenv.entry)
