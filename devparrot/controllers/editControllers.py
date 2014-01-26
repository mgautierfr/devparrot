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


import ttk
from devparrot.core.controller import Controller, bind
from devparrot.core.utils.posrange import Index
import readOnlyControllers

from devparrot.core.errors import *


class KeyboardController(Controller):
    def __init__(self):
        Controller.__init__(self)
    
    @bind('<KeyPress>')
    def on_key_pressed(self, event, modifiers):
        from devparrot.core import session
        if event.keysym in ( 'Return', 'Enter', 'KP_Enter', 'BackSpace', 'Delete', 'Insert' ):
            event.widget.sel_clear()
            return "break"
        char = event.char.decode('utf8')
        if char in set(session.config.get("wchars")+session.config.get("puncchars")+session.config.get("spacechars")):
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
        insert = event.widget.index('insert')
        if session.config.get("textView.remove_tail_space"):
            match_start = ttk.Tkinter.Text.search(event.widget, "[ \t]*$", '%s.0'%insert.line, regexp=True)
            if match_start:
                event.widget.delete(match_start, event.widget.lineend(insert))
        if session.config.get("textView.auto_indent"):
            match_start = ttk.Tkinter.Text.search(event.widget, "[ \t]*" , '%s.0'%insert.line, stopindex=str(insert), regexp=True, count=count)
            if match_start:
                match_end = Index(insert.line, min(count.get(), int(insert.col)))
                text += event.widget.get(str(match_start), str(match_end))
        event.widget.insert( 'insert', text )
    
    @bind('<ISO_Left_Tab>')
    def on_back_tab(self, event, modifier):
        from devparrot.core import session
        from devparrot.core.utils.posrange import Index
        tabs = ['\t']
        if session.config.get("textView.space_indent"):
            tabs += [' '*i for i in xrange(session.config.get("textView.tab_width"), 0, -1)]
        try:
            start = event.widget.index('sel.first').line
            stop = event.widget.index('sel.last').line
        except BadArgument:
            start = event.widget.index('insert').line
            stop = start
        for line in xrange(start, stop+1):
            for tab in tabs:
                if event.widget.get( '%d.0'%line, '%d.%d'%(line, len(tab)) ) == tab:
                    event.widget.delete('%d.0'%line, '%d.%d'%(line, len(tab)))
                    break

    @bind('<Tab>')
    def on_tab(self, event, modifier):
        from devparrot.core.utils.posrange import Index
        from devparrot.core import session
        tab = ' '*session.config.get("textView.tab_width") if session.config.get("textView.space_indent") else '\t'
        try:
            start = event.widget.index('sel.first')
            stop = event.widget.index('sel.last')
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
            # we want to catch the except here, so no call to sel_delete
            event.widget.delete( 'sel.first', 'sel.last' )
            event.widget.sel_clear()
        except BadArgument:
            event.widget.delete( 'insert -1 chars', 'insert' )
    
    @bind('<Delete>', '<KP_Delete>')
    def on_delete(self, event, modifiers):
        if event.keysym == "KP_Delete" and len(event.char) > 0 :
            return self.on_key_pressed(event, modifiers)
        try:
            # we want to catch the except here, so no call to sel_delete
            event.widget.delete( 'sel.first', 'sel.last' )
            event.widget.sel_clear()
        except BadArgument:
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
        self.set_current(event)
        try:
            event.widget.insert( 'current', event.widget.selection_get() )
            event.widget.edit_separator()
        except TclError:
            pass

