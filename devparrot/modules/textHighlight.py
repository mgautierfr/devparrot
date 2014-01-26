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
        self.idle_handle = None


def on_new_document(document):
    create_style_table(document.model)

    document.connect('pathChanged', lambda document, oldPath: init_and_highlight(document))
    document.model._highlight = HighlightContext()
    init_and_highlight(document)
    document.model.connect('insert', on_insert)
    document.model.connect('delete', on_delete)
    document.model.connect('replace', on_replace)

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
        update_highlight(document.model, Start, document.model.getend())

def on_insert(model, insertMark, text):
    if model._highlight.lexer :
        start = model.index(insertMark)
        stop = model.addchar(start, len(text))

        for name in model.tag_names(str(start)):
            if not name.startswith("DP::SH::"):
                continue
            model.tag_remove(name, str(start), str(stop))

        update_highlight(model, start, stop)

def on_delete(model, fromMark, toMark):
    if model._highlight.lexer :
        update_highlight(model, fromMark, fromMark)

def on_replace(model, fromMark, toMark, text):
    on_insert(model, fromMark, text)

def update_highlight(model, start, stop):
    if model._highlight.idle_handle:
        idle_handle, old_start, old_stop = model._highlight.idle_handle

        start = min(start, old_start)
        stop = max(stop, old_stop)

        model.after_cancel(model._highlight.idle_handle[0])

    # force the min cause model can be shorter than previous time (old_stop).
    stop = min(stop, model.getend())
    handle = model.after_idle(lambda : _update_highlight(model, start, stop))
    model._highlight.idle_handle = (handle, start, stop)

def _update_highlight(model, start, stop):
    model._highlight.idle_handle = None
    safe_zone = (start, stop)
    start = find_previous(model, start)
    stop = find_next(model, stop)
    content = model.get(str(start), "end")
    tokens = model._highlight.lexer.get_tokens_unprocessed(content)
    update_tokens(model, tokens, start, stop, safe_zone)

def find_next(model, index):
    line = min(index.line, model.nbLine)+1
    while line<=model.nbLine and not getattr(model.lineInfos[line], '_hlsafe', False):
        line += 1
    return Index(line, 0)

def find_previous(model, index):
    line = min(index.line, model.nbLine)
    while not getattr(model.lineInfos[line], '_hlsafe', False) and line>1:
        line -= 1
    return Index(line, 0)

def update_tokens(model, tokens, start, stop, safe_zone):
    currentPos = start
    currentPos_str = str(start)

    # the last syncPoint already in the buffer checked
    lastSafeLine = start.line

    tags_to_add = {}

    for i, t, v in tokens:
        if not v:
            continue
        l = len(v)

        # get start of the token.
        token_start = currentPos
        token_start_str = currentPos_str

        #get end of the token.
        currentPos = model.addchar(currentPos, l)
        currentPos_str = str(currentPos)

        #get some info on the token.
        list_for_token = tags_to_add.setdefault(t, [])
        token_name = _tokens_name[t]

        # do the job
        if token_start<safe_zone[0] or currentPos > safe_zone[1]:
            clean_tokens(model, token_start_str, currentPos_str, token_name)
        list_for_token.extend((token_start_str, currentPos_str))

        # We enter a new line
        if token_start.line != currentPos.line:
            currentPos_line = currentPos.line
            # It is safe to start syntax highligh from this line the next time ?
            # This is a nasty monkey patch hack to try to get some extra informations from the lexer
            # This work only if the lexer is RegexLexer and "get_tokens_unprocessed is not redefined.
            try:
                extraTests = tokens.gi_frame.f_locals['statestack'][-1] == 'root' and tokens.gi_frame.f_locals['action'] is Token.Text
            except KeyError:
                extraTests = True
            if t is Token.Text and v == u"\n" and extraTests:

                for line in xrange(lastSafeLine+1, currentPos_line):
                    model.lineInfos[line]._hlsafe = False

                try:
                    if currentPos_line >= stop.line and model.lineInfos[currentPos_line]._hlsafe:
                        # we passed our stop position and we've reached a line already know to be safe.
                        #No need to go futher
                        break

                    lastSafeLine = currentPos_line
                    model.lineInfos[lastSafeLine]._hlsafe = True
                except IndexError:
                    # currentPos_line > self.nbLine
                    # end of the document, just pass
                    pass
            else:
                #we change line without syncpoint, clean the safe line
                try:
                    for line in xrange(token_start.line+1, currentPos_line+1):
                        model.lineInfos[line]._hlsafe = False
                except IndexError:
                    pass


    #really add the tags to the model
    for token, positions in tags_to_add.items():
        model.tag_add(_tokens_name[token], *positions)


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

