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
import jedi

import Tkinter
import re

completionMap = {}

class TextCompletion(BaseModule):
    words = []
    @staticmethod
    def update_config(config):
        config.add_option("completion_functions", default="infile_completions")
        config.add_option("completionName", default="BasicCompletor")
        config._get("completionName").set("JediCompletor", keys=['Python'])

    def activate(self):
        with open("/usr/share/dict/words", "r") as f:
            TextCompletion.words = list(w[:-1] for w in f.readlines())
        bindings["<Control-space>"] = "completion start none\n"

    def deactivate(self):
        del bindings["<Control-space>"]

    def on_documentAdded(self, document):
        completionName = document.get_config('completionName')
        completionClass = completionMap.get(completionName, None)
        if not completionClass:
            return
        document.__completionSystem = completionClass(document)

    def on_insert(self, model, index, text):
        try:
            completionSystem = model.document.__completionSystem
            completionSystem.start_completion()
        except AttributeError:
            pass


class completion(MasterCommand):
    @SubCommand()
    def start(type):
        try:
            currentDocument = session.get_currentDocument()
            completionSystem = currentDocument.model.document.__completionSystem
            completionSystem.start_completion()
        except AttributeError:
            pass

class Completion(completion_.BaseCompletion):
    def __init__(self, startIndex, value, already):
        completion_.BaseCompletion.__init__(self, startIndex=startIndex)
        self.value = value
        self.already = already

    def name(self):
        return self.value

    def complete(self):
        return self.value[self.already:]

    def final(self):
        return True

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
    return filter

class BaseCompletionSystemMeta(type):
    def __new__(cls, name, bases, dct):
        if name == "BaseCompletionSystem":
            return type.__new__(cls, name, bases, dct)
        else:
            _class = type.__new__(cls, name, bases, dct)
            completionMap[name] = _class
            return _class

class BaseCompletionSystem(completion_.CompletionSystem):
    __metaclass__ = BaseCompletionSystemMeta

class BasicCompletor(BaseCompletionSystem):
    def __init__(self, document):
        BaseCompletionSystem.__init__(self, document.model, None)
        self.sourcefunction = globals().get(document.get_config('completion_functions'))

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
        unique = (Completion(start_index, w, len(currentWord)) for w in itertools.ifilter(uniqueFilter(), words))
        return ("", unique)

    def complete(self, completion):
        start = completion.start()
        self.textWidget.replace(start, 'insert', completion.name())

class JediCompletion(completion_.BaseCompletion):
    def __init__(self, jediCompletion, helpText, line, column):
        self.jediCompletion = jediCompletion
        self.helpText = helpText
        self.line = line
        self.col = column - (len(jediCompletion.name) - len(jediCompletion.complete))

    def start(self):
        return "%s.%s"%(self.line, self.col)

    def name(self):
        return self.jediCompletion.name

    def description(self):
        return "%s [%s] %s"%(self.jediCompletion.name, self.jediCompletion.description, "(%s)"%self.helpText if self.helpText else "")

    def complete(self):
        return self.jediCompletion.complete

    def final(self):
        return False

    def __repr__(self):
        return "<JediCompletion %s %s %s>"%(self.start(), self.name(), self.complete())


def comparator_key(comp):
    return (comp.in_builtin_module(), comp.name)

class JediCompletor(BaseCompletionSystem):
    def __init__(self, document):
        BaseCompletionSystem.__init__(self, document.model, None)
        self.document = document

    def get_completions(self):
        index = self.document.model.index("insert")

        script = jedi.api.Script(self.document.model.get_text(), line=index.line, column=index.col, path=self.document.get_path())
        create_completion = lambda j, t="": JediCompletion(j,t, line=index.line, column=index.col)
        call_signatures = script.call_signatures()
        if not call_signatures:
            char  = self.document.model.get("insert - 1c")
            if not char or not char in set(session.config.get('wchars')+"."):
                return ("", [])

            completions = sorted(script.completions(), key=comparator_key)
            return ("", (create_completion(completion) for completion in completions))
        else:
            call_signature = "%(name)s(%(args)s)"% {
               'name' : call_signatures[0].name,
               'args' : ",".join(p.name for p in call_signatures[0].params)
            }
            if call_signatures[0].index is None:
                return (call_signature, [])

            param_def = call_signatures[0].params[call_signatures[0].index]
            completions = sorted(script.completions(), key=comparator_key)
            return (call_signature, (create_completion(completion) for completion in completions))

    def complete(self, completion):
        start = completion.start()
        self.textWidget.replace(start, 'insert', completion.name())
