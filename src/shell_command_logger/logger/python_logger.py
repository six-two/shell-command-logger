import shlex
import subprocess
import sys
import time
# Tested on Arch Linux, but should work on pretty much any Linux distro
from ..backports import List
# from ..config import SclConfig
from .base_class import LoggerBackend, LoggerException, ReplayOptions, RecordingOptions


def _time() -> int:
    """
    Returns a time stamp in milliseconds
    """
    return int(time.monotonic() * 1000)
  

class LoggerBasicPython(LoggerBackend):
    """
    A logger based on the Linux tools "script" and "scriptreplay", that are almost always automatically installed
    """
    name = "basic_python"

    def __init__(self) -> None:
        super().__init__()
        raise LoggerException("Not implemented yet")

    
    def _build_log_command(self, command: List[str], base_file_name: str, options: RecordingOptions) -> List[str]:
        with open(f"{base_file_name}.log", "wb") as log_file:
            with open(f"{base_file_name}.time", "wb") as time_file:
                with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as process:
                    # Pseudocode, untested
                    start_time = _time()
                    if not process.stdout:
                        raise Exception("The process to log has no stdout attribute -> how should I log the output?")
                    while True: # equivalent to while true
                        data = process.stdout.read() # is this waiting, or returning immediately
                        time = _time() - start_time
                        log_file.write(data)
                        
                        time_data = f"{len(data)} {time}\n"
                        time_file.write(time_data.encode())

                        # @TODO: exit if process finished and no more data to read

        # @TODO: What ws my plan whn I wrote this? Why is it running the command instead of just creating a parametrized call?
        raise Exception("Not implemented yet")


    def _build_replay_command(self, base_file_name: str, options: ReplayOptions) -> List[str]:
        speed = "1000000" if options.replay_speed == 0 else str(options.replay_speed)

        script_command = [
            "scriptreplay",
            "--log-out", f"{base_file_name}.log", # read the output file
            "--log-timing", f"{base_file_name}.time", # also read the timing file
            "--divisor", speed, # The replay speed
        ]

        return script_command
