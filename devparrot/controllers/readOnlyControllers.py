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


validChars = set(printables+alphas8bit+punc8bit+" \t"+u'\u20ac')
# euro signe (\u20ac) is not in alpha8bit => add it
wordChars = set(printables+alphas8bit+punc8bit)

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
        if modifiers.ctrl:
            newPos = '1.0'
        elif session.config.get("textView.smart_home_end"):
            l, c = event.widget.index('insert').split('.')
            match_start = ttk.Tkinter.Text.search(event.widget, "[^ \t]" , 'insert linestart', stopindex='insert lineend', regexp=True)
            if match_start:
                if event.widget.compare(match_start, '!=', 'insert'):
                    newPos = match_start

        event.widget.mark_set( 'insert', newPos )
        event.widget.see('insert')
        event.widget.update_idletasks()
    
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
        event.widget.update_idletasks()
    
    @bind("<Right>", "<KP_Right>")
    def right(self, event, modifiers):
        if len(event.char) > 0:
            return
        self._handle_shift(modifiers.shift, event)
        if modifiers.ctrl:
            currentPos = event.widget.index( 'insert' )
            wordend    = event.widget.index( 'insert wordend' )
            word = event.widget.get(currentPos, wordend)

            while wordend != currentPos:
                if len(set(word)&wordChars) != 0:
                    break
                currentPos = wordend
                wordend = event.widget.index( '%s wordend'%currentPos )
                word = event.widget.get(currentPos, wordend)

            event.widget.mark_set( 'insert', wordend)
        else:
            event.widget.mark_set( 'insert', 'insert +1 chars' )
        event.widget.see( 'insert' )
        event.widget.update_idletasks()
    
    @bind("<Left>", "<KP_Left>")
    def left(self, event, modifiers):
        if len(event.char) > 0:
            return
        self._handle_shift(modifiers.shift, event)
        if modifiers.ctrl:
            currentPos = event.widget.index( 'insert' )
            wordstart  = event.widget.index( 'insert -1c wordstart' )
            word = event.widget.get(wordstart, currentPos)

            while wordstart != currentPos:
                if len(set(word)&wordChars) != 0:
                    break
                currentPos = wordstart
                wordstart = event.widget.index( '%s -1c wordstart'%currentPos )
                word = event.widget.get(wordstart, currentPos)


            event.widget.mark_set( 'insert', wordstart)
        else:
            event.widget.mark_set( 'insert', 'insert -1 chars' )
        event.widget.see( 'insert' )
        event.widget.update_idletasks()
    
    @bind("<Down>", "<KP_Down>")
    def down(self, event, modifiers):
        if modifiers.ctrl:
            return
        if len(event.char) > 0:
            return
        self._handle_shift(modifiers.shift, event)
        event.widget.mark_set( 'insert', 'insert +1 lines' )
        event.widget.see( 'insert' )
        event.widget.update_idletasks()
    
    @bind("<Up>", "<KP_Up>")
    def up(self, event, modifiers):
        if modifiers.ctrl:
            return
        if len(event.char) > 0:
            return
        self._handle_shift(modifiers.shift, event)
        event.widget.mark_set( 'insert', 'insert -1 lines' )
        event.widget.see( 'insert' )
        event.widget.update_idletasks()

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
        event.widget.update_idletasks()
    
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
        event.widget.update_idletasks()

    @bind("<Button-4>")
    def scroll_up(self, event, modifiers):
        event.widget.yview_scroll( -3, 'units' )
        event.widget.update_idletasks()

    @bind("<Button-5>")
    def scroll_down(self, event, modifiers):
        event.widget.yview_scroll( 3, 'units' )
        event.widget.update_idletasks()
    
    @bind('<Control-a>')
    def on_ctrl_a(self, event, modifiers):
        event.widget.sel_setAnchor('1.0')
        event.widget.mark_set( 'insert', 'end' )
        return "break"
    
class MouseController(Controller):
    def __init__(self):
        Controller.__init__(self)

    @staticmethod
    def set_current(event):
        try:
            pos1 = '@%d,%d' % (event.x, event.y)
            coord1 = event.widget.bbox(pos1)[0]
            lineend = event.widget.bbox("%s lineend"%pos1)[0]
            newcurrent = pos1
            if event.x < lineend:
                pos2 = '%s +1c' % pos1
                coord2 = event.widget.bbox(pos2)[0]
                halfx = (coord1 + coord2)/2
                if event.x > halfx:
                    newcurrent = pos2
            event.widget.mark_set( 'current' , newcurrent)
        except TypeError:
            pass

    @bind( '<Motion>' )
    def on_motion( self, event, modifiers):
        MouseController.set_current(event)


    @bind( '<ButtonPress-1>' )
    def click( self, event, modifiers):
        MouseController.set_current(event)
        event.widget.focus_set( )

        if not modifiers.shift and not modifiers.ctrl:
            event.widget.sel_clear( )
            event.widget.sel_setAnchor( 'current' )

    @bind( '<ButtonRelease-3>' )
    def right_click( self, event, modifiers):
        MouseController.set_current(event)
        from devparrot.core import ui
        ui.window.popupMenu.post(event.x_root, event.y_root)
        return "break"

    @bind( '<B1-Motion>', '<Shift-Button1-Motion>' )
    def dragSelection( self, event, modifiers):
        MouseController.set_current(event)
        widget = event.widget

        if event.y < 0:
            widget.yview_scroll( -1, 'units' )
        elif event.y >= widget.winfo_height():
            widget.yview_scroll( 1, 'units' )

        if not widget.sel_isAnchorSet( ):
            widget.sel_setAnchor( 'current' )

        widget.mark_set( 'insert', 'current' )
   
    @bind( '<ButtonRelease-1>')
    def moveCarrot_deselect( self, event, modifiers):
        MouseController.set_current(event)
        widget = event.widget

        widget.grab_release()
        widget.mark_set( 'insert', 'current' )
   
    @bind( '<Double-ButtonPress-1>' )
    def selectWord( self, event, modifiers):
        MouseController.set_current(event)
        event.widget.sel_setAnchor( 'current wordstart' )
        event.widget.mark_set( 'insert', 'current wordend' )
   
    @bind( '<Triple-ButtonPress-1>' )
    def selectLine( self, event, modifiers):
        MouseController.set_current(event)
        event.widget.sel_setAnchor( 'current linestart' )
        event.widget.mark_set( 'insert', 'current lineend' )

    @bind( '<Double-ButtonRelease-1>', '<Triple-ButtonRelease-1>' )
    def bypass_deselect(self, event, modifiers):
        return "break"
   
    @bind( '<Button1-Leave>' )
    def scrollView( self, event, modifiers):
        widget = event.widget

        if event.y < 0:
            widget.yview_scroll( -1, 'units' )
        elif event.y >= widget.winfo_height():
            widget.yview_scroll( 1, 'units' )
   
    @bind( '<MouseWheel>' )
    def wheelScroll( self, event, modifiers):
        widget = event.widget

        if event.delta < 0:
            widget.yview_scroll( 1, 'units' )
        else:
            widget.yview_scroll( -1, 'units' )

