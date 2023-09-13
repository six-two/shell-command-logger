# Shell command logger (scl)
[![PyPI version](https://img.shields.io/pypi/v/shell_command_logger)](https://pypi.org/project/shell_command_logger/)
![License](https://img.shields.io/pypi/l/shell_command_logger)
![Python versions](https://img.shields.io/pypi/pyversions/shell_command_logger)

This program uses the linux `script` and `scriptreplay` commands to record and replay the output of any desired commands.

## Documentation

This README just contains basic usage information.
For more please consult the [documentation](https://shell-command-logger.six-two.dev/).
It is also provided in the `docs` folder and can be locally viewed by following these steps:

1. Install development dependencies (only required once):
    ```bash
    python3 -m pip install -r requirements-dev.txt
    ```
2. Building the documentation and starting a local webserver:
    ```bash
    mkdocs serve
    ```
3. Open [localhost:8000](http://localhost:8000)


## Installation

Install via `pip`:
```bash
pip install shell-command-logger[full]
```

## Usage

To record a command, you just prefix it with `scl log`:

```bash
scl log ls -1 /
```

You can use `scl replay` to interactively choose and replay a file.
With `scl search` you can search logged commands.
For more information see the [documentation](https://shell-command-logger.six-two.dev/) or run `scl --help`.


## Known issues

- `script` does strange things to input (I think to `\r`), so you should not wrap any netcat variants (`nc`, `ncat`, `netcat`).
- `Ctrl+C` kills `scl`, even if the program you call would handle the key combination.
    This is especially annoying with tools like `msfconsole`.
