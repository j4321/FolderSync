#! /usr/bin/python3
# -*- coding: utf-8 -*-
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


Treeview with checkboxes at each item and a noticeable disabled style
"""

from tkinter import PhotoImage
from tkinter.ttk import Treeview, Style
from foldersynclib.constants import IM_CHECKED, IM_UNCHECKED, IM_TRISTATE


class CheckboxTreeview(Treeview):
    """
        Treeview widget with checkboxes left of each item.
        The checkboxes are done via the image attribute of the item, so to keep
        the checkbox, you cannot add an image to the item.
    """

    def __init__(self, master=None, **kw):
        Treeview.__init__(self, master, style='Checkbox.Treeview', **kw)
        # style (make a noticeable disabled style)
        style = Style(self)
        style.map("Checkbox.Treeview",
                  fieldbackground=[("disabled", '#E6E6E6')],
                  foreground=[("disabled", 'gray40')],
                  background=[("disabled", '#E6E6E6')])
        # checkboxes are implemented with pictures
        self.im_checked = PhotoImage(file=IM_CHECKED, master=self)
        self.im_unchecked = PhotoImage(file=IM_UNCHECKED, master=self)
        self.im_tristate = PhotoImage(file=IM_TRISTATE, master=self)
        self.tag_configure("unchecked", image=self.im_unchecked)
        self.tag_configure("tristate", image=self.im_tristate)
        self.tag_configure("checked", image=self.im_checked)
        # check / uncheck boxes on click
        self.bind("<Button-1>", self.box_click, True)

    def expand_all(self):
        def aux(item):
            self.item(item, open=True)
            children = self.get_children(item)
            for c in children:
                aux(c)
        children = self.get_children("")
        for c in children:
            aux(c)

    def collapse_all(self):
        def aux(item):
            self.item(item, open=False)
            children = self.get_children(item)
            for c in children:
                aux(c)
        children = self.get_children("")
        for c in children:
            aux(c)

    def state(self, states=None):
        if states:
            if "disabled" in states:
                self.bind('<Button-1>', lambda e: 'break')
            elif "!disabled" in states:
                self.unbind("<Button-1>")
                self.bind("<Button-1>", self.box_click, True)
            return Treeview.state(self, states)
        else:
            return Treeview.state(self)

    def change_state(self, item, state):
        """ replace the current state of the item
            (ie replace the current state tag but keeps the other tags) """
        tags = self.item(item, "tags")
        states = ("checked", "unchecked", "tristate")
        new_tags = [t for t in tags if not t in states]
        new_tags.append(state)
        self.item(item, tags=tuple(new_tags))

    def tag_add(self, item, tag):
        """ add tag to the tags of item """
        tags = self.item(item, "tags")
        self.item(item, tags=tags + (tag,))

    def tag_del(self, item, tag):
        """ add tag to the tags of item """
        tags = list(self.item(item, "tags"))
        if tag in tags:
            tags.remove(tag)
            self.item(item, tags=tuple(tags))

    def insert(self, parent, index, iid=None, **kw):
        """ same method as for standard treeview but add the tag for the box
            state accordingly to the parent state if no tag among
            ('checked', 'unchecked', 'tristate') is given """
        if self.tag_has("checked", parent):
            tag = "checked"
        else:
            tag = 'unchecked'
        if not "tags" in kw:
            kw["tags"] = (tag,)
        elif not ("unchecked" in kw["tags"] or "checked" in kw["tags"]
                  or "tristate" in kw["tags"]):
            kw["tags"] += (tag,)

        Treeview.insert(self, parent, index, iid, **kw)

    def check_descendant(self, item):
        """ check the boxes of item's descendants """
        children = self.get_children(item)
        for iid in children:
            self.change_state(iid, "checked")
            self.check_descendant(iid)

    def check_ancestor(self, item):
        """ check the box of item and change the state of the boxes of item's
            ancestors accordingly """
        self.change_state(item, "checked")
        parent = self.parent(item)
        if parent:
            children = self.get_children(parent)
            b = ["checked" in self.item(c, "tags") for c in children]
            if False in b:
                # at least one box is not checked and item's box is checked
                self.tristate_parent(parent)
            else:
                # all boxes of the children are checked
                self.check_ancestor(parent)

    def tristate_parent(self, item):
        """ put the box of item in tristate and change the state of the boxes of
            item's ancestors accordingly """
        self.change_state(item, "tristate")
        parent = self.parent(item)
        if parent:
            self.tristate_parent(parent)

    def uncheck_descendant(self, item):
        """ uncheck the boxes of item's descendant """
        children = self.get_children(item)
        for iid in children:
            self.change_state(iid, "unchecked")
            self.uncheck_descendant(iid)

    def uncheck_ancestor(self, item):
        """ uncheck the box of item and change the state of the boxes of item's
            ancestors accordingly """
        self.change_state(item, "unchecked")
        parent = self.parent(item)
        if parent:
            children = self.get_children(parent)
            b = ["unchecked" in self.item(c, "tags") for c in children]
            if False in b:
                # at least one box is checked and item's box is unchecked
                self.tristate_parent(parent)
            else:
                # no box is checked
                self.uncheck_ancestor(parent)

    def box_click(self, event):
        """ check or uncheck box when clicked """
        x, y, widget = event.x, event.y, event.widget
        elem = widget.identify("element", x, y)
        if "image" in elem:
            # a box was clicked
            item = self.identify_row(y)
            if self.tag_has("unchecked", item) or self.tag_has("tristate", item):
                self.check_ancestor(item)
                self.check_descendant(item)
            else:
                self.uncheck_descendant(item)
                self.uncheck_ancestor(item)
