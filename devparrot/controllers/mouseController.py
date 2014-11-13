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
from devparrot.core.errors import TclError

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

    @bind( '<ButtonPress-2>' )
    def middle_click( self, event, modifiers):
        self.set_current(event)
        if event.widget.readOnly:
            return
        try:
            event.widget.insert( 'current', event.widget.selection_get() )
            event.widget.edit_separator()
        except TclError:
            pass

