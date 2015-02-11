#    This file is part of DevParrot.
#
#    Author: Matthieu Gautier <matthieu.gautier@devparrot.org>
#
#    DevParrot is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    DevParrot is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with DevParrot.  If not, see <http://www.gnu.org/licenses/>.
#
#
#    Copyright 2011-2013 Matthieu Gautier


import tkinter, tkinter.ttk
from devparrot.core.errors import *
import itertools

def escape_token(value):
    if set("'\"\\ ") | set(value):
        for specialChar in "'\"\\ ":
            value = value.replace(specialChar, '\\'+specialChar)
    return value

class BaseCompletion:
    def __init__(self, startIndex):
        self.startIndex = startIndex

    def name(self):
        """return the full name of the completion"""
        raise NotImplemented

    def description(self):
        return self.name()

    def complete(self):
        """return the text to add to finish the completion"""
        raise NotImplemented

    def final(self):
        """return True if the completion must stop"""
        raise NotImplemented

    def start(self):
        """return the start index of the completion"""
        return self.startIndex

class CompletionSystem:
    """
    CompletionSystem Class allow a text widget to be completed.
    This class is abstract. It is intent to be inherite to provide how to find posible completion and to insert the text as wanted
    """
    def __init__(self):
        """
        """
        self.textWidget = None
        self._create_listboxWidget()
        self.completions = []
        self.labelText = ""
        self.handle_idle = None

    def set_model(self, model):
        self.textWidget = model

    def _create_listboxWidget(self):
        self.displayed = False
        self.toplevel = tkinter.Toplevel()
        self.toplevel.withdraw()
        self.toplevel.wm_overrideredirect(True)

        self.listbox = tkinter.Listbox(self.toplevel, activestyle='none')
        self.listbox.pack(expand=True, fill=tkinter.BOTH, side=tkinter.BOTTOM)
        self.toplevel.pack_propagate(True)
        self.toplevel.bind_class("completion_%d"%id(self), '<Key>', self._on_event)
        self.toplevel.bind_class("completion_%d"%id(self), '<FocusOut>', self.on_lost_focus)

        self.label = tkinter.ttk.Label(self.toplevel)

    def _set_position(self):
        x, y, width, height = self.textWidget.bbox('insert')
        xpos = self.textWidget.winfo_rootx() + x
        ypos = self.textWidget.winfo_rooty() + y + height
        self.toplevel.wm_geometry("+%d+%d"% (xpos, ypos))

    def _show(self):
        self.displayed = True
        self._set_position()
        self.toplevel.deiconify()
        size = max([len(self.labelText)] + [len(v.description()) for v in self.completions])
        self.listbox.configure(width=size, height=len(self.completions))
        bindtags = list(self.textWidget.bindtags())
        bindtags.insert(0,"completion_%d"%id(self))
        bindtags = " ".join(bindtags)
        self.textWidget.bindtags(bindtags)

    def _hide(self):
        if self.handle_idle:
            self.textWidget.after_cancel(self.handle_idle)
            self.handle_idle = None
        self.displayed = False
        self.toplevel.withdraw()
        bindtags = list(self.textWidget.bindtags())
        if bindtags[0] == "completion_%d"%id(self):
            bindtags = bindtags[1:]
        bindtags = " ".join(bindtags)
        self.textWidget.bindtags(bindtags)

    def on_lost_focus(self, event):
        self._hide()

    def update_completion(self, now=False):
        if self.handle_idle:
            self.textWidget.after_cancel(self.handle_idle)
        self.stop_completion()
        if now:
            self.handle_idle = self.textWidget.after_idle(self._update_completion)
        else:
            self.handle_idle = self.textWidget.after(250, self._update_completion)

    def _update_completion(self):
        self.handle_idle = None
        self._update_completion_content(*self.get_completions())

    def stop_completion(self):
        self._hide()
        self.textWidget.focus()

    def get_selected(self):
        return self.completions[int(self.listbox.curselection()[0])]

    def _on_event(self, event):
        if event.keysym in ("Escape",):
            self.stop_completion()
            return "break"
        if event.keysym in ("Return", "KP_Enter"):
            try:
                self.complete(self.get_selected())
                self.update_completion()
                return "break"
            except IndexError:
                # no selection => let textWidget do its normal stuff.
                pass
        if event.keysym == 'Tab':
            try:
                cur = int(self.listbox.curselection()[0])
            except IndexError:
                # no selection => select the first one
                self.listbox.select_set(0)
            else:
                self.listbox.select_clear(cur)
                cur += 1
                if cur == len(self.completions):
                    cur = 0
                self.listbox.select_set(cur)
            return "break"
        self.stop_completion()

    def _update_completion_content(self, labelText, completions):
        self.completions = completions = list(itertools.islice(completions, 10))
        self.labelText = labelText
        if not labelText and (not completions or (len(completions)==1 and not completions[0].complete())):
            self.stop_completion()
            return
        self.label['text'] = labelText
        if not labelText:
            self.label.pack_forget()
        else:
            self.label.pack(expand=True, fill=tkinter.X, anchor="w", side=tkinter.TOP)

        self.listbox.delete('0', 'end')
        if self.completions:
            self.listbox.pack(expand=True, fill=tkinter.BOTH, side=tkinter.BOTTOM)
            for v in self.completions:
                self.listbox.insert('end', v.description())
        else:
            self.listbox.pack_forget()
        self._show()

    def get_completions(self):
        """
        analyse the text and return a tuple completion list

        This function has to be redefine in sub class
        """
        raise NotImplemented

    def complete(self, completion):
        """
        effectively complete a text widget (text replace)
        @param completion the completion choosen
        This function has to be redefine in sub class
        """
        raise NotImplemented

