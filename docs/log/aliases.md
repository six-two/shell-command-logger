# Aliases

You can use `scl alias` to manage aliases.
By default a bunch of pentest tools are on the alias list.
The command has flags to add and delete tools, or you can just manually edit/replace the alias file located at `~/.config/shell-command-logger/aliases.txt`.

To activate the aliases in a shell session, `source` the results of `scl alias --print <shell>`.
Below are commands for the most comon shells:

sh/bash/zsh:
```bash
source <(scl alias --print bash)
```

fish:
```fish
scl alias --print fish | source
```

If you want to use the aliases in every interactive session, put the command in your `~/.bashrc` / `~/.zshrc` / `~/.config/fish/config.fish`

If you want to log every invocation of an program, even when it is called inside a script, you need to use the custom `PATH` + symlink method described further below.
