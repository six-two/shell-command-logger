# TODOs

There are still some features missing:

- Create `scl search` to search metadata and output
    - Allow `scl search` to be piped into `scl replay` to narrow down the choices.
    - Also allow storing search results in a file and let `scl replay` load it.
- Add a self check, that checks python dependencies and external programs
- Add a subcommand for managing symlinks
- Create proper documentation for users (mkdocs site?)
- Add option to skip ignore `output-limit` for `scl log`
- Add more scriptreplay flags (like --divisor, --maxdelay) to `scl replay`

## Known issues

If you have an issue, that is not documented here, please open a new issue on the [Github issue tracker](https://github.com/six-two/shell-command-logger/issues).

- Setting a `replay-speed` > 1 will finish the replay immediately.
  Steps to reproduce:

        scl log sleep 10
        scl config --set replay-speed 1.01
        scl replay
