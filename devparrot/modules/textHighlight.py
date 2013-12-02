#    This file is part of DevParrot.
#
#    Author: Matthieu Gautier <matthieu.gautier@devparrot.org>
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
#    Copyright 2011-2013 Matthieu Gautier


import tkFont
import os.path

from devparrot.core import session

from devparrot.core.utils.posrange import Index, Index_

from pygments.token import SyncPoint, Token
from devparrot.core.utils.variable import fcb

import Tkinter
import weakref


_fonts = {}
_styles = {}
_tokens_name = {}
_moduleName = None
_lexers_cache = {}

def init(configSection, name):
    global _moduleName
    _moduleName=name
    configSection.add_variable("hlstyle", "default")
    configSection.active.register(activate)

def activate(var, old):
    if var.get():
        create_fonts()
        create_styles()
        session.config.textView.font.register(on_font_changed)
        session.config.modules[_moduleName].hlstyle.register(on_style_changed)
        session.eventSystem.connect("newDocument",on_new_document)
    else:
        pass

def on_font_changed(var, old):
    if var.get() == old:
        return
    create_fonts()
    create_styles()

def on_style_changed(var, old):
    if var.get() == old:
        return
    create_styles()

def create_fonts():
    global _fonts
    _fonts[(False,False)] = tkFont.Font(font=session.config.get("textView.font"))
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
    global _style
    global _tokens_name
    
    _style = get_style_by_name(session.config.get("modules.%s.hlstyle"%_moduleName))
    
    tkStyles = dict(_style)
    for token in sorted(tkStyles):
        while True:
            if token == Token:
                break
            parent = token.parent
            if not tkStyles[token]['color']:
                tkStyles[token]['color'] = tkStyles[parent]['color']
            if not tkStyles[token]['bgcolor']:
                tkStyles[token]['bgcolor'] = tkStyles[parent]['bgcolor']
            if tkStyles[token]['color'] and tkStyles[token]['bgcolor']:
                break
            token = parent
            
    for token,tStyle in tkStyles.items():
        token = _tokens_name.setdefault(token,"DP::SH::%s"%str(token))
        _styles[token] = {}
        
        _styles[token]['foreground'] = "#%s"%tStyle['color'] if tStyle['color'] else ""
        _styles[token]['background'] = "#%s"%tStyle['bgcolor'] if tStyle['bgcolor'] else ""

        _styles[token]['underline'] = tStyle['underline']
        _styles[token]['font'] = _fonts[(tStyle['bold'],tStyle['italic'])]

    _styles.setdefault("DP::SH::Token.Error", {})['background'] = "red"
    _styles.setdefault("DP::SH::Token.Generic.Error", {})['background'] = "red"
        

def create_style_table(textWidget):
    textWidget.configure(background=_style.background_color,selectbackground=_style.highlight_color)
    for token, style in _styles.items():
        textWidget.tag_configure(token, style)

class HighlightContext(object):
    def __init__(self):
        self.lexer = None
        self.markNb=0

def on_new_document(document):
    create_style_table(document.model)
    session.config.textView.font.register(fcb(lambda v, o, tw=weakref.proxy(document.model) : create_style_table(tw), weakref.ref(document)))
    session.config.modules[_moduleName].hlstyle.register(fcb(lambda v, o, tw=weakref.proxy(document.model) : create_style_table(tw), weakref.ref(document)))
    document.connect('pathChanged', lambda document, oldPath: init_and_highlight(document))
    document.model._highlight = HighlightContext()
    init_and_highlight(document)
    document.model.connect('insert', on_insert)
    document.model.connect('delete', on_delete)
    document.model.connect('replace', on_replace)
    Tkinter.Text.mark_set(document.model, "DP::SH::_synctx_START", "1.0")
    Tkinter.Text.mark_gravity(document.model, "DP::SH::_synctx_START", "left")

def init_and_highlight(document):
    def find_lexer(filename):
        from pygments.lexers import get_lexer_for_mimetype
        from pygments.util import ClassNotFound
        from xdg import Mime
        mime = str(Mime.get_type_by_name(filename))
        lexer = None
        try:
            lexer = _lexers_cache[mime](noSyncPoint=False)
        except KeyError:
            try:
                lexer = get_lexer_for_mimetype(mime, noSyncPoint=False)
                _lexers_cache[mime] = lexer.__class__
            except ClassNotFound:
                pass
        return lexer

    if not document.has_a_path():
        return

    filename = os.path.basename(document.get_path())
    document.model._highlight.lexer = find_lexer(filename)
    on_insert(document.model, "1.0", "end")

def on_insert(model, insertMark, text):
    if model._highlight.lexer :
        l = len(text)
        start = Index(model, insertMark)
        stop = Index(model, "%s + %d c"%(insertMark, l))

        for name in model.tag_names(str(start)):
            if not name.startswith("DP::SH::"):
                continue
            model.tag_remove(name, str(start), str(stop))

#		import statprof
#		statprof.reset(1000000-1)
#		statprof.start()
        if True:
#		try:
            update_highlight(model, start, l)
            #import cProfile
            #cProfile.runctx('update_highlight(model, start, l)',  globals(), locals(), 'prof')
#		finally:
#			statprof.stop()
#			statprof.display()

def on_delete(model, fromMark, toMark):
    if model._highlight.lexer :
        update_highlight(model, Index(model, fromMark), 0)

def on_replace(model, fromMark, toMark, text):
    on_insert(model, fromMark, text)

def update_highlight(textWidget, insertPoint, length):
    start_name, start_pos = find_previous(textWidget,insertPoint)
    content = textWidget.get(start_pos.text, "end")
    tokens = textWidget._highlight.lexer.get_tokens_unprocessed(content)
    tokens = append_lastSyncPoint(tokens, len(content))
    update_tokens(textWidget, tokens, start_name, start_pos, insertPoint, length)

def find_next(textWidget, index, forceAfter=False):
    next = textWidget.mark_next(str(index))
    while next:
        if next.startswith("DP::SH::_synctx_"):
            nextI = Index(textWidget, next, True)
            if not forceAfter or nextI > index:
                break
        next = textWidget.mark_next(next)
    if next:
        return next, nextI
    return None, None

def find_previous(textWidget, index):
    previous = textWidget.mark_previous(str(index))
    while previous:
        if previous.startswith("DP::SH::_synctx_"):
            previousI = Index(textWidget, previous, True)
            break
        previous = textWidget.mark_previous(previous)
    if previous:
        return previous, previousI
    return "DP::SH::_synctx_START", Index(textWidget, "1.0")

def append_lastSyncPoint(tokens, lenth):
    last_is_syncPoint = True
    for i in tokens:
        if i[1] == SyncPoint:
            if not last_is_syncPoint:
                yield i
                last_is_syncPoint = True
        else:
            yield i
            last_is_syncPoint = False
    if not last_is_syncPoint:
        yield lenth, SyncPoint, ''

def update_tokens(textWidget, tokens, startPoint_text, startPoint_pos, insertPoint, length):
    currentPos_buf = 0
    currentPos_wid = startPoint_pos

    # we must not stop before this point
    _, SyncPointToReach = find_next(textWidget, insertPoint, forceAfter=True)
    if SyncPointToReach is None:
        SyncPointToReach = Index(textWidget, "end", True)

    # the last syncPoint already in the buffer checked
    lastSyncPoint_text = startPoint_text
    lastSyncPoint_pos = startPoint_pos

    currentLine_info_line = None

    tags_to_add = {}

    markNb = textWidget._highlight.markNb

    def is_in_safeZone(start, stop, nstart=insertPoint, nstop=Index(textWidget, "%s + %d c"%(insertPoint.text, length), True)):
        return (start >= nstart and stop <= nstop)

    for i, t, v in tokens:
        if t == SyncPoint:
            if i==0:
                continue
            #update current pos
            if i != currentPos_buf:
                currentPos_buf = i
                currentPos_wid = Index(textWidget, "%s + %d c"%(startPoint_pos.text,i), True)

            # no syncPoint so add it directly
            if is_in_safeZone(lastSyncPoint_pos, currentPos_wid):
                lastSyncPoint_text = "DP::SH::_synctx_%d"%markNb
                lastSyncPoint_pos  = currentPos_wid
                Tkinter.Text.mark_set(textWidget, lastSyncPoint_text, lastSyncPoint_pos.text)
                Tkinter.Text.mark_gravity(textWidget, lastSyncPoint_text, "left")
                markNb += 1
                continue

            # find next syncPoint after(or at) currentPos and remove all other between
            # if there is no syncPoint => no need to clean
            if lastSyncPoint_pos:
                lastSyncPoint_text, lastSyncPoint_pos = find_next_and_clean_syncPoints(textWidget, lastSyncPoint_text, lastSyncPoint_pos, currentPos_wid)

            # mark the new one if not already in the buffer
            if currentPos_wid != lastSyncPoint_pos:
                lastSyncPoint_text = "DP::SH::_synctx_%d"%markNb
                lastSyncPoint_pos  = currentPos_wid
                Tkinter.Text.mark_set(textWidget, lastSyncPoint_text, lastSyncPoint_pos.text)
                Tkinter.Text.mark_gravity(textWidget, lastSyncPoint_text, "left")
                markNb += 1
                continue

            #stop if pygment give as a syncPoint as same pos that one we already have
            if currentPos_wid >= SyncPointToReach:
                break

        else:
            l = len(v)
            if not l:
                continue
#			print v,

            # get start of the token
            if i == currentPos_buf:
                start = currentPos_wid
            else:
                start = Index(textWidget, "%s + %d c"%(startPoint_pos.text,i), True)
            
            #get some info on the current line if this is a new one
            if currentLine_info_line != start.line:
                currentLine_info_line = start.line
                currentLine_info_len = int(textWidget.index("%s lineend"%start.text).split('.')[1])
                currentLine_text = "%d.%%d"%currentLine_info_line

            #get end of the token. Try to find it without calling textWidget.index
            currentPos_buf = i+l
            if start.col==currentLine_info_len and v == "\n":
                pos = currentLine_info_line+1
                currentPos_wid = Index_(pos, 0, "%d.0"%pos)
            elif start.col + l > currentLine_info_len:
                currentPos_wid = Index(textWidget, "%s + %dc"%(start.text, l), True)
            else:
                col = start.col+l
                currentPos_wid = Index_(currentLine_info_line, col, currentLine_text%col)

            #get some info on the token
            try:
                list_for_token = tags_to_add[t]
            except:
                list_for_token = tags_to_add.setdefault(t, [])
            try:
                token_name = _tokens_name[t]
            except:
                token_name = _tokens_name.setdefault(token,"DP::SH::%s"%str(t))

            # do the job
            if not is_in_safeZone(start, currentPos_wid):
                clean_tokens(textWidget, start.text, currentPos_wid.text, token_name)
            list_for_token.extend((start.text, currentPos_wid.text))

    textWidget._highlight.markNb = markNb

    #really add the tags to the textWidget
    for token, positions in tags_to_add.items():
        textWidget.tag_add(_tokens_name[token], *positions)

def find_next_and_clean_syncPoints(textWidget, currentSync_text, currentSync_pos, currentPos):
    # remove all syncPoint between lastSyncPoint and currentPos

    # currentSync_text in a mark name => will return different mark at same pos if exist else next mark. will not return currentSync_text
    next = find_next(textWidget, currentSync_text)

    # no sync point
    if next[0] == None:
        return currentSync_text, currentSync_pos

    #remove all duplicate at currentSync
    while currentSync_pos==next[1]:
        textWidget.mark_unset(next[0])
        next = find_next(textWidget, currentSync_text)

    if next[1] <= currentPos:
        currentSync_text, currentSync_pos = next
        #remove all tag strictly before currentPos
        while currentSync_text and currentSync_pos<currentPos:
            textWidget.mark_unset(currentSync_text)
            currentSync_text, currentSync_pos = find_next(textWidget, currentSync_pos)

        #remove all duplicate at currentPos
        if currentSync_text and currentSync_pos == currentPos:
            next = find_next(textWidget, currentSync_text)
            while next[0] and next[1]==currentPos:
                textWidget.mark_unset(currentSync_text)
                currentSync_text, currentSync_pos = next
                next = find_next(textWidget, currentSync_text)

    return currentSync_text, currentSync_pos



def clean_tokens(tw, start, end, token_name):
    if tw.tag_nextrange(token_name, start, end) != (start, end):
    
        tags = set()

        for n in tw.tag_names(start):
            if not n.startswith("DP::SH::"):
                continue
            if n != token_name:
                tags.add(n)

        def process_dump(key, name, pos):
            if not name.startswith("DP::SH::"):
                return

            if name == token_name:
                return

            if key == 'tagon' and pos != end:
                tags.add(name)
            if key == 'tagoff' and pos != start:
                tags.add(name)

        tw.dump(start, end, command=process_dump, tag=True)
        map(lambda n : tw.tag_remove(n, start, end), tags)

