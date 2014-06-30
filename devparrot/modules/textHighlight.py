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
from devparrot.core.modules import BaseModule

from devparrot.core.utils.posrange import Index, Start

from pygments.token import Token

import Tkinter
import weakref

_tokens_name = {}
_lexers_cache = {}

class HighlightContext(object):
    def __init__(self):
        self.lexer = None
        self.idle_handle = None

class TextHighlight(BaseModule):
    def __init__(self, configSection, name):
        BaseModule.__init__(self, configSection, name)
        configSection.add_variable("hlstyle", "default")

    def activate(self):
        self._create_fonts()
        self._create_styles()
        self.font_changed_handle = session.config.textView.font.register(self._on_font_changed)
        self.style_changed_handle = self.configSection.hlstyle.register(self._on_style_changed)

    def deactivate(self):
        session.config.textView.font.unregister(self.font_changed_handle)
        self.configSection.hlstyle.unregister(self.style_changed_handle)

    def _on_font_changed(self, var, old):
        if var.get() == old:
            return
        self._create_fonts()
        self._create_styles()
        for document in session.get_documentManager():
            self.create_style_table(document.model)

    def _on_style_changed(self, var, old):
        if var.get() == old:
            return
        self._create_styles()
        for document in session.get_documentManager():
            self.create_style_table(document.model)

    def _create_fonts(self):
        self._fonts = {}
        self._fonts[(False,False)] = tkFont.Font(font=session.config.get("textView.font"))
        self._fonts[(True,False)] = self._fonts[(False,False)].copy()
        self._fonts[(True,False)].configure(weight='bold')
        self._fonts[(False,True)] = self._fonts[(False,False)].copy()
        self._fonts[(False,True)].configure(slant='italic')
        self._fonts[(True,True)] = self._fonts[(False,False)].copy()
        self._fonts[(True,True)].configure(slant='italic',weight='bold')

    def _create_styles(self):
        from pygments.styles import get_style_by_name
        global _tokens_name

        self._style = get_style_by_name(self.configSection.get("hlstyle"))

        tkStyles = dict(self._style)
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

        self._styles = {}
        for token,tStyle in tkStyles.items():
            token = _tokens_name.setdefault(token,"DP::SH::%s"%str(token))
            self._styles[token] = {}

            self._styles[token]['foreground'] = "#%s"%tStyle['color'] if tStyle['color'] else ""
            self._styles[token]['background'] = "#%s"%tStyle['bgcolor'] if tStyle['bgcolor'] else ""

            self._styles[token]['underline'] = tStyle['underline']
            self._styles[token]['font'] = self._fonts[(tStyle['bold'],tStyle['italic'])]

        self._styles.setdefault("DP::SH::Token.Error", {})['background'] = "red"
        self._styles.setdefault("DP::SH::Token.Generic.Error", {})['background'] = "red"

    def create_style_table(self, textWidget):
        textWidget.configure(background=self._style.background_color,selectbackground=self._style.highlight_color)
        for token, style in self._styles.items():
            textWidget.tag_configure(token, style)

    def on_pathChanged(self, document, oldPath):
        self.init_and_highlight(document)

    def on_documentAdded(self, document):
        self.create_style_table(document.model)

        document.model._highlight = HighlightContext()
        self.init_doc(document)

    def init_doc(self, document):
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

    def init_and_highlight(self, document):
        self.init_doc(document)
        if document.model._highlight.lexer:
            update_highlight(document.model, Start, document.model.getend())

    def on_textSet(self, document):
        if document.model._highlight.lexer :
            update_highlight(document.model, Start, document.model.getend())

    def on_insert(self, model, insertMark, text):
        if model._highlight.lexer :
            start = model.index(insertMark)
            stop = model.addchar(start, len(text))

            for name in model.tag_names(str(start)):
                if not name.startswith("DP::SH::"):
                    continue
                model.tag_remove(name, str(start), str(stop))

            update_highlight(model, start, stop)

    def on_delete(self, model, fromMark, toMark):
        if model._highlight.lexer :
            update_highlight(model, fromMark, fromMark)

    def on_replace(self, model, fromMark, toMark, text):
        self.on_insert(model, fromMark, text)

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

