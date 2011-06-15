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
		
	def get_document(self):
		return self.document
	
	def set_text(self, content):
		self.begin_not_undoable_action()
		gtksourceview2.Buffer.set_text(self, content)
		self.end_not_undoable_action()
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

	def search(self, backward, text):
		if not text : return
		self.apply_tag_on_text(self.search_tag,text)

		if self.get_has_selection():
			(it, selection) = self.get_selection_bounds()
			if backward:
				if it.compare(selection)>0 : it = selection
			else:
				if it.compare(selection)<0 : it = selection
		else:
			it = self.get_iter_at_mark(self.get_insert())
		if backward:
			search_func = gtk.TextIter.backward_search
			falldawn_iter = self.get_end_iter()
		else:
			search_func = gtk.TextIter.forward_search
			falldawn_iter = self.get_start_iter()

		res = search_func (it,text, gtk.TEXT_SEARCH_TEXT_ONLY)
		if not res:
			res = search_func (falldawn_iter,text, gtk.TEXT_SEARCH_TEXT_ONLY, it)
		if res:
			match_start, match_end = res
			self.select_range(match_start, match_end)
			if backward : return match_start
			return match_end
		return None
