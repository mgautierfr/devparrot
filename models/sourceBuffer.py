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

import gtksourceview2
import gtk

#@Representation("text")
class SourceBuffer(gtksourceview2.Buffer):
	def __init__(self, document):
		gtksourceview2.Buffer.__init__(self)
		self.connect("mark-set", self.on_mark_set)
		self.search_tag = self.create_tag(background="yellow")
		self.document = document
		self.searchMark = None
		self.connect("mark-set", self.on_mark_set)
		self.highlight_tag = self.create_tag(background="yellow")
		self.search_tag = self.create_tag(background="red")
		self.load_from_document()
		
	def get_document(self):
		return self.document
		
	def load_from_document(self):
		self.begin_not_undoable_action()
		self.set_text(self.document.get_content())
		self.end_not_undoable_action()
		self.set_modified(False)
	
	def save_to_document(self, document=None):
		if not document : document = self.document
		document.set_content(self.get_text(self.get_start_iter(), self.get_end_iter()))
		self.set_modified(False)
		
	def on_mark_set(self, textbuffer, iter, textmark):
		if textmark.get_name() in ['insert', 'selection_bound']:
			if textbuffer.get_has_selection():
				select = textbuffer.get_selection_bounds()
				if select:
					start_select , stop_select = select 
					text = textbuffer.get_text(start_select , stop_select)
					if len(text) >1 :
						self.apply_tag_on_text(self.highlight_tag, text)
					else:
						self.apply_tag_on_text(self.highlight_tag, None)

	def apply_tag_on_text(self, tag, text):
		start, end = self.get_bounds()
		self.remove_tag(tag, start,end)

		if text:
			res = start.forward_search(text, gtk.TEXT_SEARCH_TEXT_ONLY)
			while res:
				match_start, match_end = res
				self.apply_tag(tag, match_start, match_end)
				res = match_end.forward_search(text, gtk.TEXT_SEARCH_TEXT_ONLY)

	def start_search(self, text):
		if not text : return
		self.apply_tag_on_text(self.search_tag,text)

		self.searchedText = text
		if not self.searchMark:
			self.searchMark = self.create_mark('search_start', self.get_iter_at_mark(self.get_insert()))
		else:
			self.move_mark(self.searchMark,self.get_iter_at_mark(self.get_insert()))
		return self.next_search()

	def next_search(self):
		it  = self.get_iter_at_mark(self.searchMark)
		res = it.forward_search(self.searchedText, gtk.TEXT_SEARCH_TEXT_ONLY)
		if not res:
			res = self.get_start_iter().forward_search(self.searchedText, gtk.TEXT_SEARCH_TEXT_ONLY, it)
		if res:
			match_start, match_end = res
			self.select_range(match_start, match_end)
			self.move_mark(self.searchMark,match_end)
			return match_end
		return None
