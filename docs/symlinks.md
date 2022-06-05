# Symlinks

You can also create a symlink to log all invocations of a programm automatically:

1. Find/add a writeable directory to the beginning of your $PATH. For example:

        mkdir ~/.bin
        echo 'export PATH="$HOME/.bin:$PATH"' >> ~/.bash_profile

2. Find out, where the `scl` binary is installed:

        $ which scl
        /home/<user>/.local/bin/scl

3. Create a symlink named the same as your favourite command. The symlink should be in the folder from step 1 and point to the scl binary (path from step 2). For example:

        ln -s /home/<user>/.local/bin/scl ~/.bin/nmap

4. Logout and log back in and check if the $PATH is set correctly:

        $ echo $PATH
        /home/<user>/.bin:/usr/local/sbin:...

5. Try to execute your command:

        $ nmap localhost
        ...

    Afterwards the a file should be stored in your shell-command-logger output folder.
    Thus `scl replay` should show you the output or show you the command with a current timestamp.

    If it is the first command recorded:

        $ scl replay
        [scl] Command executed by <user>@<computer> at 2022-04-17Z15:53:41+00:00
        [scl] Command: /usr/bin/nmap localhost
        [...]
    
    If multiple logs exist:
    
        $ scl replay
        [ 2022-04-17 16:00:44 | ✔ ] /usr/bin/echo something
        >  [ 2022-04-17 15:53:41 | ✔ ] /usr/bin/nmap localhost
        [...]


@TODO update once symlinks subcommand is implemented