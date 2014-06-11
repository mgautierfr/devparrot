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


import os

# import for other import
from constraintInstance import ConstraintInstance


from constraintBase import _Constraint, type_to_completion
from devparrot.core.completion import Completion
from devparrot.core.errors import UserCancel

class Stream(object):
    def __init__(self, help=""):
        self.help = help

    def get_help(self):
        return self.help
    

class Default(_Constraint):
    """No particular constraint"""
    def __init__(self, optional=False, multiple=False, default=None, help=""):
        _Constraint.__init__(self, optional=optional, multiple=multiple, default=default, help=help)

class Keyword(_Constraint):
    """Must be a particular keyword"""
    def __init__(self, keywords, *args, **kwords):
        _Constraint.__init__(self, *args, **kwords)
        self.keywords = keywords

    def check(self, arg):
        return arg in self.keywords, arg

    check_direct = check

    def complete(self, token):
        tokenValue = None
        if token.get_type().endswith('String'):
            tokenValue = token.values
        if token.get_type() == 'Identifier':
            tokenValue = token.name
        if token.get_type() == 'New':
            tokenValue = ""
        if tokenValue is None:
            return []
        return [Completion(k, True) for k in self.keywords if k.startswith(tokenValue)]

class Command(_Constraint):
    """Must be a command name"""
    def __init(self, *args, **kwords):
        _Constraint.__init__(self, *args, **kwords)

    def complete(self, token):
        import devparrot.core.session as session
        from devparrot.core.command.section import Section
        tokenValue = None
        if token.get_type().endswith('String'):
            tokenValue = token.values
        if token.get_type() == 'Identifier':
            tokenValue = token.name
        if token.get_type() == 'New':
            tokenValue = ""
        if tokenValue is None:
            return []
        l = tokenValue.split('.')
        sections = l[:-1]
        name = l[-1]
        currentSection = session.commands
        try:
            for section in sections:
                currentSection = currentSection[section]
        except KeyError:
            return []
        return [Completion(".".join(sections+([k, ""] if isinstance(i,Section) else [k])), not isinstance(i,Section)) for k,i in currentSection.items() if k.startswith(name)]

    def check(self, token):
        from devparrot.core import session
        l = token.split('.')
        sections = l[:-1]
        name = l[-1]
        currentSection = session.commands
        try:
            for section in sections:
                currentSection = currentSection[section]
        except KeyError:
            return False, None
        return name in currentSection, currentSection.get(name)

    def check_direct(self, arg):
        from devparrot.core.command.wrappers import CommandWrapper
        return isinstance(arg, CommandWrapper), arg

class Boolean(_Constraint):
    """Must be a boolean"""
    def __init__(self, *args, **kwords):
        _Constraint.__init__(self, *args, **kwords)

    def check(self, token):
        from ast import literal_eval
        return True, bool(literal_eval(token))
            
class File(_Constraint):
    """Must be a file path"""
    OPEN, SAVE, NEW = xrange(3)
    def __init__(self, mode=OPEN, optional=False, multiple=False, default=None, help=""):
        try:
            (x for x in mode)
        except TypeError:
            mode = (mode,)

        _Constraint.__init__(self, optional=optional, multiple=multiple, default=default, askUser=True, help=help)
        self.mode = mode

    def check(self, _file):
        _file = os.path.abspath(os.path.expanduser(_file))
        if os.path.exists(_file):
            return True, _file
        d = os.path.dirname(_file)
        if not os.path.exists(d):
            return False, None
        return (File.SAVE in self.mode or File.NEW in self.mode), _file

    check_direct = check

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
            raise UserCancel()
        return token

    def _complete(self, directory, filestart, prefix, completionClass):
        completions = []
        try:
            for f in os.listdir(directory):
                if f.startswith(filestart):
                    name = os.path.join(prefix, f)
                    if os.path.isdir(os.path.join(directory, f)):
                        completion = completionClass(name+"/", False)
                    else:
                        completion = completionClass(name, True)
                    completions.append(completion)
        except OSError:
            #directory is not an valid directory. Fail silently.
            pass
        return completions

    def complete(self, token):
        completions = []
        value = ""
        if token.get_type() == 'Identifier':
            value = token.name

        if token.get_type().endswith('String'):
            value = token.values

        completionClass = type_to_completion[token.get_type()]

        currentFile = os.path.abspath(os.path.expanduser(value))

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
    """Must be a index"""
    def __init__(self, *args, **kwords):
        _Constraint.__init__(self, *args, **kwords)

    def check(self, text):
        from devparrot.core.session import get_documentManager, get_currentDocument
        from index import parse_something, NoMatch
        splitted = text.split("@")
        if len(splitted) > 1:
            document = get_documentManager().get_file_from_title(splitted[0])
            text = '@'.join(splitted[1:])
        else:
            document = get_currentDocument()

        model = document.model
        tags = set(model.tag_names())
        marks = set(model.mark_names())

        try:
            unresolved_idx = parse_something(text, marks, tags)
            idx = unresolved_idx.resolve(model)
            return self.check_direct((document, idx))
        except NoMatch:
            return False, None

    def check_direct(self, arg):
        from devparrot.core.utils.posrange import Range, Index
        from devparrot.core.document import Document
        try:
            doc, stuff = arg
            if not isinstance(doc, Document):
                return False, None
            if  isinstance(stuff, Range):
                return True, (doc, stuff[0])
            if isinstance(stuff, Index):
                return True, (doc, stuff)
            return False, None
        except TypeError:
            return False, None

class Range(_Constraint):
    """Must be a range"""
    def __init__(self, *args, **kwords):
        _Constraint.__init__(self, *args, **kwords)

    def check(self, text):
        from devparrot.core.session import get_documentManager, get_currentDocument
        from index import parse_something, NoMatch
        splitted = text.split("@")
        if len(splitted) > 1:
            document = get_documentManager().get_file_from_title(splitted[0])
            text = '@'.join(splitted[1:])
        else:
            document = get_currentDocument()

        model = document.model
        tags = set(model.tag_names())
        marks = set(model.mark_names())

        try:
            unresolved_idx = parse_something(text, marks, tags)
            idx = unresolved_idx.resolve(model)
            return self.check_direct((document, idx))
        except NoMatch:
            return False, None

    def check_direct(self, arg):
        from devparrot.core.utils.posrange import Range, Index
        from devparrot.core.document import Document
        try:
            doc, stuff = arg
            if not isinstance(doc, Document):
                return False, None
            if  isinstance(stuff, Range):
                return True, (doc, stuff)
            if isinstance(stuff, Index):
                return True, (doc, Range(stuff, stuff))
            return False, None
        except TypeError:
            return False, None
    
class Integer(_Constraint):
    """Must be a integer"""
    def __init__(self, *args, **kwords):
        _Constraint.__init__(self, *args, **kwords)

    def check(self, arg):
        try:
            arg = int(arg)
            return True, arg
        except ValueError:
            return False, None

    def check_direct(self, arg):
        return isinstance(arg,int) , arg

class OpenDocument(_Constraint):
    """Must be a open document"""
    def __init__(self, *args, **kwords):
        _Constraint.__init__(self, *args, **kwords)

    def check(self, token):
        from devparrot.core import session
        try:
            return True, session.get_documentManager().get_file_from_title(token)
        except KeyError:
            return False, None

    def check_direct(self, arg):
        from devparrot.core.document import Document
        return isinstance(arg,Document) , arg

    def complete(self, token):
        from devparrot.core import session
        documentManager = session.get_documentManager()
        tokenValue = None
        if token.get_type().endswith('String'):
            tokenValue = token.values
        if token.get_type() == 'Identifier':
            tokenValue = token.name
        if token.get_type() == 'New':
            tokenValue = ""
        if tokenValue is None:
            return []
        return [Completion(d.get_title(), True) for d in documentManager.documents if d.get_title().startswith(tokenValue)]

class ConfigEntry(_Constraint):
    """Must be a config entry"""
    def __init__(self, *args, **kwords):
        _Constraint.__init__(self, *args, **kwords)
        
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

    def check_direct(self, arg):
        from devparrot.core.configLoader import Section
        return isinstance(arg,Section) , arg

    def complete(self, token):
        from devparrot.core import session
        completions = []
        
        if token.get_type().endswith('String'):
            token = token.values
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

