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
#    Copyright 2011-2014 Matthieu Gautier


from devparrot.core import session, completion
from devparrot.core.modules import BaseModule

import Tkinter
import re

class TextCompletion(BaseModule):
    @staticmethod
    def update_config(config):
        pass

    def on_documentAdded(self, document):
        document.model._completion = BasicCompletionSystem(document.model)

class Completion(object):
    def __init__(self, value):
        self.value = value
        self.final = True

    def __str__(self):
        return self.value

class BasicCompletionSystem(completion.CompletionSystem):
    def __init__(self, textWidget):
        completion.CompletionSystem.__init__(self, textWidget)

    def get_completions(self):
        separators = session.config.get('spacechars')+session.config.get('puncchars')+"\n"
        separators = separators.replace("\\", "\\\\")
        separators = separators.replace("]", "\\]")
        regex =  r"[%s]"%separators
        start_sep = Tkinter.Text.search(self.textWidget, regex, "insert", stopindex="1.0", regexp=True, backwards=True)
        if not start_sep:
            start_sep = "1.0"
        start_index = self.textWidget.index("%s +1c"%start_sep)
        currentWord = self.textWidget.get(str(start_index), "insert")
        if not currentWord:
            return None, []
        all_text = self.textWidget.get("1.0", "end")
        words_iter = re.finditer(r"[%s]+"%session.config.get('wchars'), all_text)
        words = (m.group(0) for m in words_iter)
        words_starting = (w for w in words if w!=currentWord and w.startswith(currentWord))
        words_completion = [Completion(w) for w in set(words_starting)]
        return str(start_index), words_completion

    def complete(self, startIndex, text):
        oldInsert = self.textWidget.index("insert")
        self.textWidget.tk.call((self.textWidget._w, 'replace', startIndex, 'insert', text))

