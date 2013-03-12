#    This file is part of DevParrot.
#
#    Author: Matthieu Gautier <matthieu.gautier@mgautier.fr>
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
#    Copyright 2011 Matthieu Gautier


import os

from devparrot.core.completion import Completion
from devparrot.core.command.commandCompleter import DoubleStringCompletion, SimpleStringCompletion
from devparrot.core.command.tokens import New


type_to_completion = {
    'DoubleString'   : DoubleStringCompletion,
    'SimpleString'   : SimpleStringCompletion,
    'UnquotedString' : Completion,
    'Identifier'     : Completion,
    'New'            : Completion
}

class noDefault(Exception):
    pass

class userCancel(Exception):
    pass

class _Constraint:
    def __init__(self, optional=False, multiple=False, default=None, askUser=False):
        self.optional = optional
        self.askUser = askUser
        if default is None:
            self.default = self._no_default
        else:
            self.default = default
        self.multiple = multiple
        self.isVararg = False

    def check_arg(self, args):
        if self.multiple:
            valids, args = zip(*[self.check(arg) for arg in args])
            valid = reduce(lambda x, y: x and y, valids)
            if not valid:
                return False, None
            return True, args
        else:
            return self.check(args)

    def _no_default(self):
        raise noDefault()

    def complete_context(self, context):
        if not self.multiple and context.get_type() == "List":
            return (None, [])

        if self.multiple and context.get_type() == 'New':
            return (None, [Completion("[", False)])

        if self.multiple:
            if context.get_type() != "List":
                return (None, [])
            if context.values:
                context = context.values[-1]
            else:
                context = New(index=context.index+1)

        if context.get_type() == "List":
            # more than one open context. can't handle it (for now?)
            return (None, [])

        return (context.index, self.complete(context))

    def check(self, token):
        return True, token
    
    def ask_user(self):
        raise userCancel()

    def complete(self, token):
        if token.get_type().endswith('String'):
            return [type_to_completion[token.get_type()](token.values, token.closed)]
        if token.get_type() == 'Identifier':
            return [Completion(token.name, False)]
        return []

class Stream(object):
    pass
    

class Default(_Constraint):
    def __init__(self, optional=False, multiple=False, default=None):
        _Constraint.__init__(self, optional, multiple, default)

class Keyword(_Constraint):
    def __init__(self, keywords, *args, **kwords):
        _Constraint.__init__(self, *args, **kwords)
        self.keywords = keywords
    
    def __str__(self):
        return "Keyword <%s>" % self.keywords
    
    def __repr__(self):
        return "<Constraint.Keyword %s>" % self.keywords

class Boolean(_Constraint):
    def __init__(self, *args, **kwords):
        _Constraint.__init__(self, *args, **kwords)

    def check(self, token):
        return True, bool(token)
            
class File(_Constraint):
    OPEN, SAVE, NEW = xrange(3)
    def __init__(self, mode=OPEN, optional=False, multiple=False, default=None):
        try:
            (x for x in mode)
        except TypeError:
            mode = (mode,)

        _Constraint.__init__(self, optional, multiple, default, askUser=True)
        self.mode = mode

    def check(self, _file):
        if os.path.exists(_file):
            return True, os.path.abspath(_file)
        d = os.path.dirname(_file)
        if not os.path.exists(d):
            return False, None
        return (File.SAVE in self.mode or File.NEW in self.mode), os.path.abspath(_file)

    def ask_user(self):
        from devparrot.core import session, ui
        path = None
        currentDoc = session.get_currentDocument()
        d = {}
        if currentDoc:
            path = currentDoc.get_path()
            if path:
                d['initialdir'] = os.path.dirname(path)

        if File.SAVE in self.mode:
            token = ui.helper.ask_filenameSave(**d)
        else:
            d['multiple'] = self.multiple or self.isVararg
            token = ui.helper.ask_filenameOpen(**d)
        if not token:
            raise userCancel()
        return token

    def _complete(self, directory, filestart, prefix, completionClass):
        completions = []
        for f in os.listdir(directory):
            if f.startswith(filestart):
                name = os.path.join(prefix, f)
                if os.path.isdir(os.path.join(directory, f)):
                    completion = completionClass(name+"/", False)
                else:
                    completion = completionClass(name, True)
                completions.append(completion)
        return completions

    def complete(self, token):
        completions = []
        value = ""
        if token.get_type() == 'Identifier':
            value = token.name

        if token.get_type().endswith('String'):
            value = token.values

        completionClass = type_to_completion[token.get_type()]

        currentFile = os.path.abspath(value)

        if value:
            if os.path.isdir(currentFile):
                completions.extend(self._complete(currentFile, "", value, completionClass))

            directory, file_ = os.path.split(currentFile)
            prefix, tail = os.path.split(value)
            if tail == "":
                #value ends with a '/'.
                prefix, tail = os.path.split(prefix)
        else:
            directory = os.getcwd()
            file_ = ""
            prefix = ""

        completions.extend(self._complete(directory, file_, prefix, completionClass))
        return completions


class Index(_Constraint):
    def __init__(self, *args, **kwords):
        _Constraint.__init__(self, *args, **kwords)

class Range(_Constraint):
    def __init__(self, *args, **kwords):
        _Constraint.__init__(self, *args, **kwords)
    
class Integer(_Constraint):
    def __init__(self, *args, **kwords):
        _Constraint.__init__(self, *args, **kwords)

    def check(self, arg):
        try:
            arg = int(arg)
            return True, arg
        except ValueError:
            return False, None

class OpenDocument(_Constraint):
    def __init__(self, *args, **kwords):
        _Constraint.__init__(self, *args, **kwords)

class ConfigEntry(_Constraint):
    def __init__(self):
        _Constraint.__init__(self)
        
    def check(self, arg):
        from devparrot.core import session
        sections = arg.split('.')
        currentSection = session.config
        for section in sections:
            try:
                currentSection = currentSection[section]
            except KeyError:
                return False, None
        return True, currentSection

    def complete(self, token):
        from devparrot.core import session
        completions = []
        
        if token.get_type().endswith('String'):
            token = token.value
        elif token.get_type() == 'Identifier':
            token = token.name
        else:
            token = ''

        sections = token.split('.')
        currentSection = session.config

        for section in sections[:-1]:
            try:
                currentSection = currentSection[section]
            except KeyError:
                return []

        prefix = ".".join(sections[:-1])
        token = sections[-1]

        prefix = ""
        if len(sections) > 1:
            prefix = ".".join(sections[:-1]+[""])

        completions.extend([Completion("%s%s."%(prefix, section), False) for section in currentSection.sections if section.startswith(token)])
        completions.extend([Completion("%s%s"%(prefix, var), True) for var in currentSection.variables if var.startswith(token)])
        return completions

