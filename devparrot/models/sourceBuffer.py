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

from devparrot.core import config, ui, utils
from devparrot.core.utils.variable import mcb
from time import time

import Tkinter

PREFIX = "tkController"

class Modifiers(object):
	_button3 = 1024
	_button2 = 512
	_button1 = 256
	_altgr   = 128
	_super   = 64
	_meta    = 32
	_numlock = 16
	_alt     = 8
	_ctrl    = 4
	_lock    = 2
	_shift   = 1
	def __init__(self, event):
		self.state = event.state
		self.modifiers = set()
		for level in [2**i for i in xrange(10, -1, -1)]:
			if self.state >= level:
				self.modifiers.add(level)
				self.state -= level
			

	def __getattr__(self, name):
		level = getattr(self, "_"+name)
		return level in self.modifiers
			

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
		for key in dir(self):
			method = getattr(self, key)
			if hasattr(method, "tkevent") and callable(method):
				for eventSequence in method.tkevent:
					handle(eventSequence, lambda event, method=method: method(event, Modifiers(event)))

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

def bind(*events):
	def decorator(func):
		func.tkevent = events
		return func
	return decorator

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
		try:
			event.widget.sel_delete()
		finally:
			count = ttk.Tkinter.IntVar()
			text = "\n"
			l, c = event.widget.index('insert').split('.')
			match_start = ttk.Tkinter.Text.search(event.widget, "[ \t]*" , '%s.0'%l, stopindex=event.widget.index('insert'), regexp=True, count=count)
			if match_start:
				match_end = "%s.%i"%(l,min(count.get(),int(c)))
				text += event.widget.get(match_start, match_end)
			event.widget.insert( 'insert', text )

	@bind('<Tab>', '<ISO_Left_Tab>')
	def on_tab(self, event, modifier):
		from devparrot.core.utils.annotations import Index, BadArgument
		try:
			start = Index(event.widget, 'sel.first')
			stop = Index(event.widget, 'sel.last')
		except BadArgument:
			# no selection
			if event.keysym == 'Tab':
				event.widget.insert( 'insert', '\t' )
			return "break"
		if event.keysym == 'ISO_Left_Tab':
			for line in xrange(start.line(), stop.line()+1):
				print line, ":", event.widget.get( '%d.0'%line )
				if event.widget.get( '%d.0'%line ) == '\t':
					event.widget.delete('%d.0'%line, '%d.1'%line)
		else:
			for line in xrange(start.line(), stop.line()+1):
				event.widget.insert( '%d.0'%line, '\t')
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
		if len(event.char) > 0 : return
		self._handle_shift(modifiers.shift,event)
		if modifiers.ctrl:
			event.widget.mark_set( 'insert', '1.0' )
		else:
			l, c = event.widget.index('insert').split('.')
			match_start = ttk.Tkinter.Text.search(event.widget, "[^ \t]" , 'insert linestart', stopindex='insert lineend', regexp=True)
			if match_start:
				if event.widget.compare(match_start, '==', 'insert'):
					event.widget.mark_set( 'insert', 'insert linestart' )
				else:
					event.widget.mark_set( 'insert', match_start)
			else:
				event.widget.mark_set( 'insert', 'insert linestart' )
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

	@bind( '<ButtonPress-1>' )
	def click( self, event, modifiers):
		event.widget.focus_set( )

		if not modifiers.shift and not modifiers.ctrl:
			event.widget.sel_clear( )
			event.widget.sel_setAnchor( 'current' )

	@bind( '<ButtonPress-2>' )
	def middle_click( self, event, modifiers):
		try:
			event.widget.insert( 'current', event.widget.selection_get() )
			event.widget.edit_separator()
		except Tkinter.TclError:
			pass

	@bind( '<ButtonRelease-3>' )
	def right_click( self, event, modifiers):
		ui.mainWindow.popupMenu.post(event.x_root, event.y_root)
		return "break"

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
		event.widget.sel_setAnchor( 'current wordstart' )
		event.widget.mark_set( 'insert', 'current wordend' )
   
	@bind( '<Triple-ButtonPress-1>' )
	def selectLine( self, event, modifiers):
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

def insert_char(event):
	if event.widget and event.char:
		event.widget.insert('insert',event.char)


class CodeText(ttk.Tkinter.Text, utils.event.EventSource):
	def __init__(self):
		ttk.Tkinter.Text.__init__(self, ui.mainWindow.workspaceContainer,
		                          undo=True,
		                          autoseparators=False,
		                          tabstyle="wordprocessor")
		utils.event.EventSource.__init__(self)
		self.bind("<<Selection>>", self.on_selection_changed)
		self.bind_class("Text","<Key>",insert_char)
		bindtags = list(self.bindtags())
		bindtags.insert(1,"Command")
		bindtags = " ".join(bindtags)
		self.bindtags(bindtags)

		config.controller.install( self )
		
		self.tag_configure('currentLine_tag', background=config.color.currentLine_tag_color)
		self.tag_raise("currentLine_tag")
		self.tag_raise("sel", "currentLine_tag")
		
		self.on_font_changed(None, None)
		config.textView.font_register(mcb(self.on_font_changed))
		config.textView.tab_width_register(mcb(self.on_tab_width_changed))
	
	def on_font_changed(self, var, old):
		self.config(font = config.textView.font)
		self.on_tab_width_changed(None, None)
	
	def on_tab_width_changed(self, var, old):
		import tkFont
		self.config(tabs = config.textView.tab_width*tkFont.Font(font=config.textView.font).measure(" "))
	
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
		self.tag_remove('currentLine_tag', '1.0', 'end')
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
		ttk.Tkinter.Text.insert(self, index, *args)
		self.edit_separator()
		self.set_currentLineTag()
		if kword.get('forceUpdate', False):
			self.update()
		self.event('insert')(self, self.index(index), args[0])
		if index=='insert':
			self.see('insert')
		
	
	def delete(self, index1, index2):
		index1 = self.index(index1)
		ttk.Tkinter.Text.delete(self, index1, index2)
		self.edit_separator()
		self.set_currentLineTag()
		self.event('delete')(self, index1, index2)
	
	def calcule_distance(self, first, second):
		return self.tk.call(self._w, "count", "-chars", first, second)

	def undo(self):
		try:
			self.edit_undo()
		except:
			pass
		self.sel_clear()

	def redo(self):
		try:
			self.edit_redo()
		except:
			pass
		self.sel_clear()



class SourceBuffer(CodeText):
	def __init__(self, document):
		CodeText.__init__(self)
		self.document = document
		self.highlight_tag_protected = False
		self.tag_configure("highlight_tag", background=config.color.highlight_tag_color)
		self.tag_configure("search_tag", background=config.color.search_tag_color)
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

