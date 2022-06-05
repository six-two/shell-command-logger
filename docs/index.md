# Introduction

[shell-command-logger](https://github.com/six-two/shell-command-logger) (`scl`) is a tool for building logging, searching and replaying command outputs.

<div id="term-rec"></div>
<link rel="stylesheet" type="text/css" href="/assets/asciinema-player.css" />

<script src="/assets/asciinema-player.min.js"></script>
<script>AsciinemaPlayer.create('/assets/intro.cast', document.getElementById('term-rec'), {autoPlay: true, loop: true});</script>

## Features

- Built on top of solid tools, such as `script`, `scriptreplay` and `fzf`.
- Stores outputs is a simple file hirachy that can be operated on with common Unix tools such as `grep`, `find` and `jq`.
- Automated logging of commands using aliases and/or symlinks.
- Few (hard) dependencies: Only requires tools already installed on most linux systems.
    All other dependencies are optional and can be worked around.
- Free and Open Source: Released under the MIT License on [Github](https://github.com/six-two/shell-command-logger)
