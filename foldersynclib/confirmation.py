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

Sync confirmation
"""


from tkinter import Toplevel, Text
from tkinter.ttk import Button, Label, PanedWindow, Style, Frame
from foldersynclib.scrollbar import AutoScrollbar as Scrollbar
from foldersynclib.constantes import convert_size
from os import scandir
from os.path import getsize


class Confirmation(Toplevel):
    """
    Confirmation window that recapitulate the changes that will be made
    during the synchronisation.
    """

    def __init__(self, master, a_copier, a_supp, a_supp_avant_cp, original,
                 sauvegarde, show_size):
        Toplevel.__init__(self, master)
        self.geometry("%ix%i" % (self.winfo_screenwidth(),
                                 self.winfo_screenheight()))
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.title(_("Confirmation"))

        self.a_copier = a_copier
        self.a_supp = a_supp
        self.a_supp_avant_cp = a_supp_avant_cp

        h = max(len(a_supp), len(a_copier))

        style = Style(self)
        style.configure("text.TFrame", background="white", relief="sunken")

        Label(self,
              text=_("Synchronization from %(original)s to %(backup)s") % {"original": original, "backup": sauvegarde}).grid(row=0, columnspan=2, padx=10, pady=10)
        paned = PanedWindow(self, orient='horizontal')
        paned.grid(row=1, columnspan=2, sticky="eswn", padx=(10, 4), pady=4)
        paned.columnconfigure(0, weight=1)
        paned.columnconfigure(1, weight=1)
        paned.rowconfigure(1, weight=1)

        # --- copy
        frame_copie = Frame(paned)
        frame_copie.columnconfigure(0, weight=1)
        frame_copie.rowconfigure(1, weight=1)
        paned.add(frame_copie, weight=1)
        Label(frame_copie, text=_("To copy:")).grid(row=0, columnspan=2,
                                                    padx=(10, 4), pady=4)
        f_copie = Frame(frame_copie, style="text.TFrame", borderwidth=1)
        f_copie.columnconfigure(0, weight=1)
        f_copie.rowconfigure(0, weight=1)
        f_copie.grid(row=1, column=0, sticky="ewsn")
        txt_copie = Text(f_copie, height=h, wrap="none",
                         highlightthickness=0, relief="flat")
        txt_copie.grid(row=0, column=0, sticky="eswn")
        scrollx_copie = Scrollbar(frame_copie, orient="horizontal",
                                  command=txt_copie.xview)
        scrolly_copie = Scrollbar(frame_copie, orient="vertical",
                                  command=txt_copie.yview)
        scrollx_copie.grid(row=2, column=0, sticky="ew")
        scrolly_copie.grid(row=1, column=1, sticky="ns")
        txt_copie.configure(yscrollcommand=scrolly_copie.set,
                            xscrollcommand=scrollx_copie.set)
        txt_copie.insert("1.0", "\n".join(a_copier))
        txt_copie.configure(state="disabled")
        self._size_copy = Label(frame_copie)
        self._size_copy.grid(row=3, column=0)

        # --- deletion
        frame_supp = Frame(paned)
        frame_supp.columnconfigure(0, weight=1)
        frame_supp.rowconfigure(1, weight=1)
        paned.add(frame_supp, weight=1)
        Label(frame_supp, text=_("To remove:")).grid(row=0, columnspan=2,
                                                     padx=(4, 10), pady=4)
        f_supp = Frame(frame_supp, style="text.TFrame", borderwidth=1)
        f_supp.columnconfigure(0, weight=1)
        f_supp.rowconfigure(0, weight=1)
        f_supp.grid(row=1, column=0, sticky="ewsn")
        txt_supp = Text(f_supp, height=h, wrap="none",
                        highlightthickness=0, relief="flat")
        txt_supp.grid(row=0, column=0, sticky="eswn")
        scrollx_supp = Scrollbar(frame_supp, orient="horizontal",
                                 command=txt_supp.xview)
        scrolly_supp = Scrollbar(frame_supp, orient="vertical",
                                 command=txt_supp.yview)
        scrollx_supp.grid(row=2, column=0, sticky="ew")
        scrolly_supp.grid(row=1, column=1, sticky="ns")
        txt_supp.configure(yscrollcommand=scrolly_supp.set,
                           xscrollcommand=scrollx_supp.set)
        txt_supp.insert("1.0", "\n".join(a_supp))
        txt_supp.configure(state="disabled")
        self._size_supp = Label(frame_supp)
        self._size_supp.grid(row=3, column=0)

        Button(self, command=self.ok,
               text="Ok").grid(row=3, column=0, sticky="e",
                               padx=(10, 4), pady=(4, 10))
        Button(self, text=_("Cancel"),
               command=self.destroy).grid(row=3, column=1, sticky="w",
                                          padx=(4, 10), pady=(4, 10))
        self.wait_visibility()
        self.grab_set()
        self.transient(self.master)
        if show_size:
            self.compute_size()

    def compute_size(self):
        """Compute and display total size of files to copy/to delete."""
        def size(path):
            s = 0
            try:
                with scandir(path) as content:
                    for f in content:
                        try:
                            if f.is_file():
                                s += f.stat().st_size
                            else:
                                s += size(f.path)
                        except FileNotFoundError:
                            pass
            except NotADirectoryError:
                s = getsize(path)
            return s

        size_copy = 0
        size_supp = 0

        for path in self.a_copier:
            size_copy += size(path)
        for path in self.a_supp:
            size_supp += size(path)
        self._size_copy.configure(text=_("Copy: %(size)s") % {'size': convert_size(size_copy)})
        self._size_supp.configure(text=_("Remove: %(size)s") % {'size': convert_size(size_supp)})

    def ok(self):
        """Close dialog and start sync."""
        self.grab_release()
        self.master.copie_supp(self.a_copier, self.a_supp, self.a_supp_avant_cp)
        self.destroy()
