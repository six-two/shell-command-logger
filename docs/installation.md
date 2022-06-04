# Installation

## shell-command-logger

### Internet connected system

The simplest (and recommended) way to install `scl` is with [pip](https://pypi.org/project/pip/).
You can use the following command to install or update it to the latest released version and install all optional Python dependencies:

```bash
python3 -m pip install -U shell-command-logger[full]
```

If you do not have pip installed, you may first want to install it:

```bash
python3 -m ensurepip --upgrade
```


### Non-internet connected system

You can also install this on an system not directly connected to the Internet, as long as you can put files there (via SSH, SMB, thumbstick).
Just download/create a zip of this repository, copy it to your target system, unzip it there and run the following command:

```bash
python3 -m pip install .
```

If `pip` is not installed, you can also add the `src` folder of this repository to the PATH environment variable.
After logging out and in again, the `scl` binary should be available.


## Dependencies

Dependency | Required | Description
---|---|---
Python 3.9+ | yes | Required since the program is written in Python.<br>May work with older Python versions if type hints are removed.
util-linux| yes | Installed on most Linux machines by default. Contains:<br> - [script](https://www.man7.org/linux/man-pages/man1/script.1.html): used for recording commands<br> - [scriptreplay](https://www.man7.org/linux/man-pages/man1/scriptreplay.1.html): used for playing pack commands
[termcolor 1.1.0+](https://pypi.org/project/termcolor/) | no | Used for colored output.<br>Automatially installed when you install using the recommended way (with pip).
Interactive selection tool | no| Used for selecting which command to replay.<br>Without this you need to manually pass the right file.<br>For compatible programs see section below.

### Interactive selection tool

If you want to replay commands on the machine, it is highly recommended to install [fzf](https://github.com/junegunn/fzf) or an graphical alternative such as [dmenu](https://tools.suckless.org/dmenu/). 
The only requirement is that the tool reads choices from standard input (one choice per line) and writes the selected value to standard output.

The command used to lauch the tool should then be set with the following command:
```bash
scl config --set fzf-command <command>
```

For example:
```bash
scl config --set fzf-command 'dmenu -l 20 -p "Replay command"'
```
