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


from devparrot.core import completion as completion_
from devparrot.core.modules import BaseModule
from devparrot.core.command import MasterCommand, SubCommand
from devparrot.core.session import bindings
from devparrot.core import session
import itertools

import Tkinter
import re

class TextCompletion(BaseModule):
    words = []
    @staticmethod
    def update_config(config):
        config.add_option("completion_functions", default=infile_completions)

    def activate(self):
        with open("/usr/share/dict/words", "r") as f:
            TextCompletion.words = list(w[:-1] for w in f.readlines())
        bindings["<Control-space>"] = "completion start none\n"

    def deactivate(self):
        del bindings["<Control-space>"]


class completion(MasterCommand):
    @SubCommand()
    def start(type):
        currentDocument = session.get_currentDocument()
        completionSystem = BasicCompletionSystem(currentDocument.model, currentDocument.get_config('completion_functions'))
        completionSystem.start_completion()

class Completion(object):
    def __init__(self, value):
        self.value = value
        self.final = True

    def __str__(self):
        return self.value

def infile_completions(currentWord, textWidget):
    all_text = textWidget.get("1.0", "end")
    words_iter = re.finditer(r"[%s]+"%session.config.get('wchars'), all_text)
    words = (m.group(0) for m in words_iter)
    return (w for w in words if w!=currentWord and w.startswith(currentWord))

def words_completions(currentWord, textWidget):
    return (w for w in TextCompletion.words if w!=currentWord and w.startswith(currentWord))

def uniqueFilter():
    mySet = set()
    def filter(value):
        if value in mySet:
            return False
        mySet.add(value)
        return True

class BasicCompletionSystem(completion_.CompletionSystem):
    def __init__(self, textWidget, sourcefunction):
        completion_.CompletionSystem.__init__(self, textWidget, None)
        self.sourcefunction = sourcefunction

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
        words = self.sourcefunction(currentWord, self.textWidget)
        unique = (Completion(w) for w in itertools.ifilter(uniqueFilter(), words))
        return str(start_index), [Completion(currentWord)]+list(itertools.islice(unique,10))

    def complete(self, startIndex, text):
        oldInsert = self.textWidget.index("insert")
        self.textWidget.tk.call((self.textWidget._w, 'replace', startIndex, 'insert', text))

