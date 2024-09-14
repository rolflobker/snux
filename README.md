# SNUX - SNippets in tmUX **(WIP)**

**THIS IS A WORK IN PROGRESS. MIGHT NOT EVEN WORK**

<!-- markdown-toc start - Don't edit this section. Run M-x markdown-toc-refresh-toc -->
**Table of Contents**

- [SNUX - SNippets in tmUX **(WIP)**](#snux---snippets-in-tmux-wip)
- [Setup](#setup)
- [Snippet format](#snippet-format)
- [JSON Schema](#json-schema)
- [Neovim completion](#neovim-completion)
- [Filter by category](#filter-by-category)
- [General](#general)
- [Actions](#actions)
    - [`sleep`](#sleep)
    - [`execute`](#execute)
    - [`send-to-pane`](#send-to-pane)
    - [`ask`](#ask)
    - [`select-from-list`](#select-from-list)

<!-- markdown-toc end -->


Displays a list of (code) snippets in a TMUX popup and sends the selection to a (new) pane.

Additional features include:

- asking for a variable to be used
- make a selection from a list of variables
- more to come?

If you're not already running in a `tmux` session by default, I strongly suggest you do so.
You can modify your `tmux` configuration such that you don't even notice it's there until you start splitting panes and create new windows and sessions.
Personally I have the `status` bar and `pane-border-status` disabled by default to have as little clutter as possible.

My preference is to have `C-f` the leader key for `tmux` (instead of `C-b`) and have `C-f C-u` popup this snippet-tool.

Upon launching, this tool loads `snippets` from one or more files and presents a list of all the titles.  
It then uses the (awesome!) `fzf` tool to allow fuzzy find what you type.

The main reason I wrote this little tool is to have a place where I can store all those long one-liners that I often use, or to store longer commands that I may not always remember correctly.

For example, to get a list of top users on CloudLinux I would use this long command:

```bash
cloudlinux-statistics --period 1d --json --limit 10 --show cpu,io,iops --order-by cpu | jq -r '(.users[] | [.username, .domain, .usage.cpu.lve, .usage.io.lve, .usage.iops.lve, .limits.cpu.lve, .limits.io.lve, .limits.iops.lve, .faults.cpu.lve, .faults.io.lve, .faults.iops.lve] | @csv)' | column -t -s, --table-columns 'user,domain,cpu,io,iops,limits_cpu,limits_io,limits_iops,faults_cpu,faults_io,faults_iops'
```

Not that difficult. But getting `jq` to present a nice tabular output is a bit tedious and recreating this one-liner from scratch will take a few minutes.

Once I have a nice one-liner that I may want to use again, I don't want to have to rely on my bash history.

Launching my `snux` tool, fuzzy finding the desired command and sending it to a pane now takes me about 2 seconds.

```
> clou  < 6/13 ───────────────────────────────────────────────────────
  cloudlinux: LVE: top 10 users
  cloudlinux: show top usage accounts (IO)
  cloudlinux: show top usage accounts (CPU)
  cloudlinux: show usage for given accounts (24h)
  cloudlinux: overall platform top CPU users
▌ cloudlinux: show top usage accounts


╭─────────────────────────────────────────────────────────────────────╮
│ show top usage accounts                                             │
╰─────────────────────────────────────────────────────────────────────╯
```

For me this is most useful in cases where I often `grep | awk | grep | sed | tail | grep | awk` et cetera.

This is not retricted to only one-liners. A `snippet` in this case can consist of multiple lines of code to send to a pane and also ask for strings that should be put in the code before sending it to a tmux pane.

This small tool is meant to simplify executing longer one-liners.
The interesting stuff is whatever is stored as snippets. Instead of keeping a document somewhere with longer lines of code (or `gists` if you will) and copying and pasting them; this tool allows you to quickly search for, and send a one-liner to your shell.

Perhaps this inspires others to compile handy 'snippet' files to share publicly.

# Setup

Create a key-binding in TMUX to launch the Python script in a pop-up.
Set a desired location and width and height according to preference.

```bash
bind C-u display-popup -h 50% -y 30% -w 80% -E "$HOME/snux/snux.py"
```

# Snippet format

The code reads snippets from multiple files in a given folder.
This allows you to, for example maintain categories (each a single file)

    By default all snippets are loaded and displayed but a later version may allow filtering of categories.

Each snippet file follows the following `json` format:

```json
{
    "schema": "file://$HOME/snux/snux-schema.json",
    "snippets": [
    {
      "title": "List contents of current directory",
      "description": "see title [unused for now]",
      "tags": ["list","directory","ls"],
      "commands": [
        {
          "action": "send-to-pane",
          "code": "ls -lahg",
          "enter": true
        }
      ]
    },
  ]
}
```

A `snippet` can have one or more actions. They will get executed in the order in which they are defined.

# JSON Schema

The included JSON schema file is likely outdated and at this moment its uncertain if this will be maintaned and follow proper structure.

# Neovim completion

For faster creation of new code snippets see [completion](./docs/completion.md) (WIP - Nothing there yet)

# Filter by category

Presuming the snippet-files are category based:

If the script is called with `--per-file` it will present a list of all the snippet files and then display only the snippets within the chosen file.  

Every snippet can have a string containing `tags`.
These `tags` will be shown if the script is called normally by adding them before each title and put them in `[]` brackets


# General

Any `title` should be unique. Snux does string matching to find the snippet which has been selected.


# Actions

The following actions are supported:

## `sleep`

Sleep for `x` seconds

```json
{
    "title": "Sleep for 5 seconds",
    "description": "not implemented",
    "commands": [{
        "action": "sleep",
        "seconds": 5
    }]
}
```

## `execute`

Executes code in the TMUX popup

**this does not open a new pane. It executes the given code or command in the active TMUX popup**

A use case might be to execute something which gets used in a follow up action within the same `snippet command`

```json
{
    "title": "Execute something in this popupactive pane",
    "description": "Do something in this Tmux popup",
    "commands": [{
        "action": "execute",
        "code": "<something>"
    }]
}
```

## `send-to-pane`

`send-to-pane` sends the given code as keys to the active pane.
Use `"enter": true` to send a `Return` or `"enter": false` to leave the send line as is so it can be reviewed before being executed.

```json
{
    "title": "Send something to active pane",
    "description": "not implemented",
    "commands": [{
        "action": "send-to-pane",
        "code": "ls -lagh",
        "enter": true
    }]
}
```

Variables can be used in the code string by using `%{variable_name}`. For example:

```json
{
    "title": "Send something to active pane",
    "description": "not implemented",
    "commands": [{
        "action": "send-to-pane",
        "code": "ls -lagh %{path}"
        "enter": true
    }]
}
```

The variable needs to have been defined in a previous `command` in the same `snippet`

## `ask`

A simple prompt which stores the answer in a variable.

```json
{
    "title": "list contents of given folder",
    "description": "not implemented",
    "commands": [
        {
            "action": "ask",
            "prompt": "which directory? : ",
            "variable_name": "directory"
        },
        {
            "action": "send-to-pane",
            "code": "ls -lagh %{directory}",
            "enter": true
        }
    ]
}
```

## `select-from-list`

```json
{
    "title": "list contents of given folder",
    "description": "not implemented",
    "commands": [
        {
            "action": "select-from-list",
            "variable_name": "period",
            "list": ["1h","2h","4h","1d"]
        },
        {
            "action": "send-to-pane",
            "code": "ls -lagh %{directory}",
            "enter": true
        }
    ]
}
```
