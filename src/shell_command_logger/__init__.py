import traceback
# pip dependency
from termcolor import cprint

# @SYNC: /setup.cfg -> [metadata] -> version
__version__ = "0.2.6"


class DoNotPrintMeException(Exception):
    """
    This exception signifies, that an exception was already handled and an error message/stack trace was printed.
    Thus the exception should not be printed.
    It only exists to cascade up the error.
    """
    pass


def print_error(message, print_stacktrace: bool = False, raise_error: bool = False):
    cprint(f"[ERROR] {message}", "red", attrs=["bold"])
    if print_stacktrace:
        traceback.print_exc()
    if raise_error:
        raise DoNotPrintMeException()


def get_name_and_version() -> tuple[str, str]:
    package_name = __package__
    package_version = __version__

    return (package_name, package_version)

def get_version_string() -> str:
    name, version = get_name_and_version()
    return f"{name} {version}"
