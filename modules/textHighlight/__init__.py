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

def on_insert(model, insertMark, text):
	if model._highlight.lexer :
		update_highlight(model, insertMark)

def on_delete(model, fromMark, toMark):
	if model._highlight.lexer :
		update_highlight(model, fromMark)


def update_highlight(textWidget, insertPoint):
	start = textWidget.index(find_startPoint(textWidget,insertPoint))
	content = textWidget.get(start,"end")
	tokens = textWidget._highlight.lexer.get_tokens_unprocessed(content)
	tokens = stop_at_syncPoint(textWidget, tokens, start, insertPoint)
	textWidget._highlight.colorizeContext = [tokens, start, start]
	textWidget.after_idle(lambda tw=textWidget: _update_a_token(tw))

def find_next(textWidget, index):
	next = textWidget.mark_next(index)
	while next and (not next.startswith("DP::SH::_synctx_") or not textWidget.compare(next, ">", index)):
		next = textWidget.mark_next(next)
	return next or "end"

def find_previous(textWidget, index):
	previous = textWidget.mark_previous(index)
	while previous and (not previous.startswith("DP::SH::_synctx_") or not textWidget.compare(previous, "<", index)):
		previous = textWidget.mark_previous(previous)
	return previous

def find_startPoint(textWidget, index):
	previous =  find_previous(textWidget, index)
	if previous:
		return find_previous(textWidget, previous) or "1.0"
	return "1.0"

def stop_at_syncPoint(textWidget, tokens, startPoint, insertPoint):
	from pygments.token import _ContextToken
	syncPoint = textWidget.index(find_next(textWidget, insertPoint))
	distance = textWidget.calcule_distance(startPoint, syncPoint)
	for i,t,v in tokens:
		if not v:
			continue
		currentPos = "%s + %d c"%(startPoint, i)
		if isinstance(t,_ContextToken) and t[1]:
			while i > distance:
				next = find_next(textWidget, syncPoint)
				distance += textWidget.calcule_distance(syncPoint, next)
				syncPoint = textWidget.index(next)
			if i == distance and textWidget.compare(textWidget._highlight.last_stopToken, "<=", currentPos) :
				raise StopIteration
			yield i,t,v,True
		else:
			yield i,t,v,False


def _update_a_token(textWidget,realTime=False):
	prefix = "DP::SH::"
	markoff = textWidget.mark_unset
	tagdel = textWidget.tag_remove
	tagadd = textWidget.tag_add
	
	def markon(pos):
		textWidget.mark_set("DP::SH::_synctx_%d"%textWidget._highlight.markNb, pos)
		textWidget._highlight.markNb += 1
	
	def process_itvs(elem):
		i,t,v,s = elem
		token_name = "DP::SH::%s"%str(t).replace('.','_')
		token = (textWidget._highlight.colorizeContext[2],
			 textWidget.index("%s+%dc"%(textWidget._highlight.colorizeContext[2],len(v)))
			)

		textWidget._highlight.colorizeContext[2] = token[1]
		context = {
			"tags" : set([token_name]) if token_name != "DP::SH::Token_Text" else set(),
			"mark" : None,
			"openedPos" : None
		}
		
		def process_dump(ctx, key, name, pos):
			if name[:8] == prefix:
				def first_mark():
					if pos==token[0]:
						ctx['mark'] = {'name':name, 'pos':pos}
					else:
						markoff(name)	
					markf = other_mark
				def other_mark():
					markoff(name)
				markf = first_mark if s else other_mark
							
				if key == 'mark':
					markf()
				if key == 'tagon':
					if name != token_name:
						ctx['tags'].add(name)
					else:
						ctx['openedPos'] = pos
				if key == 'tagoff' and pos != token[0]:
					if name != token_name:
						ctx['tags'].add(name)
					elif (ctx['openedPos'],pos) == token:
						ctx['tags'].remove(token_name)
						ctx['openedPos'] = None

		[process_dump(context,"tagon",n,token[0]) for n in textWidget.tag_names(token[0])]
		map(lambda item : process_dump(context, *item), textWidget.dump(*token, mark=True, tag=True))
		
		tags = context["tags"]
		mark = context["mark"]
		openedPos = context["openedPos"]

		if s and not mark:
			textWidget.mark_set("DP::SH::_synctx_%d"%textWidget._highlight.markNb, token[0])
			textWidget._highlight.markNb += 1			
			#if token_name in tags and len(tags[token_name]) == 1 and \
		#	tags[token_name][0] ==  token:
		#		del tags[token_name]
		#else:
	
		def filter_(name, tl):
			return name == token_name and len(tl)==1 and tl[0]==token

		for name in tags:
			if name == token_name:
				tagadd(token_name, *token)
			else:
				tagdel(name, *token)

		if textWidget._highlight.last_stopToken < token[1]:
			textWidget._highlight.last_stopToken = token[1]
	
	if textWidget._highlight.colorizeContext:
		tokens = textWidget._highlight.colorizeContext[0]
		startPoint = textWidget._highlight.colorizeContext[1]
	else:
		return

	if realTime:
		map(process_itvs, tokens)
		textWidget._highlight.last_stopToken = "1.0"
	else:
		try :
			process_itvs(tokens.next())
			textWidget.after_idle(lambda tw=textWidget: _update_a_token(tw))

		except StopIteration:
			textWidget._highlight.last_stopToken = "1.0"
			pass



