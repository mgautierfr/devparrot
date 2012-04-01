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

import core.config
import core.mainWindow
from time import time

import Tkinter

import utils.event

PREFIX = "tkController"

class Modifiers(object):
	def __init__(self, modifiers):
		self.modifiers = modifiers

	def __getattr__(self, name):
		if name in ["shift", "ctrl", "meta", "super", "lock"]:
			return name in self.modifiers
		raise AttibuteError
			

class Controller(object):
	def __init__(self, master=None):
		if master is None:
			master = Tkinter._default_root
		assert master is not None
		self.tag = PREFIX + str(id(self))
		def bind(event, handler):
			master.bind_class(self.tag, event, handler)
		self.create(bind)

	def create(self, handle):
		# override if necessary
		# the default implementation looks for decorated methods
		for key in dir(self):
			method = getattr(self, key)
			if hasattr(method, "tkevent") and hasattr(method, "tkmodif") and callable(method):
				for eventSequence in method.tkevent:
					for modif in method.tkmodif:
						rawEventSequence = [eventSequence[1:-1]]
						if 'shift' in modif: rawEventSequence.insert(0, 'Shift')
						if 'ctrl' in modif: rawEventSequence.insert(0, 'Control')
						if 'alt' in modif: rawEventSequence.insert(0, 'Alt')
						rawEventSequence = "-".join(rawEventSequence)
						rawEventSequence = "<"+rawEventSequence+">" 
						handle(rawEventSequence, lambda event, method=method, modif=modif:
						                                   method(event, Modifiers(modif)))

class MetaController:
	def __init__(self, master=None):
		if master is None:
			master = Tkinter._default_root
		assert master is not None
		self.subControllers = []
	
	def set_subControllers(self, *controllers):
		self.subControllers.extend(controllers)
	
	def install(self, widget):
		widgetclass = widget.winfo_class()
		# remove widget class bindings and other controllers
		tags = list(widget.bindtags())
		tags[tags.index(widgetclass):tags.index(widgetclass)+1] = [c.tag for c in self.subControllers]
		widget.bindtags(tuple(tags))


_none = ()
_shift = ('shift',)
_lock = ('lock',)
_ctrl = ('ctrl',)
_alt = ('alt',)
_super = ('super',)
_shiftctrl = ('shift','ctrl')
_shiftalt  = ('shift','alt')
_shiftsuper= ('shift','super')
_lockctrl = ('lock','ctrl')
_lockalt  = ('lock','alt')
_locksuper= ('lock','super')
_ctrlalt   = ('ctrl', 'alt')
_ctrlsuper = ('ctrl', 'super')
_altsuper  = ('alt', 'super')
_shiftctrlalt = ('shift', 'ctrl', 'alt')
_shiftctrlsuper = ('shift', 'ctrl', 'super')
_shiftaltsuper = ('shift', 'alt', 'super')
_lockctrlalt = ('lock', 'ctrl', 'alt')
_lockctrlsuper = ('lock', 'ctrl', 'super')
_lockaltsuper = ('lock', 'alt', 'super')
_ctrlaltsuper = ('ctrl', 'alt', 'super')
_shiftctrlaltsuper = ('shift', 'ctrl', 'alt', 'super')
_lockctrlaltsuper = ('lock', 'ctrl', 'alt', 'super')



def bind(*events):
	if isinstance(events[-1], list):
		modifiers = events[-1]
		events = events[:-1]
	else:
		modifiers = [_none]
	def decorator(func):
		func.tkevent = events
		func.tkmodif = modifiers
		return func
	return decorator

def _bind(modifiersList, *events):
	def decorator(func):
		func.tkevent = events
		func.tkmodif = modifiersList
		return func
	return decorator

def bind(*events):
	return _bind([_none], *events)

def mbind(*events):
	return _bind([_none, _shift, _ctrl, _alt, _lock, _super, _shiftctrl, _shiftalt, _shiftsuper, _ctrlalt, _ctrlsuper, _altsuper, _lockctrl, _lockalt, _locksuper, _shiftctrlalt, _shiftctrlsuper, _shiftaltsuper, _ctrlaltsuper, _shiftctrlaltsuper, _lockctrlalt, _lockctrlsuper, _lockaltsuper, _lockctrlaltsuper],
	*events)

class BasicTextController(Controller):
	def __init__(self):
		Controller.__init__(self)
	
	@bind('<KeyPress>')
	def on_key_pressed(self, event, modifiers):
		if event.keysym in ( 'Return','Enter','KP_Enter','Tab','BackSpace','Delete','Insert' ):
			event.widget.sel_clear()
			return "break"
		if len(event.char) > 0:
			try:
				event.widget.sel_delete( )
			except:
				pass
	      
			event.widget.insert( 'insert', event.char )
			event.widget.sel_clear( )
			return "break"
			
	@bind('<Return>', '<KP_Enter>')
	def on_return(self, event, modifiers):
		try:
			event.widget.sel_delete()
		finally:
			event.widget.search
			count = ttk.Tkinter.IntVar()
			text = "\n"
			l, c = event.widget.index('insert').split('.')
			match_start = ttk.Tkinter.Text.search(event.widget, "[ \t]*" , '%s.0'%l, stopindex=event.widget.index('insert'), regexp=True, count=count)
			if match_start:
				match_end = "%s.%i"%(l,min(count.get(),int(c)))
				text += event.widget.get(match_start, match_end)
			event.widget.insert( 'insert', text )
			event.widget.see('insert')

	@bind('<Key-Tab>')
	def on_tab(self, event, modifier):
		event.widget.insert( 'insert', '\t' )
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
	
	@mbind( "<Home>", "<KP_Home>")
	def home(self, event, modifiers):
		self._handle_shift(modifiers.shift,event)
		if modifiers.ctrl:
			event.widget.mark_set( 'insert', '1.0' )
		else:
			event.widget.mark_set( 'insert', 'insert linestart' )
		event.widget.see('insert')
		event.widget.update_idletasks()
	
	@mbind("<End>", "<KP_End>",)
	def end(self, event, modifiers):
		self._handle_shift(modifiers.shift, event)
		if modifiers.ctrl:
			event.widget.mark_set( 'insert', 'end' )
		else:
			event.widget.mark_set( 'insert', 'insert lineend' )
		event.widget.see( 'insert' )
		event.widget.update_idletasks()
	
	@mbind("<Right>")
	def right(self, event, modifiers):
		self._handle_shift(modifiers.shift, event)
		if modifiers.ctrl:
			currentPos = event.widget.index( 'insert' )
			maxPos     = event.widget.index( 'end wordstart' )
	    
			if currentPos == maxPos:
				return
	    
			offset = 1
			while event.widget.compare( currentPos, '==', event.widget.index('insert') ):
				event.widget.mark_set( 'insert', 'insert wordend +%dc wordstart' % offset )
				offset += 1
		else:
			event.widget.mark_set( 'insert', 'insert +1 chars' )
		event.widget.see( 'insert' )
		event.widget.update_idletasks()
	
	@mbind("<Left>")
	def left(self, event, modifiers):
		self._handle_shift(modifiers.shift, event)
		if modifiers.ctrl:
			currentPos = event.widget.index( 'insert' )
			minPos     = event.widget.index( '1.0 wordstart' )
	    
			if currentPos == minPos:
				return
	    
			offset = 2
			event.widget.mark_set( 'insert', 'insert wordstart' )
			while event.widget.compare( currentPos, '==', event.widget.index('insert') ):
				event.widget.mark_set( 'insert', 'insert -%dc wordstart' % offset )
				offset += 1
		else:
			event.widget.mark_set( 'insert', 'insert -1 chars' )
		event.widget.see( 'insert' )
		event.widget.update_idletasks()
	
	@mbind("<Down>")
	def down(self, event, modifiers):
		if modifiers.ctrl: return
		self._handle_shift(modifiers.shift, event)
		event.widget.mark_set( 'insert', 'insert +1 lines' )
		event.widget.see( 'insert' )
		event.widget.update_idletasks()
	
	@mbind("<Up>")
	def up(self, event, modifiers):
		if modifiers.ctrl: return
		self._handle_shift(modifiers.shift, event)
		event.widget.mark_set( 'insert', 'insert -1 lines' )
		event.widget.see( 'insert' )
		event.widget.update_idletasks()

	@staticmethod
	def find_nbLine(widget):
		nbLine = widget.tk.call(widget._w, "count", "-displaylines", "@0,0", "@%d,%d"%(widget.winfo_width(),widget.winfo_height()))
		return nbLine

	@mbind("<Prior>")
	def prior(self, event, modifiers):
		event.widget.yview_scroll( -1, 'pages' )
		if modifiers.ctrl : return
		self._handle_shift(modifiers.shift, event)
		event.widget.mark_set('insert', 'insert -%d lines'%CarretController.find_nbLine(event.widget))
		event.widget.see( 'insert' )
		event.widget.update_idletasks()
	
	@mbind("<Next>")
	def next(self, event, modifiers):
		event.widget.yview_scroll( 1, 'pages' )
		if modifiers.ctrl : return
		self._handle_shift(modifiers.shift, event)
		event.widget.mark_set('insert', 'insert +%d lines'%CarretController.find_nbLine(event.widget))
		event.widget.see( 'insert' )
		event.widget.update_idletasks()

class AdvancedTextController(Controller):
	def __init__( self ):
		Controller.__init__( self )
	
	@bind('<Control-a>')
	def on_ctrl_a(self, event, modifiers):
		self._selectionAnchor = '1.0'
		event.widget.mark_set( 'insert', 'end' )
		return "break"
	
	@bind('<Control-c>')
	def on_ctrl_c(self, event, modifiers):
		try:
			event.widget.clipboard_clear()
			event.widget.clipboard_append( event.widget.get( 'sel.first', 'sel.last' ) )
		except:
			pass
		return "break"
	
	@bind('<Control-r>')
	def on_ctrl_r(self, event, modifiers):
		try:
			event.widget.edit_redo( )
		except:
			pass
		event.widget.sel_clear( )
		return "break"
	
	@bind('<Control-v>')
	def on_ctrl_v(self, event, modifiers):
		try:
			event.widget.mark_set( 'insert', 'sel.first' )
			event.widget.delete( 'sel.first', 'sel.last' )
		except:
			pass
    
		event.widget.insert( 'insert', event.widget.clipboard_get( ) )
		event.widget.sel_clear( )
		return "break"
	
	@bind('<Control-x>')
	def on_ctrl_x(self, event, modifiers):
		try:
			event.widget.clipboard_clear()
			event.widget.clipboard_append( event.widget.get( 'sel.first', 'sel.last' ) )
			event.widget.delete( 'sel.first', 'sel.last' )
			event.widget.ins_updateTags( )
		except:
			pass
		event.widget.sel_clear( )
		return "break"
	
	@bind('<Control-z>')
	def on_ctrl_z(self, event, modifiers):
		try:
			event.widget.edit_undo( )
		except:
			pass
		event.widget.sel_clear( )
		return "break"

class MouseController(Controller):
	def __init__(self):
		Controller.__init__(self)

	@mbind( '<ButtonPress-1>' )
	def click( self, event, modifiers):
		event.widget.focus_set( )

		if not modifiers.shift and not modifiers.ctrl:
			event.widget.sel_clear( )
			event.widget.sel_setAnchor( 'current' )

	@bind( '<B1-Motion>', '<Shift-Button1-Motion>' )
	def dragSelection( self, event, modifiers):
		widget = event.widget

		if event.y < 0:
			widget.yview_scroll( -1, 'units' )
		elif event.y >= widget.winfo_height():
			widget.yview_scroll( 1, 'units' )

		if not widget.sel_isAnchorSet( ):
			widget.sel_setAnchor( '@%d,%d' % (event.x+2, event.y) )

		widget.mark_set( 'insert', '@%d,%d' % (event.x+2, event.y) )
   
	@bind( '<ButtonRelease-1>')
	def moveCarrot_deselect( self, event, modifiers):
		widget = event.widget

		widget.grab_release()
		widget.mark_set( 'insert', 'current' )
   
	@bind( '<Double-ButtonPress-1>' )
	def selectWord( self, event, modifiers):
		event.widget.sel_setAnchor( 'insert wordstart' )
		event.widget.mark_set( 'insert', 'insert wordend' )
   
	@bind( '<Triple-ButtonPress-1>' )
	def selectLine( self, event, modifiers):
		event.widget.sel_setAnchor( 'insert linestart' )
		event.widget.mark_set( 'insert', 'insert lineend' )

	@bind( '<Double-ButtonRelease-1>', '<Triple-ButtonRelease-1>' )
	def bypass_deselect(self, event, modifiers): return "break"
   
	@bind( '<Button1-Leave>' )
	def scrollView( self, event, modifiers):
		widget = event.widget

		if event.y < 0:
			widget.yview_scroll( -1, 'units' )
		elif event.y >= widget.winfo_height():
			widget.yview_scroll( 1, 'units' )

		widget.grab_set( )
   
	@bind( '<MouseWheel>' )
	def wheelScroll( self, event, modifiers):
		widget = event.widget

		if event.delta < 0:
			widget.yview_scroll( 1, 'units' )
		else:
			widget.yview_scroll( -1, 'units' )

def insert_char(event):
	if event.widget and event.char:
		event.widget.insert('insert',event.char)


class CodeText(ttk.Tkinter.Text, utils.event.EventSource):
	def __init__(self):
		ttk.Tkinter.Text.__init__(self, core.mainWindow.workspaceContainer,
		                          undo=True,
		                          autoseparators=True,
#		                          wrap="none",
		                          font=core.config.get('textView','font'))
		utils.event.EventSource.__init__(self)
		self.bind("<<Selection>>", self.on_selection_changed)
		self.bind_class("Text","<Key>",insert_char)
		bindtags = list(self.bindtags())
		bindtags.insert(1,"Action")
		bindtags = " ".join(bindtags)
		self.bindtags(bindtags)
		controller = MetaController()
		controller.set_subControllers(CarretController(), AdvancedTextController(), BasicTextController(), MouseController() )
		controller.install( self )
		self.tag_configure('currentLine_tag', background=core.config.get('color','currentLine_tag_color'))
		self.tag_raise("currentLine_tag")
		self.tag_raise("sel", "currentLine_tag")
		
	
	# Selection Operations
	def sel_clear( self ):
		try:
			self.tag_remove( 'sel', '1.0', 'end' )
		except:
			pass
      
		try:
			self.mark_unset( 'sel.anchor', 'sel.first', 'sel.last' )
		except:
			pass
   
	def sel_setAnchor( self, index ):
		self.mark_set( 'sel.anchor', index )
   
	def sel_isAnchorSet( self ):
		try:
			self.index( 'sel.anchor' )
			return True
		except:
			return False

	def sel_isSelection( self ):
		try:
			self.index( 'sel.first' )
			return True
		except:
			return False

	def sel_update( self ):
		if widget.compare( 'sel.anchor', '<', 'insert' ):
			widget.mark_set( 'sel.first', 'sel.anchor' )
			widget.mark_set( 'sel.last', 'insert' )
		elif widget.compare( 'sel.anchor', '>', 'insert' ):
			widget.mark_set( 'sel.first', 'insert' )
			widget.mark_set( 'sel.last', 'sel.anchor' )
		else:
			return
      
		widget.tag_remove( 'sel', '1.0', 'end' )
		widget.tag_add( 'sel', 'sel.first', 'sel.last' )
   
	def sel_delete( self ):
		try:
			self.delete('sel.first', 'sel.last' )
		except:
			pass
		
		self.sel_clear( )
	
	def set_currentLineTag(self):
		self.tag_remove('currentLine_tag', '0.0', 'end')
		self.tag_add( 'currentLine_tag', 'insert linestart', 'insert + 1l linestart')

	# Overloads
	def mark_set( self, name, index ):
		Tkinter.Text.mark_set( self, name, index )
		if name == 'insert':
			self.set_currentLineTag()
			try:
				if self.compare( 'sel.anchor', '<', 'insert' ):
					self.mark_set( 'sel.first', 'sel.anchor' )
					self.mark_set( 'sel.last', 'insert' )
				elif self.compare( 'sel.anchor', '>', 'insert' ):
					self.mark_set( 'sel.first', 'insert' )
					self.mark_set( 'sel.last', 'sel.anchor' )
				else:
					return
            	
				self.tag_remove( 'sel', '1.0', 'end' )
				self.tag_add( 'sel', 'sel.first', 'sel.last' )
			except:
				pass 
		
	def insert(self, index, *args, **kword):
		index = self.index(index)
		ttk.Tkinter.Text.insert(self, index, *args)
		self.set_currentLineTag()
		if kword.get('forceUpdate', False):
			self.update()
		self.event('insert')(self, index, args[0])
	
	def delete(self, index1, index2):
		index1 = self.index(index1)
		ttk.Tkinter.Text.delete(self, index1, index2)
		self.set_currentLineTag()
		self.event('delete')(self, index1, index2)
	
	def calcule_distance(self, first, second):
		return self.tk.call(self._w, "count", "-chars", first, second)



class SourceBuffer(CodeText):
	def __init__(self, document):
		CodeText.__init__(self)
		self.document = document
		self.highlight_tag_protected = False
		self.tag_configure("highlight_tag", background=core.config.get('color','highlight_tag_color'))
		self.tag_configure("search_tag", background=core.config.get('color','search_tag_color'))
		self.hl_callId = None
		self.tag_lower("highlight_tag", "sel")
		self.tag_lower("search_tag", "sel")
		self.tag_raise("highlight_tag", "currentLine_tag")
		self.tag_raise("search_tag", "currentLine_tag")
		
	def get_document(self):
		return self.document
	
	def set_text(self, content):
		self.delete("0.1", "end")
		self.insert("end", content, forceUpdate=True)
		self.edit_reset()
		self.edit_modified(False)
	
	def get_text(self):
		return self.get("0.1", "end")

	def on_selection_changed(self, event):
		if self.highlight_tag_protected : return
		select = self.tag_ranges("sel")
		if select:
			start_select , stop_select = select 
			text = self.get(start_select , stop_select)
			if self.hl_callId:
				self.after_cancel(self.hl_callId)
			self.hl_callId = self.after(300, self.hl_apply_tag, text)
	
	def hl_apply_tag(self, text):
		if len(text)>1 :
			self.apply_tag_on_text("highlight_tag", text)
		else:
			self.apply_tag_on_text("highlight_tag", None)
		self.hl_callId = None

	def apply_tag_on_text(self, tag, text):
		self.tag_remove(tag, "0.1","end")

		if text:
			count = ttk.Tkinter.IntVar()
			match_start = ttk.Tkinter.Text.search(self,text, "0.1", stopindex="end", forwards=True, exact=True, count=count)
			while match_start:
				match_end = "%s+%ic"%(match_start,count.get())
				self.tag_add(tag, match_start, match_end)
				match_start = ttk.Tkinter.Text.search(self,text, match_end, stopindex="end", forwards=True, exact=True, count=count)

	def search(self, backward, text):
		if not text : return
		self.apply_tag_on_text("search_tag",text)

		start_search = "insert"
		select = self.tag_ranges("sel")
		if select:
			if backward:
				start_search = select[0]
			else:
				start_search = select[1]

		count = ttk.Tkinter.IntVar()
		match_start = ttk.Tkinter.Text.search(self,text, start_search, forwards=(not backward), backwards=backward, exact=True, count=count) 
		if match_start:
			match_end = "%s+%ic"%(match_start,count.get())
			self.highlight_tag_protected = True
			self.sel_clear()
			self.tag_add("sel", match_start, match_end)
			self.highlight_tag_protected = False
			self.mark_set("insert", match_start if backward else match_end)
			return True
		return False

