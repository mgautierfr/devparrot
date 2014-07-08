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
from devparrot.core.utils.posrange import Index, Tag, Mark, LineStart, LineEnd
from devparrot.core import mimemapper

from devparrot.core.errors import *


class KeyboardController(Controller):
    def __init__(self):
        Controller.__init__(self)
    
    @bind('<KeyPress>')
    def on_key_pressed(self, event, modifiers):
        from devparrot.core import session
        if event.widget.readOnly:
            return
        if event.keysym in ( 'Return', 'Enter', 'KP_Enter', 'BackSpace', 'Delete', 'Insert' ):
            event.widget.sel_clear()
            return "break"
        char = event.char.decode('utf8')
        mimetype = mimemapper.mimeMap.get(str(event.widget.document.get_mimetype()))
        if char in set(session.config.wchars.get(mimetype)+session.config.puncchars.get(mimetype)+session.config.spacechars.get(mimetype)):
            event.widget.sel_delete( )
            event.widget.insert( 'insert', char )
            event.widget.sel_clear( )
            return "break"
            
    @bind('<Return>', '<KP_Enter>')
    def on_return(self, event, modifiers):
        from devparrot.core import session
        if event.widget.readOnly:
            return
        event.widget.sel_delete()
        count = ttk.Tkinter.IntVar()
        text = "\n"
        insert = Mark('insert').resolve(event.widget)
        linestart =  LineStart(insert).resolve(event.widget)
        mimetype = mimemapper.mimeMap.get(str(event.widget.document.get_mimetype()))
        if session.config.remove_tail_space.get(mimetype):
            match_start = ttk.Tkinter.Text.search(event.widget, "[ \t]*$", str(linestart), regexp=True)
            if match_start:
                event.widget.delete(match_start, LineEnd(insert).resolve(event.widget))
        if session.config.auto_indent.get(mimetype):
            match_start = ttk.Tkinter.Text.search(event.widget, "[ \t]*" , str(linestart), stopindex=str(insert), regexp=True, count=count)
            if match_start:
                match_end = Index(insert.line, min(count.get(), insert.col))
                text += event.widget.get(str(match_start), str(match_end))
        event.widget.insert( 'insert', text )
    
    @bind('<ISO_Left_Tab>')
    def on_back_tab(self, event, modifier):
        from devparrot.core import session
        from devparrot.core.utils.posrange import Index
        if event.widget.readOnly:
            return
        mimetype = mimemapper.mimeMap.get(str(event.widget.document.get_mimetype()))
        tabs = ['\t'] + [' '*i for i in xrange(session.config.tab_width.get(mimetype), 0, -1)]
        start, stop = Tag('sel').resolve(event.widget)
        for line in xrange(start.line, stop.line+1):
            for tab in tabs:
                if event.widget.get( '%d.0'%line, '%d.%d'%(line, len(tab)) ) == tab:
                    event.widget.delete('%d.0'%line, '%d.%d'%(line, len(tab)))
                    break

    @bind('<Tab>')
    def on_tab(self, event, modifier):
        from devparrot.core.utils.posrange import Index
        from devparrot.core import session
        if event.widget.readOnly:
            return
        mimetype = mimemapper.mimeMap.get(str(event.widget.document.get_mimetype()))
        tab = ' '*session.config.tab_width.get(mimetype) if session.config.space_indent.get(mimetype) else '\t'
        start, stop = Tag('sel').resolve(event.widget)
        if start == stop:
            # no selection
            event.widget.insert( 'insert', tab )
        else:
            for line in xrange(start.line, stop.line+1):
                event.widget.insert( '%d.0'%line, tab)
        return "break"
    
    @bind('<BackSpace>')
    def on_backspace(self, event, modifiers):
        if event.widget.readOnly:
            return
        try:
            # we want to catch the except here, so no call to sel_delete
            event.widget.delete( 'sel.first', 'sel.last' )
            event.widget.sel_clear()
        except BadArgument:
            event.widget.delete( 'insert -1 chars', 'insert' )
    
    @bind('<Delete>', '<KP_Delete>')
    def on_delete(self, event, modifiers):
        if event.widget.readOnly:
            return
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
        if event.widget.readOnly:
            return
        event.widget.redo()
        return "break"
    
    @bind('<Control-z>')
    def on_ctrl_z(self, event, modifiers):
        if event.widget.readOnly:
            return
        event.widget.undo()
        return "break"