#!/usr/bin/env python

import requests
import re
import pandas as pd
import curses
from time import sleep
from curses import wrapper
import sys
from io import StringIO
from pyfzf import FzfPrompt


def apachestatus(server):
    url = f"https://{server}/server-status?auto"
    response = requests.get(url=url).text
    lines = response.splitlines()
    dict = {}
    del lines[0]
    for line in lines:
        if ": " in line:
            key = line.split(": ")[0]
            value = line.split(": ")[1]
            dict[key] = value
    return dict


def apachestatus_html(server):
    url = f"https://{server}/server-status"
    html = requests.get(url=url).text
    return html


def __topsites(server):
    tables = pd.read_html(StringIO(apachestatus_html(server)))
    connections = tables[1]
    top = str(connections["VHost"].value_counts().head(10)).splitlines()
    del top[0]
    del top[-1]
    return top


# status = apachestatus(server)
# htmlstatus = apachestatus_html(server)
# topsites = __topsites(htmlstatus)
# scoreboard = status["Scoreboard"]
# print(scoreboard)


def scoreboard(screen, server):
    curses.noraw()
    screen.nodelay(True)
    cursor_mode = curses.curs_set(0)

    w_status = curses.newpad(10, 40)
    w_status.scrollok(True)
    w_topsites = curses.newpad(50, 40)
    w_topsites.scrollok(True)

    status = apachestatus(server)
    scoreboard = status["Scoreboard"]

    topsites = __topsites(server)

    screen.addstr(0, 0, server)

    try:
        while True:
            # screen.addstr(0, 0, scoreboard)
            # screen.addstr(1, 0, str(topsites))
            w_status.addstr(0, 0, str(scoreboard))
            w_status.refresh(0, 0, 2, 0, 15, 160)

            row = 0
            w_topsites.clear()
            for site in topsites:
                site = site.replace(":84", "")
                w_topsites.addstr(row, 0, site)
                row += 1
            w_topsites.refresh(0, 0, 2, 50, 10, 120)

            # screen.refresh()
            for i in range(10):
                if screen.getch() == ord("q"):
                    return
                sleep(0.1)

            status = apachestatus(server)
            topsites = __topsites(server)
            scoreboard = status["Scoreboard"]
    finally:
        curses.curs_set(cursor_mode)
        screen.erase()


server = sys.argv[1]

# fzf = FzfPrompt(default_options="--reverse --bind 'ctrl-j:jump-accept'")
#
# servers = []
# for i in range(160, 220):
#     s = f"s{i}.webhostingserver.nl"
#     print(s)
#     servers.append(s)
# for i in range(220, 251):
#     s = f"s{i}.webhostingserver.nl"
#     servers.append(s)

# server = fzf.prompt(servers)
wrapper(scoreboard, server)
