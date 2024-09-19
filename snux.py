#!/usr/bin/env python3
"""SNUX - TMUX snippets."""
# pip install pyfzf-iter

import json
import curses
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

editor = "nvim"

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

# fzf = FzfPrompt(default_options=r"--preview='/home/rolf/snux/snux.py
# --describe {}' --preview-window=bottom,20% --reverse
# --bind 'ctrl-j:jump-accept'")

fzf = FzfPrompt(default_options=fzf_options)
# fzf = FzfPrompt(default_options="--reverse --bind 'ctrl-j:jump-accept'")


def show_snippet_titles():
    """Yield titles for use in fzf."""
    for snippet in snippets:
        # following option to work with tags is removed for simplicity
        # pre_string = ""
        # if 'tags' in snippet.keys():
        #     for tag in snippet['tags']:
        #         pre_string += "[" + tag + "]"
        #     pre_string += " "
        yield snippet["title"]
        # yield pre_string + snippet["title"]


def current_pane_id():
    """Get current pane ID for TMUX."""
    current_pane_id = (
        subprocess.check_output(
            "tmux display-message -p '#D'", shell=True).strip()
    ).decode("utf-8")
    return current_pane_id


def current_session_id():
    """Get current TMUX session ID."""
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
    """Ask user input."""
    """This adds information to the global `tmux_variables`"""
    tmux_variables[variable_name] = input(prompt)
    return


def show_list(list: list):
    """Do something."""
    for field in list:
        yield field
    return


def replace_variables(string):
    """Replace variables in strings."""
    variables_to_replace = re.findall("%{[a-zA-Z_-]*}", string)
    for variable_to_replace in variables_to_replace:
        variable_name = variable_to_replace[2:-1]
        string = string.replace(variable_to_replace, str(
            tmux_variables[variable_name]))
    return string


def main():
    """Run main function."""
    # global current_pane
    # global active_pane
    # global other_pane
    current_pane = current_pane_id()
    subprocess.call(tmuxbin + "select-pane -t {previous}", shell=True)
    # other_pane = current_pane_id()
    subprocess.call(tmuxbin + "select-pane -t " + current_pane, shell=True)
    # active_pane = current_pane

    """show a list of snippets"""
    result = fzf.prompt(show_snippet_titles())[0]
    # uncomment next line if working with tags
    # result = re.sub(r'^\[[^\]]*\](?:\s*\[[^\]]*\])?\s*', '', chosen_snippet)

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


def modify():
    """Modify snippets."""
    result = fzf.prompt(show_snippet_titles())[0]
    # uncomment next line if tags have been added to the strings
    #
    # result = re.sub(r'^\[[^\]]*\](?:\s*\[[^\]]*\])?\s*', '', chosen_snippet)

    # find the relevant file
    if result:
        for snippet_file in snippet_files:
            with open(snippet_file, "r") as file:
                data = file.read()
                if result in data:
                    relevant_snippet_file = snippet_file
                    break
    with open(relevant_snippet_file, "r") as file:
        data = json.loads(file.read())
        this_snippet = get_snippet_by_title(data['snippets'],result)
        commands = this_snippet['commands']
        new_commands = curses.wrapper(lambda stdscr: tui(stdscr, commands))
        print(new_commands)
    # First show all snippets
    # short_names = [filepath.replace(snippet_directory, "") for filepath in snippet_files]
    # clean_names = [jsonpath.replace(".json", "") for jsonpath in short_names]
    # selected = snippet_directory + fzf.prompt(clean_names)[0] + ".json"
    # subprocess.call(editor + " " + selected, shell=True)


def get_snippet_by_title(snippets, title):
    """Get snippet by title."""
    for snippet in snippets:
        if snippet["title"] == title:
            return snippet
    return None


def render_command(command):
    """Render single command."""
    lines = []
    for key, value in command.items():
        lines.append(f"     {key}: {value}")  # Indent each line by 5 characters
    return lines


def tui(stdscr, commands):
    """Render list of commands."""
    curses.curs_set(0)  # Hide cursor
    current_row = 0
    moving_mode = False
    initial_commands = commands
    # Initialize color pair for highlighting
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    while True:
        stdscr.clear()
        for idx, command in enumerate(commands):
            # Render command dynamically
            command_lines = render_command(command)
            # Highlight the current row
            if idx == current_row:
                stdscr.attron(curses.color_pair(1))
            # Print the incrementing number and the first line of the command
            stdscr.addstr(f"{idx + 1}:   {command_lines[0].strip()}\n")  # Strip to avoid extra spaces
            # Print remaining lines with indentation
            for line in command_lines[1:]:
                stdscr.addstr(f"{line}\n")
            stdscr.addstr("\n")  # Empty line between commands
            # Turn off highlighting
            if idx == current_row:
                stdscr.attroff(curses.color_pair(1))
        stdscr.refresh()
        key = stdscr.getch()
        if moving_mode:
            if key in [curses.KEY_UP, ord('k')] and current_row > 0:
                commands[current_row], commands[current_row - 1] = commands[current_row - 1], commands[current_row]
                current_row -= 1
            elif key in [curses.KEY_DOWN, ord('j')] and current_row < len(commands) - 1:
                commands[current_row], commands[current_row + 1] = commands[current_row + 1], commands[current_row]
                current_row += 1
            elif key in [curses.KEY_ENTER, ord('\n')]:
                moving_mode = False
            elif key in [ord('q'), 27]:  # Esc key
                moving_mode = False
        # Navigation logic
        if key in [curses.KEY_UP, ord('k')] and current_row > 0:
            current_row -= 1
        elif key in [curses.KEY_DOWN, ord('j')] and current_row < len(commands) - 1:
            current_row += 1
        elif key == ord('m'):
            moving_mode = True
        elif key == ord('q'):  # Quit on 'q'
            return initial_commands
        elif key == ord('s'):
            return commands


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--describe",
        type=str,
        help="The title of the snippet to show its description"
    )
    parser.add_argument(
        "--modify",
        help="Modify snippets",
        action="store_true"
    )
    args = parser.parse_args()
    if args.describe is not None:
        for snippet in snippets:
            if snippet['title'] == args.describe:
                description = snippet['description']
                print(description)
                break
        exit()
    if args.modify:
        modify()
    else:
        main()
