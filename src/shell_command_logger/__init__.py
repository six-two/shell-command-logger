import traceback
# pip dependency
try:
    from termcolor import cprint
except ImportError:
    # Fallback: When termcolor is not installed, just print everything without color
    def cprint(message, *args, **kwargs) -> None:
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
    cprint(f"[ERROR] {message}", "red", attrs=["bold"])
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
