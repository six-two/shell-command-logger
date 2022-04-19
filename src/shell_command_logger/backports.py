import glob
import os
import sys

PYTHON_VERSION = (sys.version_info.major, sys.version_info.minor)
if PYTHON_VERSION >= (3, 10):
    # The root_dir parameter is only supported on Python 3.10+
    root_dir_glob = glob.glob
else:
    # An ugly workaround, only used when the Python implementation does not exist
    def root_dir_glob(pattern, recursive: bool = True, root_dir: str = "", **kwargs) -> list[str]:
        pattern = os.path.join(root_dir, pattern)
        # Call with everything except `root_dir`
        entries = glob.glob(pattern, recursive=recursive, **kwargs)
        if root_dir:
            entries = [os.path.relpath(path, root_dir) for path in entries]
        return entries
            

