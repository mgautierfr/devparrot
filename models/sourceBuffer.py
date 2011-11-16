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

class SourceBuffer(ttk.Tkinter.Text):
	def __init__(self, document):
		ttk.Tkinter.Text.__init__(self,core.mainWindow.workspaceContainer)
		self.bind("<<Selection>>", self.on_selection_changed)
		self.document = document
		self.highlight_tag_protected = False
		self.tag_configure("highlight_tag", background=core.config.get('color','highlight_tag_color'))
		self.tag_configure("search_tag", background=core.config.get('color','search_tag_color'))
		self.tag_lower("highlight_tag", "sel")
		self.tag_lower("search_tag", "sel")
		
		
	def get_document(self):
		return self.document
	
	def set_text(self, content):
		self.replace("0.1", "end", content)
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
