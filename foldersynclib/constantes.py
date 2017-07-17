#! /usr/bin/python3
# -*- coding:Utf-8 -*-
"""
FolderSync - Folder synchronization software
Copyright 2017 Juliette Monsel <j_4321@protonmail.com>

FolderSync is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

FolderSync is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

Constants
"""

import pkg_resources
VERSION = pkg_resources.require("FolderSync")[0].version

import os
from sys import platform
from configparser import ConfigParser
from tkinter import filedialog
from subprocess import check_output, CalledProcessError

# fichier de config
PATH = os.path.join(os.path.expanduser("~"), ".foldersync")
i = 0
LOG_COPIE = os.path.join(PATH, "copie%i.log")
LOG_SUPP = os.path.join(PATH, "suppression%i.log")

while os.path.exists(LOG_COPIE % i) or os.path.exists(LOG_SUPP % i):
    i += 1
LOG_COPIE = LOG_COPIE % i
LOG_SUPP = LOG_SUPP % i

with open(LOG_COPIE, "w") as log_copie:
    log_copie.write("###  foldersync : log de la copie  ###\n\n")

with open(LOG_SUPP, "w") as log_supp:
    log_supp.write("###  foldersync : log de la suppression  ###\n\n")

PATH_CONFIG = os.path.join(PATH, "foldersync.ini")
CONFIG = ConfigParser()
if not os.path.exists(PATH_CONFIG):
    if not os.path.exists(PATH):
        os.mkdir(PATH)
    CONFIG.add_section("Default")
    CONFIG.set("Defaults", "copy_links", "True")
    CONFIG.set("Defaults", "exclude_copie", "")
    CONFIG.set("Defaults", "exclude_supp", "")
    CONFIG.add_section("Recent")
    CONFIG.set("Recent", "orig", "")
    CONFIG.set("Recent", "sauve", "")
    CONFIG.add_section("Favoris")
    CONFIG.set("Favoris", "orig", "")
    CONFIG.set("Favoris", "sauve", "")
else:
    CONFIG.read(PATH_CONFIG)

r_o = CONFIG.get("Recent", "orig").split(", ")
r_s = CONFIG.get("Recent", "sauve").split(", ")
if r_o == ['']:
    RECENT = []
else:
    RECENT = list(zip(r_o, r_s))

f_o = CONFIG.get("Favoris", "orig").split(", ")
f_s = CONFIG.get("Favoris", "sauve").split(", ")
if f_o == ['']:
    FAVORIS = []
else:
    FAVORIS = list(zip(f_o, f_s))

# Images
IMAGE_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), "images")
IM_ICON = os.path.join(IMAGE_PATH, "icon.png")
IM_ABOUT = os.path.join(IMAGE_PATH, "about.png")
IM_COLLAPSE = os.path.join(IMAGE_PATH, "collapse_all.png")
IM_EXPAND = os.path.join(IMAGE_PATH, "expand_all.png")
IM_SYNC = os.path.join(IMAGE_PATH, "sync2.png")
IM_PREV = os.path.join(IMAGE_PATH, "prev2.png")
IM_OPEN = os.path.join(IMAGE_PATH, "open.png")
IM_DOC = os.path.join(IMAGE_PATH, "doc.png")
IM_PLUS = os.path.join(IMAGE_PATH, "plus_m.png")
IM_MOINS = os.path.join(IMAGE_PATH, "moins_m.png")
IM_ADD = os.path.join(IMAGE_PATH, "add.png")
IM_SUPP = os.path.join(IMAGE_PATH, "supp.png")
IM_CHECKED = os.path.join(IMAGE_PATH, "checked.png")
IM_UNCHECKED = os.path.join(IMAGE_PATH, "unchecked.png")
IM_TRISTATE = os.path.join(IMAGE_PATH, "tristate.png")

# filebrowser
ZENITY = False
if platform != "nt":
    paths = os.environ['PATH'].split(":")
    for path in paths:
        if os.path.exists(os.path.join(path, "zenity")):
            ZENITY = True

try:
    import tkfilebrowser as tkfb
except ImportError:
    tkfb = False

def askdirectory(initialdir, title="Ouvrir", **options):
    """ folder browser:
        initialdir: directory where the filebrowser is opened
    """
    if tkfb:
        return tkfb.askopendirname(title=title, initialdir=initialdir,
                                   **options)
    elif ZENITY:
        try:
            args = ["zenity", "--file-selection",  "--filename", initialdir,
                    "--directory", "--title", title]
            folder = check_output(args).decode("utf-8").strip()
            return folder
        except CalledProcessError:
            return ""
        except Exception:
            return filedialog.askdirectory(title=title, initialdir=initialdir,
                                           **options)
    else:
        return filedialog.askdirectory(title=title, initialdir=initialdir,
                                       **options)

def askdirectories(initialdir, title="Séléctionner", **options):
    """ folder selector:
        initialdir: directory where the filebrowser is opened
    """
    if tkfb:
        return tkfb.askopendirnames(title=title, initialdir=initialdir,
                                    **options)
    elif ZENITY:
        try:
            args = ["zenity", "--file-selection",  "--filename", initialdir,
                    "--directory", "--multiple", "--title", title]
            folder = check_output(args).decode("utf-8").strip()
            return folder.split('|')
        except CalledProcessError:
            return ""
        except Exception:
            return filedialog.askdirectory(title=title, initialdir=initialdir,
                                           **options)
    else:
        return filedialog.askdirectory(title=title, initialdir=initialdir,
                                       **options)

def askfiles(initialdir, title="Séléctionner", **options):
    """ files selector:
        initialdir: directory where the filebrowser is opened
    """
    if tkfb:
        return tkfb.askopenfilenames(title=title, initialdir=initialdir,
                                     **options)
    elif ZENITY:
        try:
            args = ["zenity", "--file-selection",  "--filename", initialdir,
                    "--multiple", "--title", title]
            files = check_output(args).decode("utf-8").strip()
            return files.split('|')
        except CalledProcessError:
            return ""
        except Exception:
            return filedialog.askopenfilenames(title=title, initialdir=initialdir,
                                               **options)
    else:
        return filedialog.askopenfilenames(title=title, initialdir=initialdir,
                                       **options)

def save_config():
    # save recent files
    orig = []
    sauve = []
    for o,s in RECENT:
        orig.append(o)
        sauve.append(s)
    CONFIG.set("Recent", "orig", ", ".join(orig))
    CONFIG.set("Recent", "sauve", ", ".join(sauve))
    orig = []
    sauve = []
    # save favorites
    for o,s in FAVORIS:
        orig.append(o)
        sauve.append(s)
    CONFIG.set("Favoris", "orig", ", ".join(orig))
    CONFIG.set("Favoris", "sauve", ", ".join(sauve))
    with open(PATH_CONFIG, 'w') as fichier:
        CONFIG.write(fichier)
