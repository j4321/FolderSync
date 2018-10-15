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

ExclusionCopie
"""


from tkinter import Toplevel, Listbox, StringVar, PhotoImage
from tkinter.ttk import Frame, Button, Style, Entry
from foldersynclib.scrollbar import AutoScrollbar as Scrollbar
from foldersynclib.constants import CONFIG, IM_SUPP, IM_ADD, save_config
from re import split


class ExclusionsCopie(Toplevel):
    """
    List of file/folder names and file extensions (e.g. *.pyc) that will be
    excluded from the copy.
    """
    def __init__(self, master):
        Toplevel.__init__(self, master)
        self.protocol("WM_DELETE_WINDOW", self.quitter)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.title(_("Exclusions"))
        self.transient(master)
        self.grab_set()
        self.img_supp = PhotoImage(file=IM_SUPP)
        self.img_add = PhotoImage(file=IM_ADD)

        style = Style(self)
        style.configure("list.TFrame", background="white", relief="sunken")

        frame = Frame(self)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        frame.grid(row=0, columnspan=2, sticky="eswn", padx=10, pady=(10, 4))

        listbox_frame = Frame(frame, borderwidth=1, style="list.TFrame")
        listbox_frame.columnconfigure(0, weight=1)
        listbox_frame.rowconfigure(0, weight=1)
        listbox_frame.grid(row=0, column=0, sticky="eswn")

        self.listvar = StringVar(self, value=CONFIG.get("Defaults", "exclude_copie"))
        self.exclude_list = split(r'(?<!\\) ',
                                  CONFIG.get("Defaults", "exclude_copie"))

        self.listbox = Listbox(listbox_frame, highlightthickness=0,
                               listvariable=self.listvar)
        self.listbox.grid(sticky="eswn")

        scroll_x = Scrollbar(frame, orient="horizontal",
                             command=self.listbox.xview)
        scroll_x.grid(row=1, column=0, sticky="ew")
        scroll_y = Scrollbar(frame, orient="vertical",
                             command=self.listbox.yview)
        scroll_y.grid(row=0, column=1, sticky="ns")
        self.listbox.configure(xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)

        Button(self, image=self.img_add,
               command=self.add).grid(row=1, column=0, sticky="e",
                                      padx=(10, 4), pady=(4, 10))
        Button(self, image=self.img_supp,
               command=self.rem).grid(row=1, column=1, sticky="w",
                                      padx=(4, 10), pady=(4, 10))
        self.geometry("200x300")

    def add(self):
        def ok(event=None):
            txt = e.get()
            txt = txt.strip().replace(" ", "\ ")
            if txt and txt not in self.exclude_list:
                self.exclude_list.append(txt)
                self.listvar.set(" ".join(self.exclude_list))
            top.destroy()
        top = Toplevel(self)
        top.transient(self)
        top.grab_set()
        e = Entry(top)
        e.pack(expand=True, fill="x", padx=10, pady=(10, 4))
        e.focus_set()
        e.bind("<Key-Return>", ok)
        Button(top, text="Ok", command=ok).pack(padx=10, pady=(4, 10))

    def rem(self):
        sel = self.listbox.curselection()
        if sel:
            sel = sel[0]
            txt = self.listbox.get(sel)
            self.exclude_list.remove(txt)
            self.listbox.delete(sel)

    def quitter(self):
        CONFIG.set("Defaults", "exclude_copie", " ".join(self.exclude_list))
        save_config()
        self.destroy()
