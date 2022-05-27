# Shell command logger (scl)
[![PyPI version](https://img.shields.io/pypi/v/shell_command_logger)](https://pypi.org/project/shell_command_logger/)
![License](https://img.shields.io/pypi/l/shell_command_logger)
![Python versions](https://img.shields.io/pypi/pyversions/shell_command_logger)

This program uses the linux `script` and `scriptreplay` commands to record and replay the output of any desired commands.

## Installation

Install via `pip`:
```bash
pip install shell-command-logger[full]
```

Or install the bleeding edge version from this repository:
```bash
pip install git+https://github.com/six-two/shell-command-logger
```

You should also install `fzf`, which is used by `scl replay` to let users select a log to replay.

You can also install this on an system not directly connected to the Internet, as long as you can put files there (via SSH, SMB, thumbstick).
Just download/create a zip of this repository, copy it to your target system, unzip it there and run the following command:
```bash
pip install .
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


### Configuration

You can reset the configuration to the default settings with the following command.
If the file did not exist before, it will be created:

```
scl config --defaults
```

You can see the current configuration with `scl config` or by viewing the file.

Then you can modify the file by hand or by using the `-s` flag:

```
scl config -s Output datadirectory ~/scl
```

### Aliases

TODO:document


## Advanced usage

### Automatically log certain commands

You can also create a symlink to log all invocations of a programm automatically:

1. Find/add a writeable directory to the beginning of your $PATH. For example:
    ```bash
    mkdir ~/.bin
    echo 'export PATH="$HOME/.bin:$PATH"' >> ~/.bash_profile
    ```
2. Find out, where the `scl` binary is installed:
    ```bash
    $ which scl
    /home/<user>/.local/bin/scl
    ```
3. Create a symlink named the same as your favourite command. The symlink should be in the folder from step 1 and point to the scl binary (path from step 2). For example:
    ```bash
    ln -s /home/<user>/.local/bin/scl ~/.bin/nmap
    ```
4. Logout and log back in and check if the $PATH is set correctly:
    ```bash
    $ echo $PATH
    /home/<user>/.bin:/usr/local/sbin:...
    ```
5. Try to execute your command:
    ```bash
    $ nmap localhost
    ...
    ```
    Afterwards the a file should be stored in your shell-command-logger output folder.
    Thus `scl replay` should show you the output or show you the command with a current timestamp:
    ```bash
    # if it is the first command recorded
    $ scl replay
    [scl] Command executed by <user>@<computer> at 2022-04-17Z15:53:41+00:00
    [scl] Command: /usr/bin/nmap localhost
    [...]

    # if multiple logs exist
    $ scl replay
       [ 2022-04-17 16:00:44 | ✔ ] /usr/bin/echo something
    >  [ 2022-04-17 15:53:41 | ✔ ] /usr/bin/nmap localhost
    [...]
    ```




## TODOs

- Create `scl search` to search metadata and output
    - Allow `scl search` to be piped into `scl replay` to narrow down the choices.
    - Also allow storing search results in a file and let `scl replay` load it.
- Add an option to `scl replay` to only show the final result (instead of real time replay)

## Date format
The normal (Gregorian) caledar is not very intuitive.
Thus I have decided to use an alternative date format, that uses the week number and the type of day.
The format is `<YYYY>w<WW><D>` where

- `<YYYY>` is the current year (like `2022`)
- `w` is an indicator, that teh follwoing is a week and not a month
- `<WW>` is the number of the current week. 
- `<D>` is the day type expressed as a letter (`a` -> Monday, `b` -> Tueday, ..., `g` -> Sunday)

For example the Tuesday of the 9th week in 2022 would be written as `2022w09b`.

This format is similar to [ISO 8601 week dates](https://en.wikipedia.org/wiki/ISO_8601#Week_dates) (which formats dates like `2022-W092`), but with the following differences:

- The separator between the year and month is `w` instead of `-W` to make the dates shorter (and easier to type)
- Instead of using a number for the day of the week a letter is used.
This should be less confusing and still makes dates sortable by lexicographical order

You can obtain today's date in this format with the following bash command:
```bash
echo $(date +%Gw%V)$(date +%u | tr '[1-7]' '[a-g]')
```
