# snux

SNippets in tmUX: a popup that lists snippets and sends the chosen one to a tmux pane. Rolf's own project
(`github.com/rolflobker/snux`, public). The snippets are a second repo: `~/projects/snux-snippets`.

## How it runs on this laptop (set up on 2026-10-31 from a dotfiles session)

- Python runs in a venv in this folder: `.venv/`, with `requirements.txt` (the package `pyfzf-iter`, its module is `pyfzf`).
  `.venv/` is excluded in `.git/info/exclude`, so it does not show in `git status`.
- snux reads the snippets from `~/.config/snux/snippets/**/*.json`. `~/.config/snux/snippets/public` is a relative link
  to `../../../projects/snux-snippets`. That link is not managed by the dotfiles or the playbook.
- tmux key: `prefix C-o` in `~/dotfiles/configs/tmux/.config/tmux/tmux.conf` runs
  `display-popup -E "$HOME/projects/snux/.venv/bin/python $HOME/projects/snux/snux.py"`.
- A new laptop: the steps are in `~/dotfiles/TODO.CLAUDE.md`, "Install the git projects".

## Set it up again

```bash
cd ~/projects/snux
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
mkdir -p ~/.config/snux/snippets
ln -sfn ../../../projects/snux-snippets ~/.config/snux/snippets/public
```

Test: press `prefix C-o` in tmux. The popup lists the snippets (40 on 2026-10-31).
