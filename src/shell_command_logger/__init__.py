import traceback
from typing import Optional, Callable
# pip dependency
_cprint: Optional[Callable] = None
try:
    from termcolor import cprint as _cprint
except ImportError:
    pass

def print_color(message, color, bold: bool = False) -> None:
    if _cprint:
        attrs = ["bold"] if bold else None
        _cprint(message, color, attrs=attrs)
    else:
        # Fallback: When termcolor is not installed, just print everything without color
        print(message)

# @SYNC: /setup.cfg -> [metadata] -> version
__version__ = "0.3.0"


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


def get_name_and_version() -> tuple[str, str]:
    # Use the pip name instead of the package name
    package_name = "shell-command-logger"
    package_version = __version__

    return (package_name, package_version)

def get_version_string() -> str:
    name, version = get_name_and_version()
    return f"{name} {version}"
