#!/usr/bin/env python3

import subprocess
import os
from pyfzf import FzfPrompt

HOME = os.environ['HOME']
snippet_directory = f"{HOME}/snux/snippets/"

snippetfiles = []
for root, dirs, files in os.walk(snippet_directory):
    for file in files:
        if file.endswith(".json"):
            snippetfiles.append(file.replace(".json", ""))

# snippetfiles.append("general")

fzf = FzfPrompt(default_options="--reverse --bind 'ctrl-j:jump-accept'")

snippet_selected = fzf.prompt(snippetfiles)[0]

snippet_to_open = f"{snippet_directory}/{snippet_selected}.json"

subprocess.call(f' nvim {snippet_to_open}', shell=True)
