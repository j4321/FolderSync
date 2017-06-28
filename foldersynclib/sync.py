#! /usr/bin/python3
# -*- coding:utf-8 -*-
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

Main GUI
"""

### TODO:
# tester os.scandir

from os.path import join, splitext, exists, isdir, islink, isfile, getmtime, abspath, commonpath
from os import listdir, chdir
from re import split
from threading import Thread
from queue import Queue
from subprocess import run, PIPE
from tkinter import Tk, PhotoImage, Menu, BooleanVar
from tkinter.ttk import Label, Button, PanedWindow, Entry, Style, Frame, Progressbar
from tkinter.messagebox import showerror, askokcancel, showwarning
from foldersynclib.checkboxtreeview import CheckboxTreeview
from foldersynclib.scrollbar import AutoScrollbar as Scrollbar
from foldersynclib.constantes import FAVORIS, RECENT, CONFIG, askdirectory
from foldersynclib.constantes import IM_OPEN, IM_PLUS, IM_MOINS, IM_ICON, IM_ABOUT
from foldersynclib.constantes import IM_PREV, IM_SYNC, IM_EXPAND, IM_COLLAPSE
from foldersynclib.constantes import LOG_COPIE, LOG_SUPP, save_config
from foldersynclib.confirmation import Confirmation
from foldersynclib.about import About
from foldersynclib.exclusions_copie import ExclusionsCopie
from foldersynclib.exclusions_supp import ExclusionsSupp

class Sync(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.title("FolderSync")
        self.geometry("%ix%i" % (self.winfo_screenwidth(), self.winfo_screenheight()))
        self.protocol("WM_DELETE_WINDOW", self.quitter)
        self.icon = PhotoImage(master=self, file=IM_ICON)
        self.iconphoto(True, self.icon)
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)

        self.img_about = PhotoImage(master=self, file=IM_ABOUT)
        self.img_open = PhotoImage(master=self, file=IM_OPEN)
        self.img_plus = PhotoImage(master=self, file=IM_PLUS)
        self.img_moins = PhotoImage(master=self, file=IM_MOINS)
        self.img_sync = PhotoImage(master=self, file=IM_SYNC)
        self.img_prev = PhotoImage(master=self, file=IM_PREV)
        self.img_expand = PhotoImage(master=self, file=IM_EXPAND)
        self.img_collapse = PhotoImage(master=self, file=IM_COLLAPSE)

        self.original = ""
        self.sauvegarde = ""
        # liste des fichiers/dossiers à supprimer avant de lancer la copie car
        # ils sont de nature différente sur l'original et la sauvegarde
        self.pb_chemins = []
        self.err_copie = False
        self.err_supp  = False

        # filenames and extensions that will not be copied
        exclude_list = split(r'(?<!\\) ',
                             CONFIG.get("Defaults", "exclude_copie"))
        self.exclude_names = []
        self.exclude_ext = []
        for elt in exclude_list:
            if elt:
                if elt[:2] == "*.":
                    self.exclude_ext.append(elt[1:])
                else:
                    self.exclude_names.append(elt.replace("\ ", " "))

        # paths that will not be deleted
        self.exclude_path_supp = [ch.replace("\ ", " ") for ch in
                                  split(r'(?<!\\) ',
                                        CONFIG.get("Defaults", "exclude_supp"))
                                  if ch]
#        while "" in self.exclude_path_supp:
#            self.exclude_path_supp.remove("")

        self.q_copie = Queue()
        self.q_supp = Queue()
        # True si une copie / suppression est en cours
        self.is_running_copie = False
        self.is_running_supp = False

        self.style = Style(self)
        self.style.theme_use("clam")
        self.style.configure("TProgressbar", troughcolor ='lightgray',
						     background='#387EF5', lightcolor="#5D95F5",
							 darkcolor="#2758AB")
        self.style.map("TProgressbar", lightcolor=[("disabled", "white")],
					   darkcolor=[("disabled", "gray")])
        self.style.configure("folder.TButton", padding=1)
        # menu
        self.menu = Menu(self, tearoff=False)
        self.configure(menu=self.menu)

        ## emplacements récents
        self.menu_recent = Menu(self.menu, tearoff=False)
        if RECENT:
            for ch_o, ch_s in RECENT:
                self.menu_recent.add_command(label="%s -> %s" % (ch_o, ch_s),
                                             command=lambda o=ch_o, s=ch_s: self.open(o, s))
        else:
            self.menu.entryconfigure(0, state="disabled")

        ## emplacements favoris
        self.menu_fav = Menu(self.menu, tearoff=False)
        self.menu_fav_del = Menu(self.menu_fav, tearoff=False)
        self.menu_fav.add_command(label="Ajouter", image=self.img_plus,
                                  compound="left", command=self.add_fav)
        self.menu_fav.add_cascade(label="Supprimer", image=self.img_moins,
                                  compound="left", menu=self.menu_fav_del)
        for ch_o, ch_s in FAVORIS:
            label = "%s -> %s" % (ch_o, ch_s)
            self.menu_fav.add_command(label=label,
                                      command=lambda o=ch_o, s=ch_s: self.open(o, s))
            self.menu_fav_del.add_command(label=label,
                                          command=lambda nom=label: self.del_fav(nom))
        if not FAVORIS:
            self.menu_fav.entryconfigure(1, state="disabled")

        ## accès aux fichiers log
        menu_log = Menu(self.menu, tearoff=False)
        menu_log.add_command(label="Copie", command=self.open_log_copie)
        menu_log.add_command(label="Suppression", command=self.open_log_suppression)

        ## paramètres, préférences
        menu_params = Menu(self.menu, tearoff=False)
        self.copy_links = BooleanVar(self, value=CONFIG.getboolean("Defaults", "copy_links"))
        menu_params.add_checkbutton(label="Copier les liens",
                                    variable=self.copy_links,
                                    command=self.toggle_copy_links)
        menu_params.add_command(label="Exclusions copie", command=self.exclusion_copie)
        menu_params.add_command(label="Exclusions supp", command=self.exclusion_supp)

        self.menu.add_cascade(label="Récents", menu=self.menu_recent)
        self.menu.add_cascade(label="Favoris", menu=self.menu_fav)
        self.menu.add_cascade(label="Log", menu=menu_log)
        self.menu.add_cascade(label="Paramètres", menu=menu_params)
        self.menu.add_command(image=self.img_prev, compound="center",
                              command=self.list_files_to_sync)
        self.menu.add_command(image=self.img_sync, compound="center",
                              state="disabled", command=self.synchronise)
        self.menu.add_command(image=self.img_about, compound="center",
                              command=lambda: About(self))

#        # sélection chemins
        frame_paths= Frame(self)
        frame_paths.grid(row=0, sticky="ew", pady=(10,0))
        frame_paths.columnconfigure(0, weight=1)
        frame_paths.columnconfigure(1, weight=1)
        f1 = Frame(frame_paths, height=26)
        f2 = Frame(frame_paths, height=26)
        f1.grid(row=0, column=0, sticky="ew")
        f2.grid(row=0, column=1, sticky="ew")
        f1.grid_propagate(False)
        f2.grid_propagate(False)
        f1.columnconfigure(1, weight=1)
        f2.columnconfigure(1, weight=1)

        ## chemin vers original
        Label(f1, text="Original").grid(row=0, column=0, padx=(10,4))
        self.entry_orig = Entry(f1)
        self.entry_orig.grid(row=0, column=1, sticky="ew", padx=(4,2))
        self.b_open_orig = Button(f1, image=self.img_open,
                                  style="folder.TButton",
                                  command=self.open_orig)
        self.b_open_orig.grid(row=0, column=2, padx=(1,8))
        ## chemin vers sauvegarde
        Label(f2, text="Sauvegarde").grid(row=0, column=0, padx=(8,4))
        self.entry_sauve = Entry(f2)
        self.entry_sauve.grid(row=0, column=1, sticky="ew", padx=(4,2))
        self.b_open_sauve = Button(f2, image=self.img_open, width=2,
                                   style="folder.TButton",
                                   command=self.open_sauve)
        self.b_open_sauve.grid(row=0, column=5, padx=(1,10))

#        self.b_prev = Button(frame_paths, image=self.img_prev,
#                             command=self.list_files_to_sync)
#        self.b_prev.grid(row=1, column=4, padx=4)
#
#        self.b_sync = Button(frame_paths, image=self.img_sync,
#                             command=self.synchronise)
#        self.b_sync.grid(row=1, column=5, padx=(4,10))
#        self.b_sync.state(("disabled",))
#        self.b_prev = Button(self, image=self.img_prev,
#                             command=self.list_files_to_sync)
#        self.b_prev.grid(row=1, sticky="ew", pady=(4,10), padx=10)


        paned = PanedWindow(self, orient='horizontal')
        paned.grid(row=2, sticky="eswn")
        paned.rowconfigure(0, weight=1)
        paned.columnconfigure(1, weight=1)
        paned.columnconfigure(0, weight=1)

        # côté gauche
        frame_left = Frame(paned)
        paned.add(frame_left, weight=1)
        frame_left.rowconfigure(3, weight=1)
        frame_left.columnconfigure(0, weight=1)

        ## fichiers à copier
        f_left = Frame(frame_left)
        f_left.columnconfigure(2, weight=1)
        f_left.grid(row=2, columnspan=2, pady=(4,2), padx=(10,4), sticky="ew")

        Label(f_left, text="À copier").grid(row=0, column=2)
        frame_copie = Frame(frame_left)
        frame_copie.rowconfigure(0, weight=1)
        frame_copie.columnconfigure(0, weight=1)
        frame_copie.grid(row=3, column=0, sticky="eswn", columnspan=2,
                         pady=(2,4), padx=(10,4))
        self.tree_copie = CheckboxTreeview(frame_copie, selectmode='none',
                                           show='tree')
        self.b_expand_copie = Button(f_left, image=self.img_expand,
                                     style="folder.TButton",
                                     command=self.tree_copie.expand_all)
        self.b_expand_copie.grid(row=0, column=0)
        self.b_expand_copie.state(("disabled",))
        self.b_collapse_copie = Button(f_left, image=self.img_collapse,
                                       style="folder.TButton",
                                       command=self.tree_copie.collapse_all)
        self.b_collapse_copie.grid(row=0, column=1, padx=4)
        self.b_collapse_copie.state(("disabled",))
        self.tree_copie.tag_configure("warning", foreground="red")
        self.tree_copie.tag_configure("link", font="tkDefaultFont 9 italic", foreground="blue")
        self.tree_copie.tag_bind("warning", "<Button-1>", self.show_warning)
        self.tree_copie.grid(row=0, column=0, sticky="eswn")
        self.scroll_y_copie = Scrollbar(frame_copie, orient="vertical",
                                        command=self.tree_copie.yview)
        self.scroll_y_copie.grid(row=0, column=1, sticky="ns")
        self.scroll_x_copie = Scrollbar(frame_copie, orient="horizontal",
                                        command=self.tree_copie.xview)
        self.scroll_x_copie.grid(row=1, column=0, sticky="ew")
        self.tree_copie.configure(yscrollcommand=self.scroll_y_copie.set,
                                  xscrollcommand=self.scroll_x_copie.set)
        self.pbar_copie = Progressbar(frame_left, orient="horizontal",
                                      mode="determinate")
        self.pbar_copie.grid(row=4, columnspan=2, sticky="ew",
                             padx=(10,4), pady=4)
        self.pbar_copie.state(("disabled",))


        # côté droit
        frame_right = Frame(paned)
        paned.add(frame_right, weight=1)
        frame_right.rowconfigure(3, weight=1)
        frame_right.columnconfigure(0, weight=1)

        ## fichiers à supprimer
        f_right = Frame(frame_right)
        f_right.columnconfigure(2, weight=1)
        f_right.grid(row=2, columnspan=2, pady=(4,2), padx=(4,10), sticky="ew")
        Label(f_right, text="À supprimer").grid(row=0, column=2)
        frame_supp = Frame(frame_right)
        frame_supp.rowconfigure(0, weight=1)
        frame_supp.columnconfigure(0, weight=1)
        frame_supp.grid(row=3, columnspan=2, sticky="eswn", pady=(2,4), padx=(4,10))
        self.tree_supp = CheckboxTreeview(frame_supp, selectmode='none',
                                          show='tree')
        self.b_expand_supp = Button(f_right, image=self.img_expand,
                                    style="folder.TButton",
                                    command=self.tree_supp.expand_all)
        self.b_expand_supp.grid(row=0, column=0)
        self.b_expand_supp.state(("disabled",))
        self.b_collapse_supp = Button(f_right, image=self.img_collapse,
                                      style="folder.TButton",
                                      command=self.tree_supp.collapse_all)
        self.b_collapse_supp.grid(row=0, column=1, padx=4)
        self.b_collapse_supp.state(("disabled",))
        self.tree_supp.grid(row=0, column=0, sticky="eswn")
        self.scroll_y_supp = Scrollbar(frame_supp, orient="vertical",
                                        command=self.tree_supp.yview)
        self.scroll_y_supp.grid(row=0, column=1, sticky="ns")
        self.scroll_x_supp = Scrollbar(frame_supp, orient="horizontal",
                                        command=self.tree_supp.xview)
        self.scroll_x_supp.grid(row=1, column=0, sticky="ew")
        self.tree_supp.configure(yscrollcommand=self.scroll_y_supp.set,
                                  xscrollcommand=self.scroll_x_supp.set)
        self.pbar_supp = Progressbar(frame_right, orient="horizontal",
                                      mode="determinate")
        self.pbar_supp.grid(row=4, columnspan=2, sticky="ew",
                             padx=(4,10), pady=4)
        self.pbar_supp.state(("disabled",))


#        # lancer synchronisation
#        self.b_sync = Button(self, image=self.img_sync,
#                             command=self.synchronise)
#        self.b_sync.grid(row=3, sticky="ew", pady=(4,10), padx=10)
#        self.b_sync.state(("disabled",))

        # bindings
        self.entry_orig.bind("<Key-Return>", self.list_files_to_sync)
        self.entry_sauve.bind("<Key-Return>", self.list_files_to_sync)

    def exclusion_supp(self):
        excl = ExclusionsSupp(self)
        self.wait_window(excl)
        # paths that will not be deleted
        self.exclude_path_supp = [ch.replace("\ ", " ") for ch in
                                  split(r'(?<!\\) ',
                                        CONFIG.get("Defaults", "exclude_supp"))
                                  if ch]

    def exclusion_copie(self):
        excl = ExclusionsCopie(self)
        self.wait_window(excl)
        exclude_list = CONFIG.get("Defaults", "exclude_copie").split(" ")
        self.exclude_names = []
        self.exclude_ext = []
        for elt in exclude_list:
            if elt:
                if elt[:2] == "*.":
                    self.exclude_ext.append(elt[2:])
                else:
                    self.exclude_names.append(elt)

    def toggle_copy_links(self):
        CONFIG.set("Defaults", "copy_links", str(self.copy_links.get()))

    def open_log_copie(self):
        run(["xdg-open", LOG_COPIE])

    def open_log_suppression(self):
        run(["xdg-open", LOG_SUPP])

    def quitter(self):
        rep = True
        if self.is_running_copie or self.is_running_supp:
            rep = askokcancel("Confirmation", "Une synchronisation est en cours, êtes-vous sur de vouloir quitter ?")
        if rep:
            self.destroy()

    def del_fav(self, nom):
        self.menu_fav.delete(nom)
        self.menu_fav_del.delete(nom)
        FAVORIS.remove(tuple(nom.split(" -> ")))
        save_config()
        if not FAVORIS:
            self.menu_fav.entryconfigure(1, state="disabled")

    def add_fav(self):
        sauvegarde = self.entry_sauve.get()
        original = self.entry_orig.get()
        if original != sauvegarde  and original and sauvegarde :
            if exists(original) and exists(sauvegarde):
                if not (original, sauvegarde) in FAVORIS:
                    FAVORIS.append((original, sauvegarde))
                    save_config()
                    label = "%s -> %s" % (original, sauvegarde)
                    self.menu_fav.entryconfigure(1, state="normal")
                    self.menu_fav.add_command(label=label,
                                              command=lambda o=original, s=sauvegarde: self.open(o, s))
                    self.menu_fav_del.add_command(label=label,
                                                  command=lambda nom=label: self.del_fav(nom))

    def open(self, ch_o, ch_s):
        self.entry_orig.delete(0, "end")
        self.entry_orig.insert(0, ch_o)
        self.entry_sauve.delete(0, "end")
        self.entry_sauve.insert(0, ch_s)
        self.list_files_to_sync()

    def open_sauve(self):
        sauvegarde = askdirectory(self.entry_sauve.get())
        if sauvegarde:
            self.entry_sauve.delete(0, "end")
            self.entry_sauve.insert(0, sauvegarde)

    def open_orig(self):
        original = askdirectory(self.entry_orig.get())
        if original:
            self.entry_orig.delete(0, "end")
            self.entry_orig.insert(0, original)

    def sync(self, original, sauvegarde):
        """ peuple tree_copie avec l'arborescence des fichiers d'original à copier
            vers sauvegarde et tree_supp avec celle des fichiers de sauvegarde à
            supprimer """
        errors = []
        copy_links = self.copy_links.get()
        excl_supp = [path for path in self.exclude_path_supp if commonpath([path, sauvegarde]) == sauvegarde]

        def arbo(tree, parent, n):
            """ affiche l'arborescence complète de parent et renvoie la longueur
                maximale des items (pour gérer la scrollbar horizontale) """
            m = 0
            if isdir(parent):
                try:
                    l = listdir(parent)
                except Exception as e:
                    errors.append(str(e))
                    l = []
                l.sort(key=lambda x: x.lower())
                for item in l:
                    chemin = join(parent, item)
                    if islink(chemin):
                        if copy_links:
                            tree.insert(parent, 'end', chemin, text=item, tags=("whole", "link"))
                            m = max(m, len(item)*9 + 20*(n+1))
                    elif (not item in self.exclude_names) and (not splitext(item)[-1] in self.exclude_ext):
                        tree.insert(parent, 'end', chemin, text=item, tags=("whole",))
                        m = max(m, len(item)*9 + 20*(n+1))
                        if isdir(chemin):
                            m = max(m, arbo(tree, chemin, n+1))
            return m

        def aux(orig, sauve, n, search_supp):
            m_copie = 0
            m_supp = 0
            try:
                lo = listdir(orig)
                ls = listdir(sauve)
            except Exception as e:
                errors.append(str(e))
                lo = []
                ls = []
            lo.sort(key=lambda x: x.lower())
            ls.sort(key=lambda x: x.lower())
            supp = False
            copie = False
            if search_supp:
                for item in ls:
                    chemin_s = join(sauve, item)
                    if not chemin_s in excl_supp and not item in lo:
                        supp = True
                        self.tree_supp.insert(sauve, 'end', chemin_s, text=item,
                                              tags=("whole",))
                        m_supp = max(m_supp, int(len(item)*9 + 20*(n+1)),
                                     arbo(self.tree_supp, chemin_s, n+1))

            for item in lo:
                chemin_o = join(orig, item)
                chemin_s = join(sauve, item)
                if (not item in self.exclude_names) and (not splitext(item)[-1] in self.exclude_ext):
                    if item not in ls:
                        # le dossier / fichier n'est pas dans la sauvegarde
                        if islink(chemin_o):
                            if copy_links:
                                copie = True
                                self.tree_copie.insert(orig, 'end', chemin_o, text=item,
                                                       tags=("whole", "link"))
                                m_copie = max(m_copie, (int(len(item)*9 + 20*(n+1))))
                        else:
                            copie = True
                            self.tree_copie.insert(orig, 'end', chemin_o, text=item,
                                                   tags=("whole",))
                            m_copie = max(m_copie, (int(len(item)*9 + 20*(n+1))),
                                          arbo(self.tree_copie, chemin_o, n+1))
                    elif islink(chemin_o) and exists(chemin_o):
                        # checking the existence prevent from copying broken links
                        if copy_links:
                            if not islink(chemin_s):
                                self.pb_chemins.append(chemin_o)
                                tags = ("whole", "warning", "link")
                            else:
                                tags = ("whole", "link")
                            self.tree_copie.insert(orig, 'end', chemin_o, text=item,
                                                   tags=tags)
                            m_copie = max(m_copie, int(len(item)*9 + 20*(n+1)))
                            copie = True
                    elif isfile(chemin_o):
                        # first check if chemin_s is also a file
                        if isfile(chemin_s):
                            if getmtime(chemin_o)//60 > getmtime(chemin_s)//60:
                                # le fichier f a été modifié depuis la dernière sauvegarde
                                copie = True
                                self.tree_copie.insert(orig, 'end', chemin_o, text=item,
                                                       tags=("whole",))
                        else:
                            self.pb_chemins.append(chemin_o)
                            self.tree_copie.insert(orig, 'end', chemin_o, text=item,
                                                   tags=("whole", "warning"))
                    elif isdir(chemin_o):
                        # to avoid errors due to unrecognized item types (neither file nor folder nor link)
                        if isdir(chemin_s):
                            self.tree_copie.insert(orig, 'end', chemin_o, text=item)
                            self.tree_supp.insert(sauve, 'end', chemin_s, text=item)
                            c, s, mc, ms = aux(chemin_o, chemin_s, n+1, search_supp and (not chemin_s in excl_supp))
                            supp = supp or s
                            copie = copie or c
                            if not c:
                                # nothing to copy
                                self.tree_copie.delete(chemin_o)
                            else:
                                m_copie = max(m_copie, mc, int(len(item)*9 + 20*(n+1)))
                            if not s:
                                # nothing to delete
                                self.tree_supp.delete(chemin_s)
                            else:
                                m_supp = max(m_supp, ms, int(len(item)*9 + 20*(n+1)))
                        else:
                            copie = True
                            self.pb_chemins.append(chemin_o)
                            self.tree_copie.insert(orig, 'end', chemin_o, text=item,
                                                   tags=("whole", "warning"))
                            m_copie = max(m_copie, (int(len(item)*9 + 20*(n+1))),
                                          arbo(self.tree_copie, chemin_o, n+1))
            return copie, supp, m_copie, m_supp

        self.tree_copie.insert("", 0, original, text=original,
                               tags=("checked",), open=True)
        self.tree_supp.insert("", 0, sauvegarde, text=sauvegarde,
                              tags=("checked",), open=True)
        c,s, mc, ms = aux(original, sauvegarde, 1, True)
        if not c:
            self.tree_copie.delete(original)
            self.tree_copie.column("#0", minwidth=0, width=0)
        else:
            mc = max(len(original)*9 + 20, mc)
            self.tree_copie.column("#0", minwidth=mc, width=mc)
        if not s:
            self.tree_supp.delete(sauvegarde)
            self.tree_supp.column("#0", minwidth=0, width=0)
        else:
            ms = max(len(sauvegarde)*9 + 20, mc)
            self.tree_supp.column("#0", minwidth=ms, width=ms)
        return errors

    def show_warning(self, event):
        x, y = event.x, event.y
        elem = event.widget.identify("element", x, y)
        if elem == "padding":
            orig = self.tree_copie.identify_row(y)
            sauve= orig.replace(self.original, self.sauvegarde)
            showwarning("Attention",
                        "%s et %s ne sont pas de même nature (dossier/fichier/lien)" % (orig, sauve),
                        master=self)

    def list_files_to_sync(self, event=None):
        """ display in a treeview the file to copy and the one to delete """
        self.pbar_copie.configure(value=0)
        self.pbar_supp.configure(value=0)
        self.sauvegarde = self.entry_sauve.get()
        self.original = self.entry_orig.get()
        if self.original != self.sauvegarde  and self.original and self.sauvegarde :
            if exists(self.original) and exists(self.sauvegarde):
                o_s = (self.original, self.sauvegarde)
                if o_s in RECENT:
                    RECENT.remove(o_s)
                    self.menu_recent.delete("%s -> %s" % o_s)
                RECENT.insert(0, o_s)
                self.menu_recent.insert_command(0, label="%s -> %s" % o_s,
                                                command=lambda o=self.original, s=self.sauvegarde: self.open(o, s))
                if len(RECENT) == 10:
                    del(RECENT[-1])
                    self.menu_recent.delete(9)
                save_config()
                self.menu.entryconfigure(0, state="normal")
                self.configure(cursor="watch")
                self.toggle_state_gui()
                self.update_idletasks()
                self.update()
                self.efface_tree()
                err = self.sync(self.original, self.sauvegarde)
                self.configure(cursor="")
                self.toggle_state_gui()
                c = self.tree_copie.get_children("")
                s = self.tree_supp.get_children("")
                if not (c or  s):
#                    self.b_sync.state(("disabled",))
                    self.menu.entryconfigure(5, state="disabled")
                    self.b_collapse_copie.state(("disabled",))
                    self.b_expand_copie.state(("disabled",))
                    self.b_collapse_supp.state(("disabled",))
                    self.b_expand_supp.state(("disabled",))
                elif not c:
                    self.b_collapse_copie.state(("disabled",))
                    self.b_expand_copie.state(("disabled",))
                elif not s:
                    self.b_collapse_supp.state(("disabled",))
                    self.b_expand_supp.state(("disabled",))
                if err:
                    showerror("Erreurs", "\n".join(err))
                warnings = self.tree_copie.tag_has('warning')
                if warnings:
                    showwarning("Attention", "Certains éléments à copier (en rouge) ne sont pas de même nature sur l'original et la sauvegarde")
            else:
                showerror("Erreur", "Chemin invalide !")

    def efface_tree(self):
        c = self.tree_copie.get_children("")
        for item in c:
            self.tree_copie.delete(item)
        s = self.tree_supp.get_children("")
        for item in s:
            self.tree_supp.delete(item)
        self.b_collapse_copie.state(("disabled",))
        self.b_expand_copie.state(("disabled",))
        self.b_collapse_supp.state(("disabled",))
        self.b_expand_supp.state(("disabled",))


    def toggle_state_gui(self):
        """ toggle the state (normal/disabled) of key elements of the GUI """
        if "disabled" in self.b_open_orig.state():
            state = "!disabled"
            for i in range(7):
                self.menu.entryconfigure(i, state="normal")
        else:
            state = "disabled"
            for i in range(7):
                self.menu.entryconfigure(i, state="disabled")
        self.tree_copie.state((state,))
        self.tree_supp.state((state,))
        self.entry_orig.state((state,))
        self.entry_sauve.state((state,))
#        self.b_sync.state((state,))
#        self.b_prev.state((state,))
        self.b_expand_copie.state((state,))
        self.b_collapse_copie.state((state,))
        self.b_expand_supp.state((state,))
        self.b_collapse_supp.state((state,))
        self.b_open_orig.state((state,))
        self.b_open_sauve.state((state,))

    def update_pbar(self):
        """ dislay the progress of the copy and deletion and put the GUI back in
            normal state once both processes are done. """
        if not self.is_running_copie and not self.is_running_supp:
            self.toggle_state_gui()
            self.pbar_copie.configure(value=self.pbar_copie.cget("maximum"))
            self.pbar_supp.configure(value=self.pbar_supp.cget("maximum"))
#            self.b_sync.state(("disabled",))
            self.menu.entryconfigure(5, state="disabled")
            self.configure(cursor="")
            self.efface_tree()
            msg = ""
            if self.err_copie:
                msg += "Il y a eu des erreurs lors de la copie, voir %s pour plus de détails.\n" % LOG_COPIE
            if self.err_supp:
                msg += "Il y a eu des erreurs lors de la suppression, voir %s pour plus de détails.\n" % LOG_SUPP
            if msg:
                showerror("Erreur", msg, master=self)
        else:
            if not self.q_copie.empty():
                self.pbar_copie.configure(value=self.q_copie.get())
            if not self.q_supp.empty():
                self.pbar_supp.configure(value=self.q_supp.get())
            self.update()
            self.after(50, self.update_pbar)

    @staticmethod
    def get_list(tree):
        """ return the list of files/folders to copy/delete
            (depending on the tree)"""
        selected = []

        def aux(item):
            tags = tree.item(item, "tags")
            if "checked" in tags and "whole" in tags:
                selected.append(item)
            elif "checked" in tags or "tristate" in tags:
                ch = tree.get_children(item)
                for c in ch:
                    aux(c)
        ch = tree.get_children("")
        for c in ch:
            aux(c)
        return selected

    def synchronise(self):
        """ display the list of files/folders that will be copied / deleted
            and launch the copy and deletion if the user validates the sync. """
        # get files to delete and folder to delete if they are empty
        a_supp = self.get_list(self.tree_supp)
        # get files to copy
        a_copier = self.get_list(self.tree_copie)
        a_supp_avant_cp = []
        for ch in self.pb_chemins:
            if ch in a_copier:
                a_supp_avant_cp.append(ch.replace(self.original, self.sauvegarde))
        if a_supp or a_copier:
            Confirmation(self, a_copier, a_supp, a_supp_avant_cp, self.original, self.sauvegarde)

    def copie_supp(self, a_copier, a_supp, a_supp_avant_cp):
        """ launch sync """
        self.toggle_state_gui()
        self.configure(cursor="watch")
        self.update()
        self.pbar_copie.state(("!disabled",))
        self.pbar_supp.state(("!disabled",))
        nbtot_copie = len(a_copier) + len(a_supp_avant_cp)
        self.pbar_copie.configure(maximum=nbtot_copie, value=0)
        nbtot_supp = len(a_supp)
        self.pbar_supp.configure(maximum=nbtot_supp, value=0)
        self.is_running_copie = True
        self.is_running_supp = True
        process_copie = Thread(target=self.copie, name="copie", daemon=True,
                               args=(a_copier, a_supp_avant_cp))
        process_supp = Thread(target=self.supp, daemon=True,
                              name="suppression", args=(a_supp,))
        process_copie.start()
        process_supp.start()
        self.update_pbar()


    def copie(self, a_copier, a_supp_avant_cp):
        """ copie tous les fichiers/dossiers de a_copier de original vers
            sauvegarde en utilisant la commande système cp. Les erreurs
            rencontrées au cours du processus sont inscrites dans
            ~/.foldersync/copie.log """
        self.err_copie = False
        orig = abspath(self.original) + "/"
        sauve = abspath(self.sauvegarde) + "/"
        chdir(orig)
        with open(LOG_COPIE, "w") as log_copie:
            log_copie.write("###  foldersync : log de la copie  ###\n\n")
            n = len(a_supp_avant_cp)
            for i, ch in zip(range(1, n + 1), a_supp_avant_cp):
                p_copie = run(["rm", "-r", ch], stderr=PIPE)
                self.q_copie.put(i)
                err = p_copie.stderr.decode()
                if err:
                    self.err_copie = True
                    log_copie.write(err + "\n")
            for i, ch in zip(range(n + 1, n + 1 + len(a_copier)), a_copier):
                ch_o  = ch.replace(orig, "")
                p_copie = run(["cp", "-ra", "--parents", ch_o, sauve], stderr=PIPE)
                self.q_copie.put(i)
                err = p_copie.stderr.decode()
                if err:
                    self.err_copie = True
                    log_copie.write(err + "\n")
        self.is_running_copie = False

    def supp(self, a_supp):
        """ supprime tous les fichiers/dossiers de a_supp de original vers
            sauvegarde en utilisant la commande système rm. Les erreurs
            rencontrées au cours du processus sont inscrites dans
            ~/.foldersync/suppression.log """
        self.err_supp = False
        with open(LOG_SUPP, "w") as log_supp:
            log_supp.write("###  foldersync : log de la suppression  ###\n\n")
            for i,ch in enumerate(a_supp):
                p_supp = run(["rm", "-r", ch], stderr=PIPE)
                self.q_supp.put(i+1)
                err = p_supp.stderr.decode()
                if err:
                    log_supp.write(err + "\n")
                    self.err_supp = True
        self.is_running_supp = False

