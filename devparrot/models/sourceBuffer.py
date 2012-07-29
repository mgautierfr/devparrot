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
from ttk import Tkinter

from devparrot.core import config, ui, utils
from devparrot.core.utils.variable import mcb
from time import time


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
		if config.textView.highlight_current_line:
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

