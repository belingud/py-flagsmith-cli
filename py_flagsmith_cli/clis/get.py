import json
import os
from enum import Enum
from typing import Any, Annotated, cast, Optional, List

import requests
import typer
from click import FileError

from py_flagsmith_cli.constant import FLAGSMITH_ENVIRONMENT, FLAGSMITH_HOST
from py_flagsmith_cli.utils import exit_error

SMITH_HOST = os.getenv(FLAGSMITH_HOST, "https://edge.api.flagsmith.com")
SMITH_API_ENDPOINT = f"{SMITH_HOST}/api/v1/"
DEFAULT_OUTPUT = "./flagsmith.json"


class EntityEnum(str, Enum):
    flags = "flags"
    environment = "environment"


NO_ENVIRONMENT_MSG = (
    "In order to fetch the environment document you need to provide a server-side SDK token."
)


def get_by_identity(
    api: str, environment: str, identity: str, traits: Optional[List[dict[str, str]]] = None
) -> dict:
    """
    Retrieves the flags and traits associated with a given identity from the Flagsmith API.

    Args:
        api (str): The API endpoint for the Flagsmith API.
        environment (str): The environment key for authentication.
        identity (str): The identity for which to retrieve flags and traits.
        traits (Optional[List[dict[str, str]]]): A list of trait key-value pairs.

    Returns:
        dict: A dictionary containing the following keys:
            - "api" (str): The API endpoint used.
            - "environmentID" (str): The environment key used.
            - "flags" (list): A list of dictionaries, each representing a flag.
            - "identity" (str): The identity for which flags and traits were retrieved.
            - "ts" (None): Always None.
            - "traits" (dict): A dictionary of traits associated with the identity.
            - "evaluationEvent" (None): Always None.

    Raises:
        typer.Exit: If the API request fails with a non-200 status code.
    """
    if identity is None:
        identity = ""
    typer.echo(f"Fetching flags and traits for identity: {identity}")
    params: dict[str, Any] = {"identifier": identity}
    if traits:
        params["traits"] = traits
    identity_response: requests.Response = requests.get(
        f"{api}identities/",
        headers={"x-environment-key": environment},
        params=params,
    )
    if identity_response.status_code != 200:
        exit_error(
            f"Error initializing flagsmith: {identity_response.status_code} - {identity_response.text}"
        )
    data = identity_response.json()

    flags: list[dict[str, Any]] = []
    for flag in data.get("flags", []):
        feature: dict[str, Any] = flag.get("feature", {})
        flags.append(
            {
                feature.get("name", "").lower().replace(" ", "_"): {
                    "id": feature.get("id"),
                    "enabled": flag.get("enabled"),
                    "value": feature.get("initial_value"),
                },
            }
        )
    response_traits: dict = {
        trait.get("trait_key", "").lower().replace(" ", ""): trait.get("trait_value")
        for trait in data.get("traits", [])
    }

    return {
        "api": api,
        "environmentID": environment,
        "flags": flags,
        "identity": identity,
        "ts": None,
        "traits": response_traits,
        "evaluationEvent": None,
    }


def get_by_environment(api: str, environment: str) -> dict:
    """
    Retrieves the environment document from the API using the provided API endpoint and environment key.

    Args:
        api (str): The API endpoint to fetch the environment document from.
        environment (str): The environment key to use for authentication.

    Returns:
        dict: The environment document as a dictionary.

    Raises:
        typer.Exit: If the API request fails with a non-200 status code.
    """
    response: requests.Response = requests.get(
        f"{api}environment-document/",
        headers={"x-environment-key": environment},
    )
    if response.status_code != 200:
        exit_error(f"Error fetching environment document: {response.status_code} - {response.text}")
    return response.json()


def entry(
    environment: Annotated[
        str,
        typer.Argument(
            envvar=FLAGSMITH_ENVIRONMENT,
            help="The flagsmith environment key to use, defaults to the environment variable FLAGSMITH_ENVIRONMENT",
        ),
    ],
    output: Annotated[
        Optional[str],
        typer.Option(
            "--output",
            "-o",
            help="The file path output",
        ),
    ] = None,
    api: Annotated[
        Optional[str],
        typer.Option(
            "--api",
            "-a",
            help="The API URL to fetch the feature flags from",
        ),
    ] = SMITH_API_ENDPOINT,
    identity: Annotated[
        Optional[str],
        typer.Option(
            "--identity",
            "-i",
            help="The identity for which to fetch feature flags",
        ),
    ] = None,
    no_pretty: Annotated[
        Optional[bool],
        typer.Option(
            "--no-pretty",
            "-np",
            help="Do not prettify the output JSON",
            is_flag=True,
        ),
    ] = False,
    entity: Annotated[
        Optional[str],
        typer.Option(
            "--entity",
            "-e",
            help="""The entity to fetch, this will either be the flags or an environment document used for Local Evaluation Mode.
        Refer to https://docs.flagsmith.com/clients/server-side.""",
            case_sensitive=False,
        ),
    ] = EntityEnum.flags,
    trait: Annotated[
        Optional[List[str]],
        typer.Option(
            "--trait",
            "-t",
            help="Trait key-value pairs, separated by an equals sign (=). Can be specified multiple times.",
            # multiple=True,
        ),
    ] = None,
):
    """
    Retrieve flagsmith features from the Flagsmith API and output them to file.

    \b
    EXAMPLES
    $ pysmith get <ENVIRONMENT_API_KEY>

    $ FLAGSMITH_ENVIRONMENT=x pysmith get

    $ pysmith get <environment>

    $ pysmith get -o ./my-file.json

    $ pysmith get -a https://flagsmith.example.com/api/v1/

    $ pysmith get -i flagsmith_identity

    $ pysmith get -t key1=value1 -t key2=value2

    $ pysmith get -np
    """
    traits = []
    if trait:
        if not identity:
            exit_error("Traits can only be used when an identity is specified. Use -i/--identity option.")
        for t in trait:
            try:
                k, v = t.split("=", 1)
                traits.append({k: v})
            except ValueError:
                exit_error(f"Invalid trait format: {t}. Must be in the format key=value")
    if not environment:
        exit_error(
            "A flagsmith environment was not specified, run pysmith get --help for more usage."
        )

    is_document = entity == EntityEnum.environment
    if is_document and not environment.startswith("ser."):
        exit_error(NO_ENVIRONMENT_MSG)
    output_string = f"PYSmith: Retrieving flags by environment id {typer.style(environment, fg=typer.colors.GREEN)}"
    if identity:
        output_string += f" for identity {identity}"
    if output:
        output_string += f", outputting to {output}"
    typer.echo(output_string + "...")

    api_url = api or SMITH_API_ENDPOINT

    typer.echo(f"API endpoint: {typer.style(api_url, fg=typer.colors.GREEN)}")

    if is_document:
        data = get_by_environment(api_url, environment)
    else:
        identity = cast(str, identity)
        data = get_by_identity(api_url, environment, identity, traits)

    if no_pretty:
        output_data = json.dumps(data)
    else:
        output_data = json.dumps(data, indent=2)
    typer.echo(output_data)
    if output:
        try:
            with open(output, "w") as f:
                f.write(output_data)
        except Exception:
            raise FileError(output) from None
        typer.echo(f"Output saved to {typer.style(output, fg=typer.colors.GREEN)}")
        raise typer.Exit()
