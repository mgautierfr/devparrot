
import gtksourceview2

#@Representation("text")
class SourceBuffer(gtksourceview2.Buffer):
	def __init__(self, document):
		gtksourceview2.Buffer.__init__(self)
		self.connect("mark-set", self.on_mark_set)
		self.search_tag = self.create_tag(background="yellow")
		self.document = document
		self.load_from_document()
		
	def get_document(self):
		return self.document
		
	def load_from_document(self):
		self.set_text(self.document.get_content())
		self.set_modified(False)
	
	def save_to_document(self):
		self.document.set_content(self.get_text(self.get_start_iter(), self.get_end_iter()))
		self.set_modified(False)
		
	def on_mark_set(self, textbuffer, iter, textmark):
		if textmark.get_name() in ['insert', 'selection_bound']:
			if textbuffer.get_has_selection():
				select = textbuffer.get_selection_bounds()
				if select:
					start_select , stop_select = select 
					text = textbuffer.get_text(start_select , stop_select)
					self.apply_tag_on_text(self.search_tag, text)

	def apply_tag_on_text(self, tag, text):
		start, end = self.get_bounds()
		self.remove_tag(tag, start,end)

		if text:
			res = start.forward_search(text, gtk.TEXT_SEARCH_TEXT_ONLY)
			while res:
				match_start, match_end = res
				self.apply_tag(tag, match_start, match_end)
				res = match_end.forward_search(text, gtk.TEXT_SEARCH_TEXT_ONLY)
