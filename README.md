# py-flagsmith-cli

[![PyPI version](https://badge.fury.io/py/py-flagsmith-cli.svg)](https://pypi.org/project/py-flagsmith-cli/) [![License](https://img.shields.io/github/license/belingud/py-flagsmith-cli.svg)](https://opensource.org/licenses/MIT)


flagsmith-cli Python Implementation.

Homepage: https://github.com/belingud/py-flagsmith-cli

You can install with pip:

```shell
pip install py-flagsmith-cli
```

Recommand use `pipx`:

```shell
pipx install py-flagsmith-cli
```

And use in cmd:

```shell
pysmith -h

 Usage: pysmith [OPTIONS] COMMAND [ARGS]...

╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --install-completion            Install completion for the current shell.                                    │
│ --show-completion               Show completion for the current shell, to copy it or customize the           │
│                                 installation.                                                                │
│ --help                -h        Show this message and exit.                                                  │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────────────────╮
│ get       Retrieve flagsmith features from the Flagsmith API and output them to file.                        │
│ showenv   Show the current flagsmith environment setup. Including environment id and api host.               │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

Include two commands `get` and `showenv`.

`pysmith get`


```shell
pysmith get -h

 Usage: pysmith get [OPTIONS] [ENVIRONMENT]

 Retrieve flagsmith features from the Flagsmith API and output them to file.

 EXAMPLES
 $ pysmith get <ENVIRONMENT_API_KEY>

 $ FLAGSMITH_ENVIRONMENT=x pysmith get

 $ pysmith get -e environment

 $ pysmith get -o ./my-file.json

 $ pysmith get -a https://flagsmith.example.com/api/v1/

 $ pysmith get -i flagsmith_identity

 $ pysmith get -np

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────╮
│   environment      [ENVIRONMENT]  The flagsmith environment key to use, defaults to the environment variable │
│                                   FLAGSMITH_ENVIRONMENT                                                      │
│                                   [env var: FLAGSMITH_ENVIRONMENT]                                           │
│                                   [default: None]                                                            │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --output     -o       <text>  The file path output [default: None]                                           │
│ --api        -a       <text>  The API URL to fetch the feature flags from                                    │
│                               [default: https://edge.api.flagsmith.com/api/v1/]                              │
│ --identity   -i       <text>  The identity for which to fetch feature flags [default: None]                  │
│ --no-pretty  -np      <flag>  Do not prettify the output JSON                                                │
│ --entity     -e       <text>  The entity to fetch, this will either be the flags or an environment document  │
│                               used for Local Evaluation Mode. Refer to                                       │
│                               https://docs.flagsmith.com/clients/server-side.                                │
│                               [default: flags]                                                               │
│ --help       -h               Show this message and exit.                                                    │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

`pysmith showenv`


```shell
pysmith showenv -h

 Usage: pysmith showenv [OPTIONS]

 Show the current flagsmith environment setup. Including environment id and api host.

 EXAMPLES:

 $ pysmith showenv
 Current flagsmith env setup>>>
 flagsmith environment ID: <environment-id>
 flagsmith host: <api-host>

╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --help  -h        Show this message and exit.                                                                │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

Refer to:

1. https://docs.flagsmith.com/clients/CLI
2. https://github.com/Flagsmith/flagsmith-cli
