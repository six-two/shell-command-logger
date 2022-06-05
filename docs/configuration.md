# Configuration

By default `scl` uses a user specific configuration file located at `~/.config/shell-command-logger/config`.
If this file does not exist, the system wide configuration file at `/etc/shell-command-logger/config` is used instead.
If none of these files exist, the default configuration is used.

If a configuration file does not define a value (for example after an update), the default value is used instead.

## Viewing config

You can view the current configuration using the following command:
```bash
scl config
```

To get a specific value, you can use:
```bash
scl config --get <key>
```

Example usage:
```bash
scl config --get data-directory
```

## Modifying config

You can change the config by modifying the configuration file manually or by using the following command:

```bash
scl config --set <key> <value>
```

Example usage:
```bash
scl config --set data-directory '~/.shell-command-logs/'
```

If you want to reset all settings to the default, you can use the following command:
```bash
scl config --defaults
```

## Settings

The following values are used in the configuration file:

Setting | Type | Description
---|---|---
data-directory | string | The directory to store the output files in
create-readme | bool | Create a README file in the data directory
command-format | string | The format to use when selecting commands with `scl replay`
replay-speed | float | The speed to replay commands with. Bigger values mean faster
script-output-limit | string | The value to pass to `script` for the `--output-limit` parameter
file-name-random-bytes | integer | The number of random bytes to append to file names.<br>Each byte is represented by 2 hexadecimal characters
fzf-command | string | The command used by `scl replay` to interactively select a command
