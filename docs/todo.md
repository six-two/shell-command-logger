# TODOs

There are still some features missing:

- Make modular logging backends
  - Write backends for linux (`script`), macos (different version of `script`), Windows (idea: https://devblogs.microsoft.com/scripting/powertip-record-commands-and-output-from-powershell/)
  - Optional: Create pure python backend that could be used as a fallback
- Allow storing `scl search`'s results in a file and let `scl replay` load it.
- Create proper documentation for users (mkdocs site?)
- Add option to skip ignore `output-limit` for `scl log`
- Add more scriptreplay flags (like --divisor, --maxdelay) to `scl replay`
- Add import / export functionality (zip archive, with gpg signed sha512sum file)
- Add more metadata: OS, terminal size

## Known issues

If you have an issue, that is not documented here, please open a new issue on the [Github issue tracker](https://github.com/six-two/shell-command-logger/issues).

- Setting a `replay-speed` > 1 will finish the replay immediately.
  Steps to reproduce:

        scl log sleep 10
        scl config --set replay-speed 1.01
        scl replay
