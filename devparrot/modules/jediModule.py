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


from devparrot.core.modules import BaseModule
from devparrot.core.textCompletion import BaseCompletor, BaseCompletion
from devparrot.core import session
from jedi import settings as JediSettings
from jedi.api import Script, defined_names
from tagExplorer import BaseProvider, BaseTag

class Jedi(BaseModule):
    def activate(self):
        session.config.get_option("completionName").set("JediCompletor", keys=['Python'])
        session.config.get_option("tagProvider").set("JediTagProvider", keys=['Python'])

    def deactivate(self):
        session.config.get_option("completionName").remove(keys=['Python'])
        session.config.get_option("tagProvider").remove(keys=['Python'])

class JediCompletion(BaseCompletion):
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

JediSettings.add_bracket_after_function=True

class JediCompletor(BaseCompletor):
    def __init__(self, model):
        self.model = model

    def get_completions(self):
        index = self.model.index("insert")

        script = Script(self.model.get_text(), line=index.line, column=index.col, path=self.model.document.get_path())
        create_completion = lambda j, t="": JediCompletion(j,t, line=index.line, column=index.col)
        try:
            call_signatures = script.call_signatures()
        except SyntaxError:
            return ("", [])
        if not call_signatures:
            char  = self.model.get("insert - 1c")
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
            char  = self.model.get("insert - 1c")
            if not char or not char in set(session.config.get('wchars')+"."):
                return (call_signature, [])

            param_def = call_signatures[0].params[call_signatures[0].index]
            completions = sorted(script.completions(), key=comparator_key)
            return (call_signature, (create_completion(completion) for completion in completions))

innerJediType2devp = {
'function' : 'method',
'statement': 'member'
}
class JediTag(object):
    def __init__(self, jediDefinition, overtype=None):
        self.jediDefinition = jediDefinition
        self.overtype = overtype

    @property
    def position(self):
        return "%d.%d"%(self.jediDefinition.line, self.jediDefinition.column)

    @property
    def name(self):
        return self.jediDefinition.name

    @property
    def type(self):
        if self.overtype:
            return self.overtype
        return self.jediDefinition.type

    @property
    def children(self):
        return [JediTag(n, innerJediType2devp.get(n.type)) for n in self.jediDefinition.defined_names()]

globalJediType2devp = {
'statement': 'variable'
}
class JediTagProvider(BaseProvider):
    def __init__(self, model):
        self.model = model

    def get_tag(self):
        return (JediTag(n, globalJediType2devp.get(n.type)) for n in defined_names(self.model.get_text()))
