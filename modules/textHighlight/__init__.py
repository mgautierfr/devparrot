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


import tkFont
import os.path

import core.config

from utils.annotations import Index

from pygments.token import SyncPoint

import Tkinter


_fonts = {}
_styles = {}

def activate():
	import core.controler
	create_fonts()
	create_styles()
	core.controler.eventSystem.connect("newDocument",on_new_document)
	pass

def deactivate():
	pass

def create_fonts():
	global _fonts
	_fonts[(False,False)] = tkFont.Font(font=core.config.get('textView','font'))
	_fonts[(True,False)] = _fonts[(False,False)].copy()
	_fonts[(True,False)].configure(weight='bold')
	_fonts[(False,True)] = _fonts[(False,False)].copy()
	_fonts[(False,True)].configure(slant='italic')
	_fonts[(True,True)] = _fonts[(False,False)].copy()
	_fonts[(True,True)].configure(slant='italic',weight='bold')

def create_styles():
	from pygments.styles import get_style_by_name
	global _fonts
	global _styles
	
	style = get_style_by_name('default')
	for token,tStyle in style:
		token = "DP::SH::%s"%str(token).replace('.','_')
		_styles[token] = {}
		if tStyle['color']:
			_styles[token]['foreground'] = "#%s"%tStyle['color']
		if tStyle['bgcolor']:
			_styles[token]['background'] = "#%s"%tStyle['bgcolor']

		_styles[token]['underline'] = tStyle['underline']
		_styles[token]['font'] = _fonts[(tStyle['bold'],tStyle['italic'])]
		

def create_style_table(textWidget):
	for token, style in _styles.items():
		textWidget.tag_configure(token, style)

class HighlightContext(object):
	def __init__(self):
		self.lexer = None
		self.markNb=0
		self.colorizeContext = None
		self.last_stopToken = "1.0"

def on_new_document(document):
	create_style_table(document.models['text'])
	document.connect('textSet', on_text_set)
	document.models['text']._highlight = HighlightContext()
	on_text_set(document)
	document.models['text'].connect('insert', on_insert)
	document.models['text'].connect('delete', on_delete)
	pass

def on_text_set(document):
	def find_lexer(filename):
		from pygments.lexers import guess_lexer,get_lexer_for_filename,guess_lexer_for_filename

		try:
			return get_lexer_for_filename(filename)
		except:
			pass
		try:
			return guess_lexer_for_filename(filename)
		except:
			pass
		return guess_lexer(document.models['text'].get("1.0", "end"))

	if not document.has_a_path():
		return

	filename = os.path.basename(document.get_path())
	document.models['text']._highlight.lexer = find_lexer(filename)	
	document.models['text']._highlight.lexer.noSyncPoint = False

def on_insert(model, insertMark, text):
	if model._highlight.lexer :
		start = Index(model, insertMark)
		stop = start + '%d c'%len(text)
		model._highlight.no_tagMarkZone = (start, stop)
		update_highlight(model, start)
#		import cProfile
#		cProfile.runctx('update_highlight(model, start)',  globals(), locals(), 'prof')

def on_delete(model, fromMark, toMark):
	if model._highlight.lexer :
		model._highlight.no_tagMarkZone = None
		update_highlight(model, Index(model, fromMark))


def update_highlight(textWidget, insertPoint):
	start = find_startPoint(textWidget,insertPoint)
	content = textWidget.get(start,"end")
	textWidget._highlight.startPoint = start
	tokens = textWidget._highlight.lexer.get_tokens_unprocessed(content)
	tokens = append_lastSyncPoint(tokens, len(content))
	tokens = filter_token_stream(textWidget, tokens, start, insertPoint)
	textWidget._highlight.tokensStream = tokens
	_update_a_token(textWidget, False)

def find_next(textWidget, index, forceAfter=False):
	next = textWidget.mark_next(index)
	while next:
		nextI = Index(textWidget, next, True)
		if next.startswith("DP::SH::_synctx_") and (not forceAfter or nextI > index):
			break
		next = textWidget.mark_next(next)
	if next:
		return next, nextI
	return None, Index(textWidget, "end", True)

def find_previous(textWidget, index):
	previous = textWidget.mark_previous(index)
	while previous:
		previousI = Index(textWidget, previous, True) 
		if previous.startswith("DP::SH::_synctx_"):
			if previousI < index:
				break
			#remove all syncpoint at index pos
			textWidget.mark_unset(previous)
		previous = textWidget.mark_previous(previousI)
	if previous:
		return previousI
	return None

def find_startPoint(textWidget, index):
	previous =  find_previous(textWidget, index)
	if previous:
		return find_previous(textWidget, previous) or Index(textWidget, "1.0")
	return Index(textWidget, "1.0")
	
def append_lastSyncPoint(tokens, lenth):
	for i in tokens:
		yield i
	yield lenth, SyncPoint, ''

def filter_token_stream(textWidget, tokens, startPoint, insertPoint):
	currentPos = (0, startPoint)

	# we must not stop before this point
	validSyncPoint = find_next(textWidget, insertPoint, forceAfter=True)

	# the last syncPoint already in the buffer checked
	lastSyncPoint = (None, startPoint)

	for i, t, v in tokens:
		if t == SyncPoint:
			if i != currentPos[0]:
				currentPos = (i, startPoint + "%dc"%i)

			# remove all syncPoint between lastSyncPoint and currentPos
			
			# lastSyntPoint[1] is a indice => return mark at pos
			i = find_next(textWidget, lastSyncPoint[1])

			# there is syncPoint in the buffer
			if i[0] is not None:

				# i[0] in a mark name => will return different mark at same pos if exist else next mark
				next = find_next(textWidget, i[0])
				while i[1]==next[1]:
					textWidget.mark_unset(next[0])
					next = find_next(textWidget, i[0])
			
				if next[1] <= currentPos[1]:
					i = next
					while i[1]<currentPos[1]:
						textWidget.mark_unset(i[0])
						i = find_next(textWidget, i[1])
				
					if i[0] is not None and i[1] == currentPos[1]:
						next = find_next(textWidget, i[0])
						while next[1]==currentPos[1]:
							textWidget.mark_unset(i[0])
							i = next
							next = find_next(textWidget, i[0])
						lastSyncPoint = i

			# mark the new one if not already in the buffer
			if currentPos[1] != i[1]:
				lastSyncPoint = ("DP::SH::_synctx_%d"%textWidget._highlight.markNb, currentPos[1])
				Tkinter.Text.mark_set(textWidget, *lastSyncPoint)
				textWidget._highlight.markNb += 1
				
				# we have finish to handle syncPoint => go to next stream element
				continue
			
			# do not stop to soon
			if textWidget._highlight.last_stopToken <= currentPos[1] and validSyncPoint[1] <= currentPos[1]:
				raise StopIteration

		else:
			l = len(v)
			if not l:
				continue

			if i == currentPos[0]:
				start = currentPos[1]
			else:
				start = startPoint + "%dc"%i
			
			currentPos = (currentPos[0]+l, start+"%dc"%l)
			yield start, currentPos[1], t


def is_in_safeZone(textWidget, start, stop):
	try:
		nstart, nstop = textWidget._highlight.no_tagMarkZone
		if( start >= nstart and stop <= nstop):
			return True
	except TypeError:
		pass
	return False


def process_token(tw, elem):
	tagdel = tw.tag_remove

	startP,endP,t = elem
	token_name = "DP::SH::%s"%t.name.replace('.', '_')
	
	if tw.tag_nextrange(token_name, startP, endP) != (startP._index, endP._index):
	
		tags = set()

		if not is_in_safeZone(tw, startP, endP):
		
			for n in tw.tag_names(startP):
				if n != token_name:
					tags.add(n)
	
			def process_dump(key, name, pos):
				if not name.startswith("DP::SH::"):
					return
				
				if name == token_name:
					return
			
				pos = Index(tw, pos)

				if key == 'tagon' and pos != endP:
					tags.add(name)
				if key == 'tagoff' and pos != startP:
					tags.add(name)

			tw.dump(startP, endP, command=process_dump, tag=True)

		map(lambda n: tagdel(n, startP, endP), tags)
		tw.tag_add(token_name, startP, endP)

	if tw._highlight.last_stopToken < endP:
		tw._highlight.last_stopToken = endP



def _update_a_token(textWidget,realTime=False):
	tokens = textWidget._highlight.tokensStream
	startPoint = textWidget._highlight.startPoint

	if realTime:
		map(lambda t, tw=textWidget : process_token(tw,t) , tokens)
		textWidget._highlight.last_stopToken = Index(textWidget, "1.0")
	else:
		def do_next():
			try:
				process_token(textWidget, tokens.next())
				textWidget.after_idle(do_next)
			except StopIteration:
				textWidget._highlight.last_stopToken = Index(textWidget,"1.0")

		textWidget.after_idle(do_next)

