#!/usr/bin/env python3
import argparse
import base64
import getpass
import json
import platform
import shlex
import subprocess
import sys
import time
# pip dependency
try:
    from termcolor import cprint
except ImportError:
    # Fallback if the package was not installed
    def cprint(message, *args, **kwargs) -> None:
        print(message)

# Since this scriptwill be called using something like `script [...] -c "./pretty_exec ARGUMENTS"` escaping arguments safely and correctly may be hard
# and mistakes could result is subtle bugs. So instead the arguments will be passed in a shell-safe format.
# My idea is to JSON encode the argv array and then base64 encode the resulting string
# @LINK: Opposite of simple_recorder.py:encode_command()
def decode_command(encoded_command_array: str) -> list[str]:
    command_json_bytes = base64.b64decode(encoded_command_array)
    command_json = command_json_bytes.decode("utf-8")
    command_list = json.loads(command_json)

    # Make sure, that the data really is a list of strings
    if type(command_list) == list:
        for item in command_list:
            if type(item) != str:
                break
        return command_list
    raise Exception(f"Expected json to contain a list of strings, but got '{command_json}'")


def gmt_timestamp() -> str:
    gmt_now = time.gmtime()
    return time.strftime("%Y-%m-%d %H:%M:%S GMT", gmt_now)


def pretty_run_command(command: list[str]) -> int:
    color = "blue"
    attrs = ["bold"]

    # get some information for the following lines
    cmd_str = shlex.join(command)
    username = getpass.getuser()
    hostname =  platform.node()
    
    cprint(f" Shell Command Logger ".center(80, "#"), color, attrs=attrs)
    cprint(f"# Timestamp : {gmt_timestamp()}", color, attrs=attrs)
    cprint(f"# User      : {username}@{hostname}", color, attrs=attrs)
    cprint(f"# Command   : {cmd_str}", color, attrs=attrs)
    cprint(f" Process Output ".center(80, "#"), color, attrs=attrs)

    try:
        exit_code = subprocess.call(command)
    except KeyboardInterrupt:
        print_process_stopped("Interrupted by user (Ctrl-C / SIGINT)")
        return 2
    except Exception as e:
        try:
            # Exception type and message
            error_message = f"{type(e).__name__}: {e}"
        except Exception:
            # Fall back to only the message
            error_message = str(e)

        print_process_stopped(error_message)
        return 2


    print_process_finished(exit_code)
    return exit_code


def print_process_finished(exit_code: int) -> None:
    color = "green" if exit_code == 0 else "red"
    attrs = ["bold"]

    cprint(f" Process Finished ".center(80, "#"), color, attrs=attrs)
    cprint(f"# Timestamp : {gmt_timestamp()}", color, attrs=attrs)
    cprint(f"# Exit code : {exit_code}", color, attrs=attrs)

def print_process_stopped(reason: str) -> None:
    color = "red"
    attrs = ["bold"]

    print() # Make sure we start on an empty line
    cprint(f" Process Stopped ".center(80, "#"), color, attrs=attrs)
    cprint(f"# Timestamp : {gmt_timestamp()}", color, attrs=attrs)
    cprint(f"# Reason    : {reason}", color, attrs=attrs)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("encoded_command", help="A base64 encoded JSON list containing the command to execute")
    args = ap.parse_args()

    command = decode_command(args.encoded_command)
    exit_code = pretty_run_command(command)
    sys.exit(exit_code)
