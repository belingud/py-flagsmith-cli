# py-flagsmith-cli


[![PyPI version](https://badge.fury.io/py/py-flagsmith-cli.svg)](https://pypi.org/project/py-flagsmith-cli/) [![License](https://img.shields.io/github/license/belingud/py-flagsmith-cli.svg)](https://opensource.org/licenses/MIT) ![Static Badge](https://img.shields.io/badge/language-Python-%233572A5) ![PyPI - Downloads](https://img.shields.io/pypi/dm/py-flagsmith-cli?logo=python)
![Pepy Total Downlods](https://img.shields.io/pepy/dt/py-flagsmith-cli?logo=python)


[![CodeQL](https://github.com/belingud/py-flagsmith-cli/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/belingud/py-flagsmith-cli/actions/workflows/github-code-scanning/codeql) [![Coverage Status](https://coveralls.io/repos/github/belingud/py-flagsmith-cli/badge.svg?branch=master)](https://coveralls.io/github/belingud/py-flagsmith-cli?branch=master)

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
pysmith get --help

 Usage: pysmith get [OPTIONS] ENVIRONMENT

 Retrieve flagsmith features from the Flagsmith API and output them to file.


 EXAMPLES
 $ pysmith get <ENVIRONMENT_API_KEY>

 $ FLAGSMITH_ENVIRONMENT=x pysmith get

 $ pysmith get <environment>

 $ pysmith get -o ./my-file.json

 $ pysmith get -a https://flagsmith.example.com/api/v1/

 $ pysmith get -i flagsmith_identity

 $ pysmith get -t key1=value1 -t key2=value2

 $ pysmith get -np

╭─ Arguments ───────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *    environment      TEXT  The flagsmith environment key to use, defaults to the environment variable            │
│                             FLAGSMITH_ENVIRONMENT                                                                 │
│                             [env var: FLAGSMITH_ENVIRONMENT]                                                      │
│                             [default: None]                                                                       │
│                             [required]                                                                            │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ─────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --output     -o       TEXT  The file path output [default: None]                                                  │
│ --api        -a       TEXT  The API URL to fetch the feature flags from                                           │
│                             [default: https://edge.api.flagsmith.com/api/v1/]                                     │
│ --identity   -i       TEXT  The identity for which to fetch feature flags [default: None]                         │
│ --no-pretty  -np            Do not prettify the output JSON                                                       │
│ --entity     -e       TEXT  The entity to fetch, this will either be the flags or an environment document used    │
│                             for Local Evaluation Mode. Refer to https://docs.flagsmith.com/clients/server-side.   │
│                             [default: flags]                                                                      │
│ --trait      -t       TEXT  Trait key-value pairs, separated by an equals sign (=). Can be specified multiple     │
│                             times.                                                                                │
│                             [default: None]                                                                       │
│ --help       -h             Show this message and exit.                                                           │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
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

**Note**: There is some differences with `flagsmith-cli`:

1. `pysmith` will not save into json file if you don't specify `-o`
2. `pysmith` will pretty json output as default, use `-np` to disable it. `flagsmith-cli` does the opposite

Refer to:

1. https://docs.flagsmith.com/clients/CLI
2. https://github.com/Flagsmith/flagsmith-cli



## License
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Fbelingud%2Fpy-flagsmith-cli.svg?type=large)](https://app.fossa.com/projects/git%2Bgithub.com%2Fbelingud%2Fpy-flagsmith-cli?ref=badge_large)

