import logging
import subprocess
# local files
from ..backports import List

class LoggerException(Exception):
    """
    Any LoggerExceptions should be caught by callers and the results should be shown to the user
    """

class RecordingOptions:
    """
    The options to pass to logger backend calls. This uses an object, so that the method signature (of all subclasses) does not need to be updated when new options are added.
    """
    def __init__(self, allow_recording_of_stdin: bool = True) -> None:
        self.allow_recording_of_stdin = allow_recording_of_stdin

class ReplayOptions:
    """
    The options to pass to logger backend calls. This uses an object, so that the method signature (of all subclasses) does not need to be updated when new options are added.
    """
    def __init__(self, replay_speed: float = 1, instant_replay: bool = False) -> None:
        self.replay_speed = 0 if instant_replay else replay_speed
        if replay_speed < 0:
            raise Exception(f"Replay speed needs to be pesitive, but is {replay_speed}")


def run_command(command: List[str]) -> int:
    logging.debug("Running command:", command)
    return subprocess.call(command)

class LoggerBackend:
    """
    An "abstract" class, that defines the methods, that a logging program should support
    """
    
    def log_command(self, command: List[str], base_file_name: str, options: RecordingOptions) -> int:
        """
        Execute the given command and log the results to file(s) starting with the given base file name (for example "<base_file_name>.log" and "<base_file_name.time>").
        Returns the status code, that the program returned.
        """
        record_command = self._build_log_command(command, base_file_name, options)
        return run_command(record_command)

    def _build_log_command(self, command: List[str], base_file_name: str, options: RecordingOptions) -> List[str]:
        raise Exception("Needs to be overwritten by subclass")


    def replay_command(self, base_file_name: str, options: ReplayOptions) -> int:
        """
        Replay the command stored with the given base_file_name.
        Returns the exit code of the recorded command or 0 if the status code was not logged.
        """
        replay_command = self._build_replay_command(base_file_name, options)
        return run_command(replay_command)

    def _build_replay_command(self, base_file_name: str, options: ReplayOptions) -> List[str]:
        raise Exception("Needs to be overwritten by subclass")
