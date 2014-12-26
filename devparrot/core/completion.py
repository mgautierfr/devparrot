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


import Tkinter
import ttk
from devparrot.core.errors import *
import itertools

def escape_token(value):
    if set("'\"\\ ") | set(value):
        for specialChar in "'\"\\ ":
            value = value.replace(specialChar, '\\'+specialChar)
    return value

class BaseCompletion(object):
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

def getcommonstart(seq):
    if not seq:
        return ""
    s1, s2 = min(seq), max(seq)
    l = min(len(s1), len(s2))
    if l == 0 :
        return ""
    for i in xrange(l) :
        if s1[i] != s2[i] :
            return s1[:i]
    return s1[:l]

class CompletionSystem(object):
    """
    CompletionSystem Class allow a text widget to be completed.
    This class is abstract. It is intent to be inherite to provide how to find posible completion and to insert the text as wanted
    """
    def __init__(self, textWidget, completionEvent='<Tab>', previousCompletionEvent='<Up>', nextCompletionEvent='<Down>'):
        """
        @param textWidget the text widget to complete
        @param completionEvent a tk event used to start the completion
        """
        self.textWidget = textWidget
        self._create_listboxWidget()
        self.completionEvent = completionEvent
        self._install_binding()
        self._update_completion("", [])

    def _install_binding(self):
        if self.completionEvent is None:
            return
        bindtagName = "Completion_%s_%d"%(self.__class__.__name__, id(self))
        bindtags = list(self.textWidget.bindtags())
        bindtags.insert(0, bindtagName)
        bindtags = " ".join(bindtags)
        self.textWidget.bindtags(bindtags)
        try:
            self.__class__.bindInitialized
        except AttributeError:
            self.__class__.bindInitialized = True
            Tkinter._default_root.bind_class(bindtagName, self.completionEvent, self.on_widget_key_completion)

    def _create_listboxWidget(self):
        self.toplevel = Tkinter.Toplevel()
        self._hide()
        self.toplevel.wm_overrideredirect(True)
        self.toplevel.bind('<FocusOut>', self.on_lost_focus)

        self.listbox = Tkinter.Listbox(self.toplevel)
        self.listbox.pack(expand=True, fill=Tkinter.BOTH, side=Tkinter.BOTTOM)
        self.toplevel.pack_propagate(True)
        self.listbox.bind('<Key>', self._on_event)

        self.label = ttk.Label(self.toplevel)

    def _set_position(self):
        x, y, width, height = self.textWidget.bbox('insert')
        xpos = self.textWidget.winfo_rootx() + x
        ypos = self.textWidget.winfo_rooty() + y + height
        self.toplevel.wm_geometry("+%d+%d"% (xpos, ypos))
        self.toplevel.wm_geometry("")

    def _show(self):
        self.displayed = True
        self._set_position()
        self.toplevel.deiconify()

    def _hide(self):
        self.displayed = False
        self.toplevel.withdraw()

    def on_lost_focus(self, event):
        self._hide()

    def start_completion(self):
        self._update_completion(*self.get_completions())
        if not self.completions or (len(self.completions)==1 and not self.completions[0].complete()):
            self._hide()
            return
        self._show()
        self.listbox.focus()
        self.listbox.select_set(0)

    def stop_completion(self):
        self._hide()
        self.textWidget.focus()

    def get_selected(self):
        try:
            return self.completions[int(self.listbox.curselection()[0])]
        except IndexError:
            return Completion("",False)

    def on_widget_key_completion(self, event):
        self.start_completion()
        self.update_completion()
        return "break"

    def _on_event(self, event):
        from devparrot.core import session
        validChars = set(session.config.get('wchars')+session.config.get('puncchars')+session.config.get('spacechars'))
        if event.keysym == 'Escape':
            self.stop_completion()
            return
        if event.keysym == 'Return' or (event.keysym == 'Tab' and len(self.completions) == 1):
            selected = self.get_selected()
            self.complete(selected)
            if selected.final():
                self.stop_completion()
            else:
                self.update_completion()
            return
        if event.keysym == 'Tab':
            self.complete(self.get_selected())
            self.update_completion()
            return
        if event.keysym == 'BackSpace':
            self.perform_backspace()
            return
        char = event.char.decode('utf8')
        if char in validChars:
            self.perform_insert_char(char)

    def update_completion(self):
        if not self.displayed:
            return

        text = self.textWidget.get('1.0', 'insert')
        self._update_completion(*self.get_completions())

    def _update_completion(self, labelText, completions):
        self.completions = completions = list(itertools.islice(completions, 10))
        self.listbox.delete('0', 'end')
        if not completions or (len(completions)==1 and not completions[0].complete()):
            self.stop_completion()
            return
        size = 0
        self.label['text'] = labelText
        if not labelText:
            self.label.pack_forget()
        else:
            self.label.pack(expand=True, fill=Tkinter.X, anchor="w")

        for v in self.completions:
            size = max(size, len(v.description()))
            self.listbox.insert('end', v.description())
        self._set_position()
        self.listbox.configure(width=size, height=len(self.completions))
        self.listbox.select_set(0)

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

    def perform_insert_char(self, char):
        self.textWidget.insert('insert', char)
        self.update_completion()

    def perform_backspace(self):
        try:
            self.textWidget.delete( 'sel.first', 'sel.last' )
            self.textWidget.tag_remove( 'sel', '1.0', 'end' )
            self.textWidget.mark_unset( 'sel.first', 'sel.last' )
        except BadArgument:
            self.textWidget.delete( 'insert -1 chars', 'insert' )
        self.update_completion()
