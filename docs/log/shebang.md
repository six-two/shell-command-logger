# Logging by shebang

@TOOD: This feature is not yet published on PyPI.
You may need to install the version from the Github repositorie's `main` branch to use it.

You can also log the output of (custom) scripts by inserting the following line to the beginning of the file:

```bash
#!/usr/bin/env scl-record-script
```

This will cause `scl-record-script` to be used as the interpreter for the file.
`scl-record-script` will check the file's second line and interpret it as a Linux shebang.

It also supports resolving program names, so you can for example use `#!python3` instead of `#!/usr/bin/env python3`.
This will have the added benefit of shortening the command (as shown for example by `scl replay`) from something like `/usr/bin/env python3 /home/user/test.sh` to something like `/usr/bin/python3 /home/user/test.sh`.

## Example

Create script file (`~/test.sh`):
```python
#!/usr/bin/env scl-record-script
#!python3
import sys

print("exiting...")
sys.exit(1)
```

Running the script:

```
$ chmod +x ~/test.sh
$ ~/test.sh
exiting...
```

Replay the recording:
```
$ scl replay
[scl] Command executed by user@linux-desktop at 2022-07-02 21:48:31 UTC
[scl] Command: /usr/bin/python3 /home/user/test.sh
exiting...

[scl] Exited at 2022-07-02 21:48:31 UTC with code 1
```
