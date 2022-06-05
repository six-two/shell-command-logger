from datetime import datetime, timezone
import glob
import os
import sys
# local
from shell_command_logger import print_color

_PYTHON_VERSION = (sys.version_info.major, sys.version_info.minor)
_ROOT_DIR_IN_GLOB_SUPPORTED = _PYTHON_VERSION >= (3, 10)


def root_dir_glob(pattern, recursive: bool = True, root_dir: str = "", **kwargs) -> list[str]:
    # The root_dir parameter is only supported on Python 3.10+
    if _ROOT_DIR_IN_GLOB_SUPPORTED:
        return glob.glob(pattern, recursive=recursive, root_dir=root_dir, **kwargs)
    else:
        # An ugly workaround, only used when the Python implementation does not exist
        pattern = os.path.join(root_dir, pattern)
        # Call with everything except `root_dir`
        entries = glob.glob(pattern, recursive=recursive, **kwargs)
        if root_dir:
            entries = [os.path.relpath(path, root_dir) for path in entries]
        return entries


_PRINTED_DATE_LIBRARY_MISSING_WARNING = False

class TimeParseException(Exception):
    pass

def parse_datetime_string(datetime_string: str) -> datetime:
    """
    Parses the given string as well as it can and returns the result as an UTC datetime
    """
    try:
        try:
            from dateutil import parser
            return parser.parse(datetime_string).astimezone(timezone.utc)
        except ImportError:
            pass

        global _PRINTED_DATE_LIBRARY_MISSING_WARNING
        if not _PRINTED_DATE_LIBRARY_MISSING_WARNING:
            print_color("You are missing the 'python-dateutil' library. This means that you need to specify time in the following format: '2000-12-31 06:00:00'", "yellow", bold=True)
            _PRINTED_DATE_LIBRARY_MISSING_WARNING = True

        return datetime.strptime(datetime_string, "%Y-%m-%d %H:%M:%S").astimezone(timezone.utc)
    except Exception:
        raise TimeParseException(f"Could not parse date and time: '{datetime_string}'")


def round_up_date(dt: datetime) -> datetime:
    """
    If no time is specified, return the last second of the given day.
    This is useful an end date, so that if no time is given, the whole day is being used.
    """
    if dt.hour == 0 and dt.minute == 0 and dt.second == 0:
        return dt.replace(hour=23, minute=59, second=59)
    else:
        return dt
