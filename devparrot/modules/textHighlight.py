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

from devparrot.core.utils.posrange import Index, Start

from pygments.token import Token

import Tkinter
import weakref


_fonts = {}
_styles = {}
_tokens_name = {}
_configSection = None
_lexers_cache = {}

def init(configSection, name):
    global _configSection
    _configSection=configSection
    configSection.add_variable("hlstyle", "default")
    configSection.active.register(activate)

def activate(var, old):
    if var.get():
        create_fonts()
        create_styles()
        session.config.textView.font.register(on_font_changed)
        _configSection.hlstyle.register(on_style_changed)
        session.get_documentManager().connect("documentAdded",on_new_document)
    else:
        pass

def on_font_changed(var, old):
    if var.get() == old:
        return
    create_fonts()
    create_styles()
    for document in session.get_documentManager():
        create_style_table(document.model)

def on_style_changed(var, old):
    if var.get() == old:
        return
    create_styles()
    for document in session.get_documentManager():
        create_style_table(document.model)

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
    
    _style = get_style_by_name(_configSection.get("hlstyle"))
    
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
        self.idle_handle = None


def on_new_document(document):
    create_style_table(document.model)

    document.connect('pathChanged', lambda document, oldPath: init_and_highlight(document))
    document.model._highlight = HighlightContext()
    init_and_highlight(document)
    document.model.connect('insert', on_insert)
    document.model.connect('delete', on_delete)
    document.model.connect('replace', on_replace)
    Tkinter.Text.mark_set(document.model, "DP::SH::_synctx_START", "1.0")
    Tkinter.Text.mark_gravity(document.model, "DP::SH::_synctx_START", "left")

def init_and_highlight(document):
    def find_lexer(mimetype):
        from pygments.lexers import get_lexer_for_mimetype
        from pygments.util import ClassNotFound
        mime = str(str(mimetype))
        lexer = None
        try:
            lexer = _lexers_cache[mime]()
        except KeyError:
            try:
                lexer = get_lexer_for_mimetype(mime)
                _lexers_cache[mime] = lexer.__class__
            except ClassNotFound:
                pass
        return lexer

    if not document.has_a_path():
        return

    document.model._highlight.lexer = find_lexer(document.get_mimetype())
    if document.model._highlight.lexer:
        update_highlight(document.model, Start, document.model.calculate_distance(Start, document.model.index("end")))

def on_insert(model, insertMark, text):
    if model._highlight.lexer :
        l = len(text)
        start = model.index(insertMark)
        stop = model.addchar(start, l)

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
        update_highlight(model, model.index(fromMark), 0)

def on_replace(model, fromMark, toMark, text):
    on_insert(model, fromMark, text)

def update_highlight(model, new_insertPoint, new_length):
    if model._highlight.idle_handle is None:
        handle = model.after_idle(lambda : _update_highlight(model, new_insertPoint, new_length))
        model._highlight.idle_handle = (handle, new_insertPoint, new_length)
        return

    idle_handle, old_insertPoint, old_length = model._highlight.idle_handle
    old_end = model.addchar(old_insertPoint, old_length)
    new_end = model.addchar(new_insertPoint, new_length)
    insertPoint = min(new_insertPoint, old_insertPoint)
    stopPoint = max(new_end, old_end)
    length = model.calculate_distance(insertPoint, stopPoint)
    model.after_cancel(model._highlight.idle_handle[0])
    handle = model.after_idle(lambda : _update_highlight(model, insertPoint, length))
    model._highlight.idle_handle = (handle, insertPoint, length)

def _update_highlight(model, insertPoint, length):
    model._highlight.idle_handle = None
    start_name, start_pos = find_previous(model,insertPoint)
    content = model.get(str(start_pos), "end")
    tokens = model._highlight.lexer.get_tokens_unprocessed(content)
    update_tokens(model, tokens, start_name, start_pos, insertPoint, length)

def find_next(model, index, forceAfter=False):
    next = model.mark_next(str(index))
    while next:
        if next.startswith("DP::SH::_synctx_"):
            nextI = model.index(next)
            if not forceAfter or nextI > index:
                break
        next = model.mark_next(next)
    if next:
        return next, nextI
    return None, None

def find_previous(model, index):
    previous = model.mark_previous(str(index))
    while previous:
        if previous.startswith("DP::SH::_synctx_"):
            previousI = model.index(previous)
            break
        previous = model.mark_previous(previous)
    if previous:
        return previous, previousI
    return "DP::SH::_synctx_START", Start

def update_tokens(model, tokens, startPoint_text, startPoint_pos, insertPoint, length):
    currentPos_buf = 0
    currentPos_wid = startPoint_pos

    # we must not stop before this point
    _, SyncPointToReach = find_next(model, insertPoint, forceAfter=True)
    if SyncPointToReach is None:
        SyncPointToReach = model.index("end")

    # the last syncPoint already in the buffer checked
    lastSyncPoint_text = startPoint_text
    lastSyncPoint_pos = startPoint_pos

    tags_to_add = {}

    markNb = model._highlight.markNb

    noTagStart = insertPoint
    noTagStop  = model.addchar(insertPoint,length)

    for i, t, v in tokens:
        if not v:
            continue
        l = len(v)

        # get start of the token.
        start = currentPos_wid

        #get end of the token.
        currentPos_buf += l
        currentPos_wid = model.addchar(currentPos_wid, l)

        #get some info on the token.
        list_for_token = tags_to_add.setdefault(t, [])
        token_name = _tokens_name[t]

        # do the job
        if start<noTagStart or currentPos_wid > noTagStop:
            clean_tokens(model, start.text, currentPos_wid.text, token_name)
        list_for_token.extend((start.text, currentPos_wid.text))

        # This a end of a line without any special Token => Add a syncPoint
        if t is Token.Text and v == u"\n":

            # we are not in the insert region. It may have some syncPoint in between
            if lastSyncPoint_pos<noTagStart or currentPos_wid>noTagStop:
                # find next syncPoint after(or at) currentPos and remove all other between
                # if there is no syncPoint => no need to clean
                if lastSyncPoint_pos is not None:
                    lastSyncPoint_text, lastSyncPoint_pos = find_next_and_clean_syncPoints(model, lastSyncPoint_text, lastSyncPoint_pos, currentPos_wid)
    
            # mark the new one if not already in the buffer
            if currentPos_wid != lastSyncPoint_pos:
                lastSyncPoint_text = "DP::SH::_synctx_%d"%markNb
                lastSyncPoint_pos  = currentPos_wid
                Tkinter.Text.mark_set(model, lastSyncPoint_text, lastSyncPoint_pos.text)
                Tkinter.Text.mark_gravity(model, lastSyncPoint_text, "left")
                markNb += 1
                continue

            #stop if pygment give as a syncPoint as same pos that one we already have
            if currentPos_wid >= SyncPointToReach:
                break

    model._highlight.markNb = markNb

    #really add the tags to the model
    for token, positions in tags_to_add.items():
        model.tag_add(_tokens_name[token], *positions)

def find_next_and_clean_syncPoints(model, currentSync_text, currentSync_pos, currentPos):
    # remove all syncPoint between lastSyncPoint and currentPos

    # currentSync_text in a mark name => will return different mark at same pos if exist else next mark. will not return currentSync_text
    next = find_next(model, currentSync_text)

    # no sync point
    if next[0] == None:
        return currentSync_text, currentSync_pos

    #remove all duplicate at currentSync
    while currentSync_pos==next[1]:
        model.mark_unset(next[0])
        next = find_next(model, currentSync_text)

    if next[1] <= currentPos:
        currentSync_text, currentSync_pos = next
        #remove all tag strictly before currentPos
        while currentSync_text and currentSync_pos<currentPos:
            model.mark_unset(currentSync_text)
            currentSync_text, currentSync_pos = find_next(model, currentSync_pos)

        #remove all duplicate at currentPos
        if currentSync_text and currentSync_pos == currentPos:
            next = find_next(model, currentSync_text)
            while next[0] and next[1]==currentPos:
                model.mark_unset(currentSync_text)
                currentSync_text, currentSync_pos = next
                next = find_next(model, currentSync_text)

    return currentSync_text, currentSync_pos



def clean_tokens(model, start, end, token_name):
    if model.tag_nextrange(token_name, start, end) != (start, end):
    
        tags = set()

        for n in model.tag_names(start):
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

        model.dump(start, end, command=process_dump, tag=True)
        map(lambda n : model.tag_remove(n, start, end), tags)

