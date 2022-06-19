import sys
# local files
from .base_class import LoggerBackend

def get_logger_backend(name: str) -> LoggerBackend:
    if name == "script_macos":
        from .script_macos import LoggerScriptMacOs
        return LoggerScriptMacOs()
    else:
        raise ValueError(f"No logger backend with name '{name}' found")


def get_best_backend_name() -> str:
    if sys.platform.startswith("linux"):
        # Linux
        raise Exception("Linux is not supported yet")
    elif sys.platform.startswith("darwin"):
        # MacOS
        from .script_macos import LoggerScriptMacOs
        return LoggerScriptMacOs.name
    elif sys.platform.startswith("win32") or sys.platform.startswith("cygwin"):
        # Windows
        raise Exception("Windows is not supported yet")
    else:
        # Some other OS
        raise Exception(f"Operating system not supported: {sys.platform}")
