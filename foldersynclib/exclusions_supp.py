#! /usr/bin/python3
# -*- coding:Utf-8 -*-
"""
FolderSync - Folder synchronization software
Copyright 2017-2018 Juliette Monsel <j_4321@protonmail.com>

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

ExclusionsSupp
"""

from tkinter import Toplevel, Listbox, StringVar, PhotoImage, TclError
from tkinter.ttk import Frame, Button, Style
from foldersynclib.scrollbar import AutoScrollbar as Scrollbar
from foldersynclib.constants import CONFIG, IM_OPEN, IM_DOC, IM_SUPP
from foldersynclib.constants import save_config, askdirectories, askfiles
from os.path import dirname, exists
from re import split


class ExclusionsSupp(Toplevel):
    """List of paths that will be excluded from removal."""
    def __init__(self, master):
        Toplevel.__init__(self, master)
        self.protocol("WM_DELETE_WINDOW", self.quitter)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(2, weight=1)
        self.rowconfigure(0, weight=1)
        self.title(_("Exclusions"))
        self.transient(master)
        self.grab_set()

        self.last_path = ""  # last opened path

        self.img_open = PhotoImage(file=IM_OPEN)
        self.img_doc = PhotoImage(file=IM_DOC)
        self.img_supp = PhotoImage(file=IM_SUPP)

        style = Style(self)
        style.configure("list.TFrame", background="white", relief="sunken")

        frame = Frame(self)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        frame.grid(row=0, columnspan=3, sticky="eswn", padx=10, pady=(10, 4))

        listbox_frame = Frame(frame, borderwidth=1, style="list.TFrame")
        listbox_frame.columnconfigure(0, weight=1)
        listbox_frame.rowconfigure(0, weight=1)
        listbox_frame.grid(row=0, column=0, sticky="nswe")

        self.listvar = StringVar(self, value=CONFIG.get("Defaults", "exclude_supp"))
        self.exclude_list = split(r'(?<!\\) ',
                                  CONFIG.get("Defaults", "exclude_supp"))

        self.listbox = Listbox(listbox_frame, highlightthickness=0,
                               listvariable=self.listvar, selectmode='extended')
        self.listbox.grid(sticky="eswn")
        self.listbox.selection_clear(0, 'end')

        scroll_x = Scrollbar(frame, orient="horizontal",
                             command=self.listbox.xview)
        scroll_x.grid(row=1, column=0, sticky="ew")
        scroll_y = Scrollbar(frame, orient="vertical",
                             command=self.listbox.yview)
        scroll_y.grid(row=0, column=1, sticky="ns")
        self.listbox.configure(xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)

        Button(self, image=self.img_doc,
               command=self.add_doc).grid(row=1, column=0, sticky="e",
                                          padx=(10, 4), pady=(4, 10))
        Button(self, image=self.img_open,
               command=self.add_dir).grid(row=1, column=1,
                                          padx=4, pady=(4, 10))
        Button(self, image=self.img_supp,
               command=self.rem).grid(row=1, column=2, sticky="w",
                                      padx=(4, 10), pady=(4, 10))
        self.geometry("500x400")

    def add_doc(self):
        path = self.listbox.get('active')
        if exists(path):
            docs = askfiles(path, parent=self)
        else:
            docs = askfiles('', parent=self)
        if docs and docs[0]:
            for d in docs:
                d = d.replace(" ", "\ ")
                if d not in self.exclude_list:
                    self.exclude_list.append(d)
            self.last_path = dirname(docs[-1])
            self.listvar.set(" ".join(self.exclude_list))

    def add_dir(self):
        path = self.listbox.get('active')
        if exists(path):
            dirs = askdirectories(path, parent=self)
        else:
            dirs = askdirectories('', parent=self)
        if dirs and dirs[0]:
            for d in dirs:
                d = d.replace(" ", "\ ")
                if d not in self.exclude_list:
                    self.exclude_list.append(d)
            self.last_path = dirs[-1]
            self.listvar.set(" ".join(self.exclude_list))

    def rem(self):
        sel = self.listbox.curselection()
        for index in reversed(sel):
            txt = self.listbox.get(index)
            self.exclude_list.remove(txt.replace(" ", "\ "))
            self.listbox.delete(index)

    def quitter(self):
        CONFIG.set("Defaults", "exclude_supp", " ".join(self.exclude_list))
        save_config()
        self.destroy()
