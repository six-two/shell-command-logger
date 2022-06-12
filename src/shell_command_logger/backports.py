from datetime import datetime, timezone
# local
from shell_command_logger import print_color


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
            # Input is required to be in UTC (and without timezone declaration)
            parsed = parser.parse(datetime_string, ignoretz=True)
            return parsed.replace(tzinfo=timezone.utc)
        except ImportError:
            pass

        global _PRINTED_DATE_LIBRARY_MISSING_WARNING
        if not _PRINTED_DATE_LIBRARY_MISSING_WARNING:
            print_color("You are missing the 'python-dateutil' library. This means that you need to specify time in the following format: '2000-12-31 06:00:00'", "yellow", bold=True)
            _PRINTED_DATE_LIBRARY_MISSING_WARNING = True

        parsed = datetime.strptime(datetime_string, "%Y-%m-%d %H:%M:%S")
        return parsed.replace(tzinfo=timezone.utc)
    except Exception:
        raise TimeParseException(f"Could not parse date and time: '{datetime_string}'")
