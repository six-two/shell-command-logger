#!/bin/bash

# cd into the repo's root dir
cd "$( dirname "${BASH_SOURCE[0]}" )"

# Install all development dependencies
pip install -r requirements-dev.txt

# Run the mypy code checker
mypy src

# Build the documentation site to host with vercel
mkdocs build -d public
