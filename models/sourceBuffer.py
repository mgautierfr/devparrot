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

from pygments import highlight
from pygments.formatter import Formatter
from pygments.lexers import guess_lexer,get_lexer_by_name
from pygments.styles import get_style_by_name
from pygments.token import _ContextToken

def insert_char(event):
	if event.widget and event.char:
		event.widget.insert('insert',event.char)
		event.widget.recolor()

class SourceBuffer(ttk.Tkinter.Text):
	def __init__(self, document):
		ttk.Tkinter.Text.__init__(self,core.mainWindow.workspaceContainer)
		self.bind("<<Selection>>", self.on_selection_changed)
		self.bind_class("Text","<Key>",insert_char) 
		bindtags = list(self.bindtags())
		bindtags.insert(1,"Action")
		bindtags = " ".join(bindtags)
		self.bindtags(bindtags)
		self.document = document
		self.highlight_tag_protected = False
		self.tag_configure("highlight_tag", background=core.config.get('color','highlight_tag_color'))
		self.tag_configure("search_tag", background=core.config.get('color','search_tag_color'))
		self.tag_lower("highlight_tag", "sel")
		self.tag_lower("search_tag", "sel")
		self.styles = {}
		self.set_style_tag()
		self.markNb=0
		
	def get_document(self):
		return self.document
	
	def set_style_tag(self):
		self.style = get_style_by_name('default')
		self.lexer = get_lexer_by_name("python",stripnl=False, stripall=False, ensurenl=False)
		
		for token,tStyle in self.style:
			token = str(token).replace('.','_')
			if tStyle['color']:
				self.tag_configure(token,foreground="#%s"%tStyle['color'])
			if tStyle['bgcolor']:
				self.tag_configure(token,background="#%s"%tStyle['bgcolor'])
			
				
			self.tag_configure(token,underline=tStyle['underline'])
			#tStyle['bold']
			#tStyle['italic']
			#tStyle['border']
	
	def set_text(self, content):
		self.delete("0.1", "end")
		self.insert("end", content)
		self.update()
		self.recolor()
		self.edit_reset()
		self.edit_modified(False)
	
	def formated_insert(self, tokensource, index):
		first = True
		for ttype, value in tokensource:
			if value:
				if ttype not in self.styles:
					used = ttype 
					while used not in self.style.styles.keys():
                				used = used.parent
					self.styles[ttype] = str(used).replace('.','_')
				used = self.styles[ttype]
				idx = self.index(index)
				self.insert(index, value, used)
				if not first and isinstance(ttype,_ContextToken) and ttype[1] == True:
					self.mark_set("_synctx_%d"%self.markNb, idx)
					self.markNb += 1
				first = False
						
				
	
	def find_good_range(self, start):
		next = self.mark_next(start)
		syncPoint = None
		while next and not next.startswith("_synctx_"):
			next = self.mark_next(next)
		if next:
			syncPoint = self.index(next)
			self.mark_unset(next)
			next = self.mark_next(syncPoint)
			while next and not next.startswith("_synctx_"):
				next = self.mark_next(next)
		if not next:
			return (start, "end")

		distance = self.tk.call(self._w, "count", "-chars", start, syncPoint)
		
		content = self.get(start, next)
		for i, t, v in self.lexer.get_tokens_unprocessed(content):
			if isinstance(t,_ContextToken) and t[1]:
				if i == distance:
					return (start, next)
		return self.find_good_range(start)
		
				
	def recolor(self):
		def find_previous(self, index):
			previous = self.mark_previous(index)
			while previous and not previous.startswith("_synctx_"):
				previous = self.mark_previous(previous)
			return previous or "1.0"
#		import pdb; pdb.set_trace()

		previous = find_previous(self,'insert')
		if previous != "1.0":
			self.mark_gravity(previous, ttk.Tkinter.LEFT)
		
		(start, end) = self.find_good_range(previous)
		
		content = self.get(start,end)
		pos = self.index('insert')
		self.mark_set("temp",previous)
		self.delete(start, end)
		self.mark_gravity('temp',ttk.Tkinter.RIGHT)
		tokens = self.lexer.get_tokens(content)
		self.formated_insert(tokens, "temp")
		self.mark_set('insert',pos)
		self.mark_unset("temp")
		if previous != "1.0":
			self.mark_gravity(previous, ttk.Tkinter.RIGHT)
		import pprint
		#pprint.pprint(self.dump("1.0", "end", mark=True, text=True))
	
	def get_text(self):
		return self.get("0.1", "end")

	def on_selection_changed(self, event):
		if self.highlight_tag_protected : return
		select = self.tag_ranges("sel")
		if select:
			start_select , stop_select = select 
			text = self.get(start_select , stop_select)
			if len(text)>1 :
				self.apply_tag_on_text("highlight_tag", text)
			else:
				self.apply_tag_on_text("highlight_tag", None)

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
			self.tag_remove("sel", "0.1","end")
			self.tag_add("sel", match_start, match_end)
			self.highlight_tag_protected = False
			self.mark_set("insert", match_start if backward else match_end)
			return True
		return False
