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
from devparrot.core.utils.posrange import WordStart, WordEnd, Mark

class CarretController( Controller ):
    def __init__( self ):
        Controller.__init__( self )
    
    def _handle_shift(self, shift, event):
        if shift:
            if not event.widget.sel_isAnchorSet():
                event.widget.sel_setAnchor( 'insert' )
        else:
            event.widget.sel_clear( )
    
    @bind( "<Home>", "<KP_Home>")
    def home(self, event, modifiers):
        from devparrot.core import session
        if len(event.char) > 0:
            return
        self._handle_shift(modifiers.shift, event)
        newPos = 'insert linestart'
        document = event.widget.document
        if modifiers.ctrl:
            newPos = '1.0'
        elif document.get_config('smart_home_end'):
            match_start = ttk.Tkinter.Text.search(event.widget, "[^ \t]" , 'insert linestart', stopindex='insert lineend', regexp=True)
            if match_start:
                if event.widget.compare(match_start, '!=', 'insert'):
                    newPos = match_start

        event.widget.mark_set( 'insert', newPos )
        event.widget.see('insert')
    
    @bind("<End>", "<KP_End>",)
    def end(self, event, modifiers):
        if len(event.char) > 0:
            return
        self._handle_shift(modifiers.shift, event)
        if modifiers.ctrl:
            event.widget.mark_set( 'insert', 'end' )
        else:
            event.widget.mark_set( 'insert', 'insert lineend' )
        event.widget.see( 'insert' )
    
    @bind("<Right>", "<KP_Right>")
    def right(self, event, modifiers):
        if len(event.char) > 0:
            return
        self._handle_shift(modifiers.shift, event)
        if modifiers.ctrl:
            wordend = WordEnd(Mark('insert'))
            event.widget.mark_set('insert', wordend.resolve(event.widget))
        else:
            event.widget.mark_set( 'insert', 'insert +1 chars' )
        event.widget.see( 'insert' )
    
    @bind("<Left>", "<KP_Left>")
    def left(self, event, modifiers):
        if len(event.char) > 0:
            return
        self._handle_shift(modifiers.shift, event)
        if modifiers.ctrl:
            wordstart = WordStart(Mark('insert'))
            event.widget.mark_set('insert', wordstart.resolve(event.widget))
        else:
            event.widget.mark_set( 'insert', 'insert -1 chars' )
        event.widget.see( 'insert' )
    
    @bind("<Down>", "<KP_Down>")
    def down(self, event, modifiers):
        if modifiers.ctrl:
            return
        if len(event.char) > 0:
            return
        self._handle_shift(modifiers.shift, event)
        event.widget.mark_set( 'insert', 'insert +1 lines' )
        event.widget.see( 'insert' )
    
    @bind("<Up>", "<KP_Up>")
    def up(self, event, modifiers):
        if modifiers.ctrl:
            return
        if len(event.char) > 0:
            return
        self._handle_shift(modifiers.shift, event)
        event.widget.mark_set( 'insert', 'insert -1 lines' )
        event.widget.see( 'insert' )

    @staticmethod
    def find_nbLine(widget):
        nbLine = widget.tk.call(widget._w, "count", "-displaylines", "@0,0", "@%d,%d" % (widget.winfo_width(), widget.winfo_height()))
        return nbLine

    @bind("<Prior>", "<KP_Prior>")
    def prior(self, event, modifiers):
        if len(event.char) > 0:
            return
        event.widget.yview_scroll( -1, 'pages' )
        if modifiers.ctrl:
            return
        self._handle_shift(modifiers.shift, event)
        event.widget.mark_set('insert', 'insert -%d lines' % CarretController.find_nbLine(event.widget))
        event.widget.see( 'insert' )
    
    @bind("<Next>", "<KP_Next>")
    def next(self, event, modifiers):
        if len(event.char) > 0:
            return
        event.widget.yview_scroll( 1, 'pages' )
        if modifiers.ctrl:
            return
        self._handle_shift(modifiers.shift, event)
        event.widget.mark_set('insert', 'insert +%d lines' % CarretController.find_nbLine(event.widget))
        event.widget.see( 'insert' )

    @bind("<Button-4>")
    def scroll_up(self, event, modifiers):
        event.widget.yview_scroll( -3, 'units' )

    @bind("<Button-5>")
    def scroll_down(self, event, modifiers):
        event.widget.yview_scroll( 3, 'units' )
    
    @bind('<Control-a>')
    def on_ctrl_a(self, event, modifiers):
        event.widget.sel_setAnchor('1.0')
        event.widget.mark_set( 'insert', 'end' )
        return "break"
