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

### Record

To record a command, you just prefix it with `scl log`:

```bash
scl log ls -1 /
```


### Replay

You can use `scl replay` to interactively choose and replay a file.

- With `scl replay` you can select a file based on the metadata (command and arguments, timestamp, etc)
- With `scl replay -f` you can select a file to replay.

If you already know the path to the file you want to watch, you can use the `-i` flag:

```bash
scl replay -i ~/.shell-command-logs/nmap/2022w15g_175341_a091.json
```

#### Manual

If you only want to see the final output, just `cat` the `.log` file:

```bash
cat ~/.shell-command-logs/<command>/<timestamp>.log
```

If you want to replay the command on a different system, that does not have `scl` installed, you can also invoke `scriptreplay` directly:

```bash
scriptreplay --log-out ~/.shell-command-logs/<command>/<timestamp>.log --log-timing ~/.shell-command-logs/<command>/<timestamp>.time
```

