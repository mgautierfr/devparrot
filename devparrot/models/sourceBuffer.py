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


import ttk
from ttk import Tkinter

import re

from devparrot.core import session, utils
from devparrot.core.utils.posrange import Index, Start
from devparrot.core.errors import *
from devparrot.core import mimemapper

import rangeInfo


def insert_char(event):
    if event.widget and event.char:
        event.widget.insert('insert', event.char)

class LineInfo(object):
    def __init__(self, lenght):
        self.len = lenght

    def __repr__(self):
        return "<LineInfo, len=%d>"%self.len

class ModelInfo(object):
    def __init__(self):
        self.reinit()

    def reinit(self):
        # Tkindex start line at 1, we add a empty element to simplify operation
        self.lineInfos = [None, LineInfo(0)]
        self.nbLine = 1

    def insert(self, index, text):
        #import pdb; pdb.set_trace()
        if index.line > self.nbLine:
            index = Index(self.nbLine, self.lineInfos[self.nbLine].len)
        lines = text.split('\n')
        if len(lines) == 1:
            self.lineInfos[index.line].len += len(lines[0])
        else:
            linelen = self.lineInfos[index.line].len
            # insert first line in the "currentline"
            self.lineInfos[index.line].len = index.col +len(lines[0])
            # insert last line after.
            self.lineInfos[index.line+1:index.line+1] = [LineInfo(len(lines[-1])+linelen-index.col)]
            # insert all in between lines
            self.lineInfos[index.line+1:index.line+1] = [LineInfo(len(l)) for l in lines[1:-1]]
        self.nbLine += len(lines)-1

    def delete(self, index1, index2):
        #import pdb; pdb.set_trace()
        if index1.line == index2.line:
            self.lineInfos[index1.line].len -= index2.col - index1.col
        else:
            # remove the left part of the first line.
            self.lineInfos[index1.line].len = index1.col

            # remove in between line.
            del self.lineInfos[index1.line+1:index2.line]
            try:
                # add left part of the last line in the firt line
                self.lineInfos[index1.line].len += self.lineInfos[index1.line+1].len - index2.col
                # remove the last line
                del self.lineInfos[index1.line+1]
            except IndexError:
                #there is no (more) line after index1.
                if index1.col == 0:
                    #we remove all the content of the last line, delete it.
                    del self.lineInfos[index1.line]
                else:
                    #we must not remove the line
                    #increment nbLine to cancel futur decrementation
                    self.nbLine += 1
                # index2 was out of range (end), no pb.
                pass
        self.nbLine -= index2.line-index1.line

    def addline(self, index, line = 1):
        if line < 0:
            return self.delline(index, -line)
        newLine = index.line+line
        if newLine > self.nbLine:
            return Index(self.nbLine+1, 0)
        newCol = min(self.lineInfos[newLine].len, index.col)
        return Index(newLine, newCol)

    def delline(self, index, line = 1):
        if line < 0:
            return self.addline(index, -line)
        newLine = max(1, index.line-line)
        newCol = min(self.lineInfos[newLine].len, index.col)
        return Index(newLine, newCol)

    def addchar(self, index, char = 1):
        if char < 0:
            return self.delchar(index, -char)
        #import pdb; pdb.set_trace()
        newCol = index.col + char
        newLine = index.line
        while newCol > self.lineInfos[newLine].len:
            newCol -= self.lineInfos[newLine].len
            if newCol:
                newLine += 1
                newCol -= 1
                if newLine > self.nbLine:
                    return Index(newLine, 0)
        return Index(newLine, newCol)

    def delchar(self, index, char = 1):
        #import pdb; pdb.set_trace()
        if char < 0:
            return self.delchar(index, -char)
        if index.col >= char:
            #everything nice
            return Index(index.line, index.col-char)
        char -= index.col
        newCol = 0
        newLine = index.line
        while char:
            newLine -= 1
            if not newLine:
                #No more to go back
                return Start
            char -= 1
            if char <= self.lineInfos[newLine].len:
                # found the right line
                newCol = self.lineInfos[newLine].len - char
                break
            char -= self.lineInfos[newLine].len
        return Index(newLine, newCol)

    def linestart(self, index):
        return Index(index.line, 0)

    def lineend(self, index):
        return Index(index.line, self.lineInfos[index.line].len)

    def getend(self):
        return Index(self.nbLine, self.lineInfos[self.nbLine].len)

    def calculate_distance(self, first, second):
        distance = second.col - first.col
        for i in range(first.line, second.line):
            distance += self.lineInfos[i].len + 1
        return distance

class TextModel(Tkinter.Text, ModelInfo):
    def __init__(self):
        Tkinter.Text.__init__(self,session.get_globalContainer(),
                                  tabstyle="wordprocessor")
        ModelInfo.__init__(self)

        # undo redo stuff
        self.undoredoStack = []
        self._nbModif = 0
        # if nbModifAtLastChange == nbModif => buffer not modified since last change
        # if nbModifAtLastChange == -1 => There is no "saved state" in undoredoStack
        self._nbModifAtLastChange = 0

        # rangeInfo stuff
        self.rangeInfo = rangeInfo.Document()

    @property
    def nbModifAtLastChange(self):
        return self._nbModifAtLastChange

    @nbModifAtLastChange.setter
    def nbModifAtLastChange(self, value):
        modified = (self._nbModifAtLastChange != self.nbModif)
        self._nbModifAtLastChange = value
        if modified != (self._nbModifAtLastChange != self.nbModif):
            session.eventSystem.event('modified')(self, not modified)

    @property
    def nbModif(self):
        return self._nbModif

    @nbModif.setter
    def nbModif(self, value):
        modified = (self._nbModifAtLastChange != self.nbModif)
        self._nbModif = value
        if modified != (self._nbModifAtLastChange != self.nbModif):
            session.eventSystem.event('modified')(self, not modified)

    # Selection Operations
    def sel_clear(self):
        """Remove any selection set on the text.
           Do not delete the selected text.
        """
        try:
            self.tag_remove('sel', '1.0', 'end')
        except TclError:
            pass
      
        try:
            self.mark_unset('sel.anchor', 'sel.first', 'sel.last')
        except TclError:
            pass
        session.eventSystem.event('selection')(self)
   
    def sel_setAnchor(self, index):
        self.mark_set('sel.anchor', str(index))
   
    def sel_isAnchorSet(self):
        try:
            Tkinter.Text.index(self, 'sel.anchor')
            return True
        except TclError:
            return False

    def sel_isSelection(self):
        try:
            Tkinter.Text.index(self, 'sel.first')
            return True
        except TclError:
            return False

    def sel_update(self):
        try:
            if self.compare('sel.anchor', '<', 'insert'):
                self.mark_set('sel.first', 'sel.anchor')
                self.mark_set('sel.last', 'insert')
            elif self.compare('sel.anchor', '>', 'insert'):
                self.mark_set('sel.first', 'insert')
                self.mark_set('sel.last', 'sel.anchor')
            else:
                return

            self.tag_remove('sel', '1.0', 'end')
            self.tag_add('sel', 'sel.first', 'sel.last')
            session.eventSystem.event('selection')(self)
        except TclError as e:
            pass
   
    def sel_delete(self):
        """Delete the selected text."""
        try:
            self.delete('sel.first', 'sel.last')
        except BadArgument:
            pass

        self.sel_clear( )

    def index(self, tkIndex):
        """Return a Index from a tkIndex"""
        if isinstance(tkIndex, Index):
            return tkIndex
        if tkIndex == "end":
            return self.getend()
        try:
            _split = tkIndex.split('.')
            split = (int(_split[0]), int(_split[1]))
        except ValueError:
            try:
                index = Tkinter.Text.index(self, tkIndex)
                _split = index.split('.')
                split = (int(_split[0]), int(_split[1]))
            except TclError:
                raise BadArgument("{!r} is not a valid index".format(tkIndex))
        except IndexError:
            raise BadArgument("{!r} is not a valid index".format(tkIndex))
        return Index(split[0], split[1])

    def addchar(self, index, char = 1):
        if char > 0:
            return self.index("%s + %s c"%(index, char))
        return self.index("%s - %s c"%(index, -char))

    def delchar(self, index, char = 1):
        return self.addchar(index, -char)

    def calculate_distance(self, first, second):
        if first.line == second.line:
            return second.col - first.col
        return self.tk.call(self._w, "count", "-chars", str(first), str(second))

    # Overloads
    def mark_set( self, name, index ):
        index = self.index(index)
        Tkinter.Text.mark_set(self, name, str(index) )
        session.eventSystem.event('mark_set')(self, name, index)
        if name == 'insert':
            self.sel_update()
        
    def insert(self, index, text, *args, **kword):
        index = self.index(index)
        orig_len = self.calculate_distance(Start, index)
        Tkinter.Text.insert(self, str(index), text, *args)
        ModelInfo.insert(self, index, text)
        if kword.get('updateUndo', True):
            self.add_change(type='insert', index=index, text=text)
        if kword.get('forceUpdate', False):
            self.update()
        #self.rangeInfo.parse_text(self.get("1.0", "end"), changeIndex=orig_len, changeLen=len(text))
        session.eventSystem.event('insert')(self, index, text)
    
    def delete(self, index1, index2, updateUndo=True):
        index1 = self.index(index1)
        index2 = self.index(index2)
        text = self.get(str(index1), str(index2))
        ttk.Tkinter.Text.delete(self, str(index1), str(index2))
        ModelInfo.delete(self, index1, index2)
        if updateUndo:
            self.add_change(type='delete', index=index1, oldText=text)
        #self.rangeInfo.parse_text(self.get("1.0", "end"), changeIndex=self.calculate_distance(Start, index1), changeLen=-len(text))
        session.eventSystem.event('delete')(self, index1, index2)

    def replace(self, index1, index2, text, updateUndo=True):
        index1 = self.index(index1)
        index2 = self.index(index2)
        oldtext = self.get(str(index1), str(index2))
        self.tk.call((self._w, 'replace', str(index1), str(index2), text))
        ModelInfo.delete(self, index1, index2)
        ModelInfo.insert(self, index1, text)
        if updateUndo:
            self.add_change(type='replace', index=index1, oldText=oldText, text=text)
        distance = self.calculate_distance(Start, index1)
        content  = self.get("1.0", "end")
        #self.rangeInfo.parse_text(content, changeIndex=distance, changeLen=-len(oldText))
        #self.rangeInfo.parse_text(content, changeIndex=distance, changeLen=len(text))
        session.eventSystem.event('replace')(self, index1, index2, text)

    def undo(self):
        if self.nbModif and self.nbModif <= len(self.undoredoStack):
            lastModif = self.undoredoStack[self.nbModif-1]
            self.nbModif -= 1
            if lastModif['type'] == 'insert':
                lastIndex = self.addchar(lastModif['index'], len(lastModif['text']))
                self.delete(lastModif['index'], lastIndex, updateUndo=False)
            elif lastModif['type'] == 'delete':
                self.insert(lastModif['index'], lastModif['oldText'], updateUndo=False)
            elif lastModif['type'] == 'replace':
                lastIndex = self.addchar(lastModif['index'], len(lastModif['text']))
                self.replace(lastModif['index'], lastIndex, lastModif['oldText'], updateUndo=False)
        self.sel_clear()

    def redo(self):
        if self.undoredoStack and self.nbModif < len(self.undoredoStack):
            lastModif = self.undoredoStack[self.nbModif]
            self.nbModif += 1
            if lastModif['type'] == 'insert':
                self.insert(lastModif['index'], lastModif['text'], updateUndo=False)
            elif lastModif['type'] == 'delete':
                lastIndex = self.addchar(lastModif['index'], len(lastModif['oldText']))
                self.delete(lastModif['index'], lastIndex, updateUndo=False)
            elif lastModif['type'] == 'replace':
                lastIndex = self.addchar(lastModif['index'], len(lastModif['oldText']))
                self.replace(lastModif['index'], lastIndex, lastModif['text'], updateUndo=False)
        self.sel_clear()

    def add_change(self, **kwords):
        self.undoredoStack[self.nbModif:] = [kwords]
        if self.nbModifAtLastChange > self.nbModif:
            self.nbModifAtLastChange = -1
        self.nbModif += 1

    def edit_reset(self):
        self.undoredoStack = []
        if self.nbModif:
            # We cannot go back to a saved state
            self.nbModifAtLastChange = -1
        self.nbModif = 0

    def edit_modified(self, change=None):
        if change is None:
            return self.nbModifAtLastChange != self.nbModif
        if change == False:
            self.nbModifAtLastChange = self.nbModif

    def set_text(self, content):
        def fast_insert(text):
            Tkinter.Text.insert(self, "end", text)
            ModelInfo.insert(self, self.getend(), text)
        Tkinter.Text.delete(self, "1.0", "end")
        self.reinit()

        oldLine = ""
        for line in content:
            if line:
                fast_insert(line)
                oldLine = line
        #remove last "\n" as tkText add one automaticaly
        if oldLine == "\n":
            ttk.Tkinter.Text.delete(self, "end -1c", "end")
            ModelInfo.delete(self, self.index("end -1c"), self.index("end"))

        #self.rangeInfo.fast_parse_text(self.get("1.0", "end"))
        self.edit_reset()
        self.edit_modified(False)
    
    def get_text(self):
        return self.get("1.0", "end")

    def search(self, text, start_search="1.0", end_search="end"):
        if not text:
            return

        count = ttk.Tkinter.IntVar()
        match_start = Tkinter.Text.search(self, text, start_search, stopindex=end_search, forwards=True, exact=False, regexp=True, count=count) 
        while match_start:
            match_end = "{}+{}c".format(match_start, count.get())
            yield self.index(match_start), self.index(match_end)
            if not count.get():
                # avoid infinit loop if regex match 0 len text.
                break
            match_start = Tkinter.Text.search(self, text, match_end, stopindex=end_search, forwards=True, exact=False, regexp=True, count=count)

class SourceBuffer(TextModel):
    def __init__(self, document):
        TextModel.__init__(self)

        tags = [str(self._w), 'devparrot'] + session.config.default_controllers.get()
        self.bindtags(tuple(tags))

        self.document = document # TODO weakref
        self.readOnly = document.is_readonly()
        mimetype = mimemapper.mimeMap.get(str(document.get_mimetype()))

        self.tag_configure('currentLine_tag', background=session.config.currentLine_tag_color.get(mimetype))
        self.tag_raise("currentLine_tag")
        self.tag_raise("sel", "currentLine_tag")

        self.on_configChanged(session.config.font, None)
        session.eventSystem.connect("configChanged", self.on_configChanged)

        self.highlight_tag_protected = False
        self.tag_configure("highlight_tag", background=session.config.highlight_tag_color.get(mimetype))
        self.tag_configure("search_tag", background=session.config.search_tag_color.get(mimetype))
        self.bind("<<Selection>>", self.on_selection_changed)
        self.hl_callId = None
        self.tag_lower("highlight_tag", "sel")
        self.tag_lower("search_tag", "sel")
        self.tag_raise("highlight_tag", "currentLine_tag")
        self.tag_raise("search_tag", "currentLine_tag")

    def on_configChanged(self, var, old):
        import tkFont
        mimetype = mimemapper.mimeMap.get(str(self.document.get_mimetype()))
        if var.name == "currentLine_tag_color":
            self.tag_configure('currentLine_tag', background=var.get(mimetype))
            return

        if var.name == "font":
            self.config(font = var.get(mimetype))

        if var.name in ("font", "tab_width"):
            self.config(tabs = session.config.tab_width.get()*tkFont.Font(font=session.config.font.get()).measure(" "))

    def set_currentLineTag(self):
        self.tag_remove('currentLine_tag', '1.0', 'end')
        if session.config.highlight_current_line.get():
            self.tag_add( 'currentLine_tag', 'insert linestart', 'insert + 1l linestart')

    def on_selection_changed(self, event):
        session.eventSystem.event('selection')(self)
        if self.highlight_tag_protected:
            return
        select = self.tag_ranges("sel")
        if select:
            start_select , stop_select = select 
            text = self.get(start_select , stop_select)
            if self.hl_callId:
                self.after_cancel(self.hl_callId)
            self.hl_callId = self.after(300, self.hl_apply_tag, text)

    def hl_apply_tag(self, text):
        if len(text)>1 :
            self.apply_tag_on_text("highlight_tag", text)
        else:
            self.apply_tag_on_text("highlight_tag", None)
        self.hl_callId = None

    def apply_tag_on_text(self, tag, text):
        self.tag_remove(tag, "1.0","end")

        if text:
            count = ttk.Tkinter.IntVar()
            match_start = ttk.Tkinter.Text.search(self, text, "1.0", stopindex="end", forwards=True, exact=False, count=count)
            while match_start:
                match_end = "{}+{}c".format(match_start,count.get())
                self.tag_add(tag, match_start, match_end)
                match_start = ttk.Tkinter.Text.search(self, text, match_end, stopindex="end", forwards=True, exact=False, count=count)

    # Overloads
    def mark_set( self, name, index ):
        TextModel.mark_set( self,  name, index )
        if name == 'insert':
            self.set_currentLineTag()

    def insert(self, index, *args, **kword):
        TextModel.insert(self, index, *args, **kword)
        self.set_currentLineTag()
        if index == 'insert':
            self.see('insert')

    def delete(self, index1, index2, **kword):
        TextModel.delete(self, index1, index2, **kword)
        self.set_currentLineTag()

    def replace(self, index1, index2, text, **kword):
        TextModel.replace(self, index1, index2, text, **kword)
        self.set_currentLineTag()
