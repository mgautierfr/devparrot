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
#    Copyright 2011-2015 Matthieu Gautier


from devparrot.core.completion import BaseCompletion, CompletionSystem
from devparrot.core import session
import Tkinter
import re

completionMap = {}

def init():
    session.completionSystem = TextCompletionSystem()
    session.eventSystem.connect('insert', on_insert)
    
def on_insert(model, index, text):
    completionSystem = session.completionSystem

    if completionSystem.displayed:
        return

    completionSystem.set_model(model)
    completionSystem.update_completion()

class TextCompletionSystem(CompletionSystem):
    def set_model(self, model):
        self.textWidget = model
        completionName = model.document.get_config('completionName')
        completionClass = completionMap.get(completionName, None)
        self.completor = completionClass(model)

    def get_completions(self):
        return self.completor.get_completions()

    def complete(self, completion):
        start = completion.start()
        self.textWidget.replace(start, 'insert', completion.name())


def uniqueFilter():
    mySet = set()
    def filter(value):
        if value in mySet:
            return False
        mySet.add(value)
        return True
    return filter

def infile_completions(currentWord, textWidget):
    all_text = textWidget.get("1.0", "end")
    words_iter = re.finditer(r"[%s]+"%session.config.get('wchars'), all_text)
    words = (m.group(0) for m in words_iter)
    unique = uniqueFilter()
    words = (w for w in words if unique(w))
    return (w for w in words if w!=currentWord and w.startswith(currentWord))

dictWords = None

def words_completions(currentWord, textWidget):
    global dictWords
    if dictWords is None:
        with open("/usr/share/dict/words", "r") as f:
            dictWords = list(w[:-1] for w in f.readlines())
    return (w for w in dictWords if w!=currentWord and w.startswith(currentWord))

class BaseCompletorMeta(type):
    def __new__(cls, name, bases, dct):
        if name == "BaseCompletor":
            return type.__new__(cls, name, bases, dct)
        else:
            _class = type.__new__(cls, name, bases, dct)
            completionMap[name] = _class
            return _class

class Completion(BaseCompletion):
    def __init__(self, startIndex, value, already):
        BaseCompletion.__init__(self, startIndex=startIndex)
        self.value = value
        self.already = already

    def name(self):
        return self.value

    def complete(self):
        return self.value[self.already:]

    def final(self):
        return True

class BaseCompletor(object):
    __metaclass__ = BaseCompletorMeta

class BasicTextCompletor(BaseCompletor):
    def __init__(self, model):
        self.textWidget = model
        self.sourcefunction = globals().get(self.textWidget.document.get_config('completion_functions'))

    def get_completions(self):
        separators = session.config.get('spacechars')+session.config.get('puncchars')+"\n"
        separators = separators.replace("\\", "\\\\")
        separators = separators.replace("]", "\\]")
        regex =  r"[%s]"%separators
        start_sep = Tkinter.Text.search(self.textWidget, regex, "insert", stopindex="1.0", regexp=True, backwards=True)
        if start_sep:
            start_index = self.textWidget.index("%s +1c"%start_sep)
        else:
            start_index = "1.0"

        currentWord = self.textWidget.get(str(start_index), "insert")
        if not currentWord:
            return ("", [])
        words = self.sourcefunction(currentWord, self.textWidget)
        completion = (Completion(start_index, w, len(currentWord)) for w in words)
        return ("", completion)

