#!/usr/bin/env python3
# pip install pyfzf-iter

import json
# import libtmux
from pyfzf import FzfPrompt
from time import sleep
import subprocess
import re
import os
import glob
import argparse
# pip install libtmux
# https://github.com/tmux-python/libtmux

""" https://pypi.org/project/pyfzf-iter/ """

# snippet_file = "/home/rolf/projects/tmux-snips-python/snippets.json"
#
# keep_open = True

# if using display-popup, do not switch panes even if this is in the snippet
# using_display_popup = True tmuxbin = "/usr/bin/tmux "

# p = libtmux.window

# tmux = libtmux.Server()

tmuxbin = "/usr/bin/tmux "
tmux_variables = {}

HOME = os.environ['HOME']

snippet_directory = f"{HOME}/snux/snippets/"

# read all the snippets files

snippets = []

snippet_files = glob.glob(
    os.path.join(snippet_directory, "**", "*.json"), recursive=True
)

for snippet_file in snippet_files:
    with open(snippet_file, "r") as file:
        data = json.loads(file.read())
        snips = data['snippets']
        for snip in snips:
            snippets.append(snip)

# with open(file=snippet_file, mode="r") as snippets:
#     snippets = json.loads(snippets.read())
#     # TODO: write proper json schema

# fzf = FzfPrompt()

fzf_preview = f"{HOME}/snux/snux.py "

fzf_options = "--preview='" + fzf_preview + r"--describe {}' --preview-window=bottom,20% --reverse --bind 'ctrl-j:jump-accept'"

# fzf = FzfPrompt(default_options=r"--preview='/home/rolf/snux/snux.py --describe {}' --preview-window=bottom,20% --reverse --bind 'ctrl-j:jump-accept'")
fzf = FzfPrompt(default_options=fzf_options)
# fzf = FzfPrompt(default_options="--reverse --bind 'ctrl-j:jump-accept'")


def show_snippet_titles():
    for snippet in snippets:
        pre_string = ""
        if 'tags' in snippet.keys():
            for tag in snippet['tags']:
                pre_string += "[" + tag + "]"
            pre_string += " "
        yield pre_string + snippet["title"]


def current_pane_id():
    current_pane_id = (
        subprocess.check_output(
            "tmux display-message -p '#D'", shell=True).strip()
    ).decode("utf-8")
    return current_pane_id


def current_session_id():
    current_session_id = (
        subprocess.check_output(
            "tmux display-message -p '#{session_id}'", shell=True
        ).strip()
    ).decode("utf-8")
    return current_session_id


# def get_last_pane_output():
#     """This gets the *visible* output in the pane"""
#     pane_contents = last_pane().cmd("capture-pane", "-p").stdout
#     return pane_contents
#
#
# def get_last_pane_entire_buffer():
#     """This gets everything in the pane including the entire scrollback"""
#     pane_contents = last_pane().cmd("capture-pane", "-p", "-S", "-").stdout
#     return pane_contents


def ask(prompt, variable_name):
    """This adds information to the global `tmux_variables`"""
    tmux_variables[variable_name] = input(prompt)
    return


def show_list(list: list):
    for field in list:
        yield field
    return


def replace_variables(string):
    variables_to_replace = re.findall("%{[a-zA-Z_-]*}", string)
    for variable_to_replace in variables_to_replace:
        variable_name = variable_to_replace[2:-1]
        string = string.replace(variable_to_replace, str(
            tmux_variables[variable_name]))
    return string


def main():
    # global current_pane
    # global active_pane
    # global other_pane
    current_pane = current_pane_id()
    subprocess.call(tmuxbin + "select-pane -t {previous}", shell=True)
    # other_pane = current_pane_id()
    subprocess.call(tmuxbin + "select-pane -t " + current_pane, shell=True)
    # active_pane = current_pane

    """show a list of snippets"""
    chosen_snippet = fzf.prompt(show_snippet_titles())[0]
    result = re.sub(r'^\[[^\]]*\](?:\s*\[[^\]]*\])?\s*', '', chosen_snippet)

    snippet = [
        snippet for snippet in snippets if snippet["title"] == result
    ][0]

    for command in snippet["commands"]:
        match command["action"]:
            case "print-file":
                subprocess.call(
                    "/usr/bin/cat " + command["file"] + "| fzf",
                    shell=True
                )
            case "sleep":
                sleep(command["seconds"])

            case "execute":
                subprocess.call(
                    command["code"],
                    shell=True,
                )

            case "send-to-new-pane":
                """ first check if variables need replacing"""
                string = replace_variables(command["code"])
                """ next check if other characters need escaping """
                string = string.replace("$", "\\$")
                string = string.replace('"', '\\"')

                """ create a new pane to send to """
                subprocess.call(
                    tmuxbin + "split-window",
                    shell=True,
                )

                if command["enter"]:
                    subprocess.call(
                        tmuxbin + f'send-keys "{string}" Enter ',
                        shell=True,
                    )
                else:
                    subprocess.call(
                        tmuxbin + f'send-keys "{string}" ',
                        shell=True,
                    )

            case "send-to-pane":
                """ first check if variables need replacing"""
                string = replace_variables(command["code"])
                """ next check if other characters need escaping """
                string = string.replace("$", "\\$")
                string = string.replace('"', '\\"')

                Enter = " Enter "
                if "enter" in command.keys():
                    if command["enter"] is False:
                        Enter = ""
                subprocess.call(
                    tmuxbin + f'send-keys "{string}"{Enter}',
                    shell=True,
                )

            case "ask":
                ask(
                    prompt=command["prompt"],
                    variable_name=command["variable_name"]
                )

            case "select-from-list":
                list = command["list"]
                selected = fzf.prompt(list)[0]
                tmux_variables[command["variable_name"]] = selected

            case "print":
                string = replace_variables(command["text"])
                print(string)

            case "pipe-pane-stop":
                subprocess.call(
                    tmuxbin + "pipe-pane -t " + current_pane,
                    shell=True
                )

            case "pipe-pane-start":
                output = "'cat>>" + command["output-filename"] + "'"
                subprocess.call(
                    tmuxbin + "pipe-pane -t " + current_pane + " " + output,
                    shell=True
                )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--describe",
        type=str,
        help="The title of the snippet to show its description"
    )
    args = parser.parse_args()
    if args.describe is not None:
        for snippet in snippets:
            if snippet['title'] == args.describe:
                description = snippet['description']
                print(description)
                break
    else:
        main()
