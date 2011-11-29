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

def insert_char(event):
	if event.widget and event.char:
		event.widget.insert('insert',event.char)


class CodeText(ttk.Tkinter.Text):
	def __init__(self):
		ttk.Tkinter.Text.__init__(self, core.mainWindow.workspaceContainer)
		self.bind("<<Selection>>", self.on_selection_changed)
		self.bind_class("Text","<Key>",insert_char)
		bindtags = list(self.bindtags())
		bindtags.insert(1,"Action")
		bindtags = " ".join(bindtags)
		self.bindtags(bindtags)
		self.styles = {}
		self.lexer = None
		self.markNb=0
		self.colorizeContext = None
		self.last_stopToken = "1.0"
	
	@staticmethod
	def _token_name(token):
		return "_DP_SH_%s"%str(token).replace('.','_')
	
	def _sync_name(self):
		return ""
	
	def enable_highlight(self, mimetype=None, filename=None):
		from pygments.lexers import guess_lexer,get_lexer_for_mimetype,get_lexer_for_filename,guess_lexer_for_filename
		from pygments.styles import get_style_by_name
		def create_style_table():
			self.style = get_style_by_name('default')
		
			for token,tStyle in self.style:
				token = "DP::SH::%s"%str(token).replace('.','_')
				if tStyle['color']:
					self.tag_configure(token,foreground="#%s"%tStyle['color'])
				if tStyle['bgcolor']:
					self.tag_configure(token,background="#%s"%tStyle['bgcolor'])

				self.tag_configure(token,underline=tStyle['underline'])
				#tStyle['bold']
				#tStyle['italic']
				#tStyle['border']

		if mimetype:
			self.lexer = get_lexer_for_mimetype(mimetype)
		if filename and not self.lexer:
			self.lexer = get_lexer_for_filename(filename)
		if filename and not self.lexer:
			self.lexer = guess_lexer_for_filename(filename)
		if not self.lexer:
			self.lexer = guess_lexer(self.get("1.0", "end"))
		if self.lexer:
			create_style_table() 
		
	def insert(self, index, *args, **kword):
		ttk.Tkinter.Text.insert(self, index, *args)
		if kword.get('forceUpdate', False):
			self.update()
		if self.lexer:
			self._update_highlight(index)
	
	def delete(self, index1, index2):
		ttk.Tkinter.Text.delete(self, index1, index2)
		if self.lexer:
			self._update_highlight(index1)
	
	def calcule_distance(self, first, second):
		return self.tk.call(self._w, "count", "-chars", first, second)

	def _update_highlight(self, insertPoint):

		def find_startPoint(self, index):
			def find_previous(self, index):
				previous = self.mark_previous(index)
				while previous and (not previous.startswith("DP::SH::_synctx_") or not self.compare(previous, "<", index)):
					previous = self.mark_previous(previous)
				return previous
			previous = find_previous(self, index)
			if previous:
				return find_previous(self, previous) or "1.0"
			return "1.0"
		
		def find_next(self, index):
			next = self.mark_next(index)
			while next and (not next.startswith("DP::SH::_synctx_") or not self.compare(next, ">", index)):
				next = self.mark_next(next)
			return next or "end"
		
		
		def stop_at_syncPoint(self, tokens, startPoint, insertPoint):
			from pygments.token import _ContextToken
			syncPoint = self.index(find_next(self, insertPoint))
			distance = self.calcule_distance(startPoint, syncPoint)
			for i,t,v in tokens:
				if v:
					currentPos = "%s + %d c"%(startPoint, i)
					if isinstance(t,_ContextToken) and t[1]:
						while i > distance:
							next = find_next(self, syncPoint)
							distance += self.calcule_distance(syncPoint, next)
							syncPoint = next
						if i == distance and self.compare(self.last_stopToken, "<=", currentPos) :
							print "stopIter", currentPos
							raise StopIteration
						yield i,t,v,True
					else:
						yield i,t,v,False

		start = self.index(find_startPoint(self,insertPoint))
		content = self.get(start,"end")
		tokens = self.lexer.get_tokens_unprocessed(content)
		tokens = stop_at_syncPoint(self, tokens, start, insertPoint)
		self.colorizeContext = (tokens, start,time())
		self._update_a_token(realTime=True)
		#self.after_idle(self._update_a_token)	

	def _update_a_token(self,realTime=False):
		def markoff(name):
			#print "markoff", name
			self.mark_unset(name)
		
		def markon(pos):
			#print "markon", "DP::SH::_synctx_%d"%self.markNb, pos
			self.mark_set("DP::SH::_synctx_%d"%self.markNb, pos)
			self.markNb += 1
		
		def tagdel(name, start, end):
			#print "tagdel",name, start, end
			self.tag_remove(name, start, end)
		
		def tagadd(name, start, end):
			#print "tagadd",name, start, end
			self.tag_add(name, start, end)
		
		def process_itvs(elem):
			i,t,v,s = elem
			start = self.index("%s+%dc"%(startPoint,i))
			token = {'start' : start,
				 'end'   : "%s+%dc"%(start,len(v)),
				 'name'  : "DP::SH::%s"%str(t).replace('.','_')
				}
			addToken = False
			tags = {}
			marks = []
			startedTags = {}
			stopedTags = {}
			for key, name, pos in self.dump(token['start'], token['end'], mark=True, tag=True):
				if key == 'mark' and name.startswith("DP::SH::_synctx_"):
					marks.append({'name':name,'pos':pos})
				if key == 'tagon':
					startedTags[name] = pos
				if key == 'tagoff' and self.compare(pos, "!=", token['start']):
					if name in startedTags:
						l = tags.get(name, [])
						l.append({'start':startedTags[name],'end':pos, 'name':name})
						tags[name] = l
						del startedTags[name]
					else:
						stopedTags[name] = pos
			if s :
				if len(marks) == 0:
					#markon(token['start'])
					self.mark_set("DP::SH::_synctx_%d"%self.markNb, token['start'])
					self.markNb += 1
				else:
					if self.compare(marks[0]['pos'], "!=", token['start']):
						#markon(token['start'])
						self.mark_set("DP::SH::_synctx_%d"%self.markNb, token['start'])
						self.markNb += 1
						#markoff(marks[0]['name'])
						self.mark_unset(marks[0]['name'])
						
					for mark in marks[1:]:
						#markoff(mark['name'])
						self.mark_unset(mark['name'])
				
			else:
				for mark in marks:
					#markoff(mark['name'])
					self.mark_unset(mark['name'])
			if len(stopedTags) != 0:
				print "WARNING !! This should not append"
			for name, pos in startedTags.items():
				start,end = self.tag_nextrange(name, pos)
				if self.compare(end, '==', token['end']):
					l = tags.get(name, [])
					l.append({'start':startedTags[name],'end':end, 'name':name})
					tags[name] = l
				else:
					#tagdel(name, start, end)
					self.tag_remove(tag['name'], tag['start'], tag['end'])

			if token['name'] in tags and len(tags[token['name']]) == 1 and \
				self.compare(tags[token['name']][0]['start'], "==", token['start']) and \
				self.compare(tags[token['name']][0]['end'], "==", token['end']):
					del tags[token['name']]
			else:
				addToken = True
				   
			for name, tagslist in tags.items():
				for tag in tagslist:
					#tagdel(tag['name'], tag['start'], tag['end'])
					self.tag_remove(tag['name'], tag['start'], tag['end'])
			
			if addToken:
				#tagadd(token['name'], token['start'], token['end'])
				self.tag_add(token['name'], token['start'], token['end'])

			if self.compare(self.last_stopToken, "<", token['end']):
				self.last_stopToken = token['end']
		
		if self.colorizeContext:
			tokens = self.colorizeContext[0]
			startPoint = self.colorizeContext[1]
		else:
			return

		if realTime:
			map(process_itvs, tokens)
			self.last_stopToken = "1.0"
			print time()-self.colorizeContext[2]
		else:
			try :
				process_itvs(tokens.next())
				self.after_idle(self._update_a_token)

			except StopIteration:
				self.last_stopToken = "1.0"
				print time()-self.colorizeContext[2]
				pass


class SourceBuffer(CodeText):
	def __init__(self, document):
		CodeText.__init__(self)
		self.document = document
		self.highlight_tag_protected = False
		self.tag_configure("highlight_tag", background=core.config.get('color','highlight_tag_color'))
		self.tag_configure("search_tag", background=core.config.get('color','search_tag_color'))
		self.tag_lower("highlight_tag", "sel")
		self.tag_lower("search_tag", "sel")
		
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
