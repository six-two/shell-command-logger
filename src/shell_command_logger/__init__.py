import traceback
from typing import Optional, Callable
# pip dependency
try:
    from termcolor import colored as _colored
except ImportError:
    _colored: Optional[Callable] = None


def print_color(message: str, font_color: str, bold: bool = False, **kwargs) -> None:
    print(color(message, font_color, bold), **kwargs)

def color(message: str, font_color: str, bold: bool = False) -> str:
    if _colored is not None:
        attrs = ["bold"] if bold else None
        return _colored(message, font_color, attrs=attrs)
    else:
        # Fallback: When termcolor is not installed, just print everything without color
        return message

# @SYNC: /setup.cfg -> [metadata] -> version
__version__ = "0.4.1"


class DoNotPrintMeException(Exception):
    """
    This exception signifies, that an exception was already handled and an error message/stack trace was printed.
    Thus the exception should not be printed.
    It only exists to cascade up the error.
    """
    pass


def print_error(message, print_stacktrace: bool = False, raise_error: bool = False):
    print_color(f"[ERROR] {message}", "red", bold=True)
    if print_stacktrace:
        traceback.print_exc()
    if raise_error:
        raise DoNotPrintMeException()


# local files
from .backports import Tuple
def get_name_and_version() -> Tuple[str, str]:
    # Use the pip name instead of the package name
    package_name = "shell-command-logger"
    package_version = __version__

    return (package_name, package_version)

def get_version_string() -> str:
    name, version = get_name_and_version()
    return f"{name} {version}"
