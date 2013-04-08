#    This file is part of DevParrot.
#
#    Author: Matthieu Gautier <matthieu.gautier@mgautier.fr>
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
#    Copyright 2011 Matthieu Gautier

import ttk
from devparrot.core.controller import Controller, bind
from pyparsing import printables, punc8bit, alphas8bit
import readOnlyControllers


validChars = set(printables+alphas8bit+punc8bit+" \t"+u'\u20ac')
# euro signe (\u20ac) is not in alpha8bit => add it
wordChars = set(printables+alphas8bit+punc8bit)


class KeyboardController(Controller):
    def __init__(self):
        Controller.__init__(self)
    
    @bind('<KeyPress>')
    def on_key_pressed(self, event, modifiers):
        if event.keysym in ( 'Return', 'Enter', 'KP_Enter', 'BackSpace', 'Delete', 'Insert' ):
            event.widget.sel_clear()
            return "break"
        char = event.char.decode('utf8')
        if char in validChars:
            event.widget.sel_delete( )
            event.widget.insert( 'insert', char )
            event.widget.sel_clear( )
            return "break"
            
    @bind('<Return>', '<KP_Enter>')
    def on_return(self, event, modifiers):
        from devparrot.core import session
        event.widget.sel_delete()
        count = ttk.Tkinter.IntVar()
        text = "\n"
        l, c = event.widget.index('insert').split('.')
        if session.config.get("textView.remove_tail_space"):
            match_start = ttk.Tkinter.Text.search(event.widget, "[ \t]*$", '%s.0'%l, regexp=True)
            if match_start:
                event.widget.delete(match_start, '%s.0 lineend'%l)
        if session.config.get("textView.auto_indent"):
            match_start = ttk.Tkinter.Text.search(event.widget, "[ \t]*" , '%s.0'%l, stopindex=event.widget.index('insert'), regexp=True, count=count)
            if match_start:
                match_end = "%s.%i" % (l, min(count.get(), int(c)))
                text += event.widget.get(match_start, match_end)
        event.widget.insert( 'insert', text )
    
    @bind('<ISO_Left_Tab>')
    def on_back_tab(self, event, modifier):
        from devparrot.core import session
        from devparrot.core.utils.posrange import Index, BadArgument
        tabs = ['\t']
        if session.config.get("textView.space_indent"):
            tabs += [' '*i for i in xrange(session.config.get("textView.tab_width"), 0, -1)]
        try:
            start = Index(event.widget, 'sel.first').line
            stop = Index(event.widget, 'sel.last').line
        except BadArgument:
            start = Index(event.widget, 'insert').line
            stop = start
        for line in xrange(start, stop+1):
            for tab in tabs:
                if event.widget.get( '%d.0'%line, '%d.%d'%(line, len(tab)) ) == tab:
                    event.widget.delete('%d.0'%line, '%d.%d'%(line, len(tab)))
                    break

    @bind('<Tab>')
    def on_tab(self, event, modifier):
        from devparrot.core.utils.posrange import Index, BadArgument
        from devparrot.core import session
        tab = ' '*session.config.get("textView.tab_width") if session.config.get("textView.space_indent") else '\t'
        try:
            start = Index(event.widget, 'sel.first')
            stop = Index(event.widget, 'sel.last')
        except BadArgument:
            # no selection
            event.widget.insert( 'insert', tab )
        else:
            for line in xrange(start.line, stop.line+1):
                event.widget.insert( '%d.0'%line, tab)
        return "break"
    
    @bind('<BackSpace>')
    def on_backspace(self, event, modifiers):
        try:
            event.widget.delete( 'sel.first', 'sel.last' )
            event.widget.sel_clear()
        except ttk.Tkinter.TclError:
            event.widget.delete( 'insert -1 chars', 'insert' )
    
    @bind('<Delete>', '<KP_Delete>')
    def on_delete(self, event, modifiers):
        if event.keysym == "KP_Delete" and len(event.char) > 0 :
            return self.on_key_pressed(event, modifiers)
        try:
            event.widget.delete( 'sel.first', 'sel.last' )
            event.widget.sel_clear()
        except ttk.Tkinter.TclError:
            event.widget.delete( 'insert', 'insert +1 chars' )
    
    @bind('<Control-r>')
    def on_ctrl_r(self, event, modifiers):
        event.widget.redo()
        return "break"
    
    @bind('<Control-z>')
    def on_ctrl_z(self, event, modifiers):
        event.widget.undo()
        return "break"

class MouseController(readOnlyControllers.MouseController):
    def __init__(self):
        readOnlyControllers.MouseController.__init__(self)

    @bind( '<ButtonPress-2>' )
    def middle_click( self, event, modifiers):
        import Tkinter
        self.set_current(event)
        try:
            event.widget.insert( 'current', event.widget.selection_get() )
            event.widget.edit_separator()
        except Tkinter.TclError:
            pass

