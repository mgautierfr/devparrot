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


class BasicTextController(Controller):
    def __init__(self):
        Controller.__init__(self)
    
    @bind('<KeyPress>')
    def on_key_pressed(self, event, modifiers):
        if event.keysym in ( 'Return','Enter','KP_Enter','BackSpace','Delete','Insert' ):
            event.widget.sel_clear()
            return "break"
        char = event.char.decode('utf8')
        if char in validChars:
            try:
                event.widget.sel_delete( )
            except:
                pass
          
            event.widget.insert( 'insert', char )
            event.widget.sel_clear( )
            return "break"
            
    @bind('<Return>', '<KP_Enter>')
    def on_return(self, event, modifiers):
        from devparrot.core import session
        try:
            event.widget.sel_delete()
        finally:
            count = ttk.Tkinter.IntVar()
            text = "\n"
            l, c = event.widget.index('insert').split('.')
            if session.config.textView.remove_tail_space:
                match_start = ttk.Tkinter.Text.search(event.widget, "[ \t]*$", '%s.0'%l, regexp=True)
                if match_start:
                    event.widget.delete(match_start, '%s.0 lineend'%l)
            if session.config.textView.auto_indent:
                match_start = ttk.Tkinter.Text.search(event.widget, "[ \t]*" , '%s.0'%l, stopindex=event.widget.index('insert'), regexp=True, count=count)
                if match_start:
                    match_end = "%s.%i"%(l,min(count.get(),int(c)))
                    text += event.widget.get(match_start, match_end)
            event.widget.insert( 'insert', text )
    
    @bind('<ISO_Left_Tab>')
    def on_back_tab(self, event, modifier):
        from devparrot.core import session
        from devparrot.core.utils.posrange import Index, BadArgument
        tabs = ['\t']
        if session.config.textView.space_indent:
            tabs += [' '*i for i in xrange(session.config.textView.tab_width, 0, -1)]
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
        tab = ' '*session.config.textView.tab_width if session.config.textView.space_indent else '\t'
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
        except:
            event.widget.delete( 'insert -1 chars', 'insert' )
    
    @bind('<Delete>', '<KP_Delete>')
    def on_delete(self, event, modifiers):
        if event.keysym=="KP_Delete" and len(event.char) > 0 :
            return self.on_key_pressed(event, modifiers)
        try:
            event.widget.delete( 'sel.first', 'sel.last' )
            event.widget.sel_clear()
        except:
            event.widget.delete( 'insert', 'insert +1 chars' )
            
    


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
        if len(event.char) > 0 : return
        self._handle_shift(modifiers.shift,event)
        newPos = 'insert linestart'
        if modifiers.ctrl:
            newPos = '1.0'
        elif session.config.textView.smart_home_end:
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
        if len(event.char) > 0 : return
        self._handle_shift(modifiers.shift, event)
        if modifiers.ctrl:
            event.widget.mark_set( 'insert', 'end' )
        else:
            event.widget.mark_set( 'insert', 'insert lineend' )
        event.widget.see( 'insert' )
        event.widget.update_idletasks()
    
    @bind("<Right>", "<KP_Right>")
    def right(self, event, modifiers):
        if len(event.char) > 0 : return
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
        if len(event.char) > 0 : return
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
        if modifiers.ctrl: return
        if len(event.char) > 0 : return
        self._handle_shift(modifiers.shift, event)
        event.widget.mark_set( 'insert', 'insert +1 lines' )
        event.widget.see( 'insert' )
        event.widget.update_idletasks()
    
    @bind("<Up>", "<KP_Up>")
    def up(self, event, modifiers):
        if modifiers.ctrl: return
        if len(event.char) > 0 : return
        self._handle_shift(modifiers.shift, event)
        event.widget.mark_set( 'insert', 'insert -1 lines' )
        event.widget.see( 'insert' )
        event.widget.update_idletasks()

    @staticmethod
    def find_nbLine(widget):
        nbLine = widget.tk.call(widget._w, "count", "-displaylines", "@0,0", "@%d,%d"%(widget.winfo_width(),widget.winfo_height()))
        return nbLine

    @bind("<Prior>", "<KP_Prior>")
    def prior(self, event, modifiers):
        if len(event.char) > 0 : return
        event.widget.yview_scroll( -1, 'pages' )
        if modifiers.ctrl : return
        self._handle_shift(modifiers.shift, event)
        event.widget.mark_set('insert', 'insert -%d lines'%CarretController.find_nbLine(event.widget))
        event.widget.see( 'insert' )
        event.widget.update_idletasks()
    
    @bind("<Next>", "<KP_Next>")
    def next(self, event, modifiers):
        if len(event.char) > 0 : return
        event.widget.yview_scroll( 1, 'pages' )
        if modifiers.ctrl : return
        self._handle_shift(modifiers.shift, event)
        event.widget.mark_set('insert', 'insert +%d lines'%CarretController.find_nbLine(event.widget))
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


class AdvancedTextController(Controller):
    def __init__( self ):
        Controller.__init__( self )
    
    @bind('<Control-a>')
    def on_ctrl_a(self, event, modifiers):
        self._selectionAnchor = '1.0'
        event.widget.mark_set( 'insert', 'end' )
        return "break"
    
    @bind('<Control-r>')
    def on_ctrl_r(self, event, modifiers):
        event.widget.redo()
        return "break"
    
    @bind('<Control-z>')
    def on_ctrl_z(self, event, modifiers):
        event.widget.undo()
        return "break"

class MouseController(Controller):
    def __init__(self):
        Controller.__init__(self)

    @staticmethod
    def set_current(event):
        try:
            pos1 = '@%d,%d' % (event.x, event.y)
            pos2 = '%s +1c'%pos1
            coord1 = event.widget.bbox(pos1)[0]
            coord2 = event.widget.bbox(pos2)[0]
            halfx = (coord1 + coord2)/2
            if event.x < halfx:
                event.widget.mark_set( 'current' , pos1)
            else:
                event.widget.mark_set( 'current' , '%s + 1c'%pos1)
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

    @bind( '<ButtonPress-2>' )
    def middle_click( self, event, modifiers):
        import Tkinter.TclError
        MouseController.set_current(event)
        try:
            event.widget.insert( 'current', event.widget.selection_get() )
            event.widget.edit_separator()
        except Tkinter.TclError:
            pass

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
    def bypass_deselect(self, event, modifiers): return "break"
   
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

