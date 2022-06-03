import glob
import os
import sys

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
