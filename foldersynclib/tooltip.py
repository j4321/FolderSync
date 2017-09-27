# *** coding: utf-8 -*-
"""
FolderSync - Alternative to filedialog for Tkinter
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


Tooltip and TooltipWrapper
"""


from tkinter import Toplevel
from tkinter.ttk import Label, Style


class Tooltip(Toplevel):
    def __init__(self, parent, **kwargs):
        Toplevel.__init__(self, parent)
        if 'title' in kwargs:
            self.title(kwargs['title'])
        self.transient(parent)
        self.attributes('-type', 'tooltip')
        self.attributes('-alpha', kwargs.get('alpha', 0.8))
        self.overrideredirect(True)
        self.configure(padx=kwargs.get('padx', 4))
        self.configure(pady=kwargs.get('pady', 4))

        self.style = Style(self)
        bg = kwargs.get('background', 'black')
        self.configure(background=bg)
        self.style.configure('tooltip.TLabel',
                             foreground=kwargs.get('foreground', 'gray90'),
                             background=bg,
                             font='TkDefaultFont 9 bold')

        self.im = kwargs.get('image', None)
        self.label = Label(self, text=kwargs.get('text', ''), image=self.im,
                           style='tooltip.TLabel',
                           compound=kwargs.get('compound', 'left'))
        self.label.pack()

    def configure(self, **kwargs):
        if 'text' in kwargs:
            self.label.configure(text=kwargs.pop('text'))
        if 'image' in kwargs:
            self.label.configure(image=kwargs.pop('image'))
        if 'background' in kwargs:
            self.style.configure('tooltip.TLabel', background=kwargs['background'])
        if 'foreground' in kwargs:
            fg = kwargs.pop('foreground')
            self.style.configure('tooltip.TLabel', foreground=fg)
        if 'alpha' in kwargs:
            self.attributes('-alpha', kwargs.pop('alpha'))
        Toplevel.configure(self, **kwargs)


class TooltipWrapper:
    def __init__(self, widget, **kwargs):
        self.widget = widget
        if 'delay' in kwargs:
            self.delay = kwargs.pop('delay')
        else:
            self.delay = 2000
        self.kwargs = kwargs.copy()
        self._timer_id = None
        self.tooltip = Tooltip(self.widget, **self.kwargs)
        self.tooltip.withdraw()

        self.widget.bind('<Enter>', self._on_enter)
        self.widget.bind('<Leave>', self._on_leave)
        self.tooltip.bind('<Leave>', self._on_leave_tooltip)

    def _on_enter(self, event):
        if not self.tooltip.winfo_ismapped():
            self._timer_id = self.widget.after(self.delay, self.display_tooltip)

    def _on_leave(self, event):
        if self.tooltip.winfo_ismapped():
            x, y = self.widget.winfo_pointerxy()
            if not self.widget.winfo_containing(x, y) in [self.widget, self.tooltip]:
                self.tooltip.withdraw()
        else:
            self.widget.after_cancel(self._timer_id)

    def _on_leave_tooltip(self, event):
        x, y = self.widget.winfo_pointerxy()
        if not self.widget.winfo_containing(x, y) in [self.widget, self.tooltip]:
            self.tooltip.withdraw()

    def display_tooltip(self):
        if "disabled" not in self.widget.state():
            self.tooltip.deiconify()
            x = self.widget.winfo_pointerx() + 14
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 2
            self.tooltip.geometry('+%i+%i' % (x, y))


class TooltipMenuWrapper:
    """Tooltip wrapper for a Menu."""
    def __init__(self, menu, delay=1500, **kwargs):
        """
        Create a Tooltip wrapper for the Menu.

        This wrapper enables the creation of tooltips for tree's items with all
        the bindings to make them appear/disappear.

        Options:
            * menu: wrapped menu
            * delay: hover delay before displaying the tooltip (ms)
            * all keyword arguments of a Tooltip
        """
        self.menu = menu
        self.delay = delay
        self._timer_id = ''
        self.tooltip_text = {}
        self.tooltip = Tooltip(menu.master, **kwargs)
        self.tooltip.withdraw()
        self.current_item = None

        self.menu.bind('<Motion>', self._on_motion)
        self.menu.bind('<Leave>', lambda e: self.menu.after_cancel(self._timer_id))

    def add_tooltip(self, index, text):
        """Add a tooltip with given text to the item."""
        self.tooltip_text[str(index)] = text

    def _on_motion(self, event):
        """Withdraw tooltip on mouse motion and cancel its appearance."""
        if self.tooltip.winfo_ismapped():
            self.tooltip.withdraw()
            self.current_item = 'none'
        else:
            self.menu.after_cancel(self._timer_id)
            self.current_item = self.menu.tk.eval("%s index @%i,%i" % (event.widget, event.x, event.y))
            self._timer_id = self.menu.after(self.delay, self.display_tooltip)

    def display_tooltip(self):
        """Display the tooltip corresponding to the hovered item."""
        text = self.tooltip_text.get(self.current_item, '')
        if text and self.menu.entrycget(self.current_item, 'state') != 'disabled':
            self.tooltip.configure(text=text)
            self.tooltip.deiconify()
            x = self.menu.winfo_pointerx() + 14
            y = self.menu.master.winfo_rooty() + 5
            self.tooltip.geometry('+%i+%i' % (x, y))
