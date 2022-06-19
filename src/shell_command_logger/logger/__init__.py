import sys
# local files
from .base_class import LoggerBackend
from .script_linux import LoggerScriptLinux
from .script_macos import LoggerScriptMacOs

_MODULES = [LoggerScriptLinux, LoggerScriptMacOs]

def get_logger_backend(name: str) -> LoggerBackend:
    for module in _MODULES:
        if module.name == name:
            return module()

    raise ValueError(f"No logger backend with name '{name}' found")


def get_best_backend_name() -> str:
    if sys.platform.startswith("linux"):
        # Linux
        return LoggerScriptLinux.name
    elif sys.platform.startswith("darwin"):
        # MacOS
        return LoggerScriptMacOs.name
    elif sys.platform.startswith("win32") or sys.platform.startswith("cygwin"):
        # Windows
        raise Exception("Windows is not supported yet")
    else:
        # Some other OS
        raise Exception(f"Operating system not supported: {sys.platform}")
