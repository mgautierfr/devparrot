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
from .constraintInstance import ConstraintInstance


from .constraintBase import _Constraint, type_to_completion
from devparrot.core.errors import UserCancel

class Stream:
    def __init__(self, help=""):
        self.help = help

    def get_help(self):
        return self.help
    

class Default(_Constraint):
    """No particular constraint"""
    def __init__(self, multiple=False, default=None, help=""):
        _Constraint.__init__(self, multiple=multiple, default=default, help=help)

class Keyword(_Constraint):
    """Must be a particular keyword"""
    def __init__(self, keywords, *args, **kwords):
        _Constraint.__init__(self, *args, **kwords)
        self.keywords = keywords

    def check(self, arg):
        return arg in self.keywords, arg

    check_direct = check

    def complete(self, token):
        if token.value is None:
            return []

        completionClass = type_to_completion[token.get_type()]
        create_completion = lambda v: completionClass(token.index, v, True, len(token.value))
        return [create_completion(k) for k in self.keywords if k.startswith(token.value)]

class Command(_Constraint):
    """Must be a command name"""
    def __init(self, *args, **kwords):
        _Constraint.__init__(self, *args, **kwords)

    def complete(self, token):
        import devparrot.core.session as session
        from devparrot.core.command.section import Section
        from devparrot.core.command.wrappers import MasterCommandWrapper

        if token.value is None:
            return []
        completionClass = type_to_completion[token.get_type()]
        try:
            masterCommand, subCommand = token.value.split(" ")
        except ValueError:
            masterCommand, subCommand  = token.value, None
        l = masterCommand.split('.')
        sections = l[:-1]
        name = l[-1]
        currentSection = session.commands
        try:
            for section in sections:
                currentSection = currentSection[section]
        except KeyError:
            return []
        create_completion = lambda v, f: completionClass(token.index, v, f, len(token.value))
        if subCommand is None:
            # Complete normal or master command
            return [create_completion(v="%s%s"%(currentSection.get_name(), "%s."%k if isinstance(i,Section) else k),
                                      f=(not isinstance(i,Section) and not isinstance(i, MasterCommandWrapper)))
                       for k,i in currentSection.items() if k.startswith(name)]
        else:
            try:
                command = currentSection[name]
            except KeyError:
                return []
            if not isinstance(command, MasterCommandWrapper):
                return []
            return [create_completion(v="%s%s"%(command.get_name(), k),
                                      f=True)
                       for k in command.subCommands if k.startswith(subCommand)]

    def check(self, token):
        from devparrot.core import session
        from devparrot.core.command.wrappers import MasterCommandWrapper
        try:
            masterCommand, subCommand = token.split()
        except ValueError:
            masterCommand, subCommand  = token, None
        l = masterCommand.split('.')
        sections = l[:-1]
        name = l[-1].strip()
        currentSection = session.commands
        try:
            for section in sections:
                currentSection = currentSection[section]
        except KeyError:
            return False, None
        if not subCommand:
            return name in currentSection, currentSection.get(name)
        else:
            try:
                command = currentSection[name]
            except KeyError:
                return False, None
            if not isinstance(command, MasterCommandWrapper):
                return False, None
            if subCommand in command.subCommands:
                return True, command.subCommands[subCommand]
            return False, None

    def check_direct(self, arg):
        from devparrot.core.command.wrappers import CommandWrapper
        return isinstance(arg, CommandWrapper), arg

booleanMap = {
'true' : True,
'on'   : True,
'1'    : True,
'yes'  : True,
'false': False,
'off'  : False,
'0'    : False,
'no'   : False
}

class Boolean(_Constraint):
    """Must be a boolean"""
    def __init__(self, *args, **kwords):
        _Constraint.__init__(self, *args, **kwords)

    def check(self, token):
        try:
            return True, booleanMap[token.lower()]
        except KeyError:
            return False, None

    @staticmethod
    def TRUE():
        return True

    @staticmethod
    def FALSE():
        return False
            
class File(_Constraint):
    """Must be a file path"""
    OPEN, SAVE, NEW, DIR = range(4)
    def __init__(self, mode=OPEN, multiple=False, default=None, help=""):
        try:
            (x for x in mode)
        except TypeError:
            mode = (mode,)

        _Constraint.__init__(self, multiple=multiple, default=default, askUser=True, help=help)
        self.mode = mode

    def check(self, _file):
        _file = os.path.abspath(os.path.expanduser(_file))
        if os.path.exists(_file):
            if File.DIR in self.mode:
                return os.path.isdir(_file), _file
            else:
                return os.path.isfile(_file), _file
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
            try:
                path = session.config.get('projectdir', keys=currentDoc.get_config_keys())
                if path:
                    d['initialdir'] = path
            except KeyError:
                #no projectdir variable (project module not active)
                path = currentDoc.get_path()
                if path:
                    d['initialdir'] = os.path.dirname(path)

        if File.DIR in self.mode:
            token = ui.helper.ask_directory(**d)
        elif File.SAVE in self.mode:
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
        value = token.value or ''

        completionClass = type_to_completion[token.get_type()]
        create_completion = lambda v,f : completionClass(token.index, v, f, len(value))

        currentFile = os.path.abspath(os.path.expanduser(value))

        if value:
            if os.path.isdir(currentFile):
                completions.extend(self._complete(currentFile, "", value, create_completion))

            directory, file_ = os.path.split(currentFile)
            prefix, tail = os.path.split(value)
            if tail == "":
                #value ends with a '/'.
                prefix, tail = os.path.split(prefix)
        else:
            directory = os.getcwd()
            file_ = ""
            prefix = ""

        completions.extend(self._complete(directory, file_, prefix, create_completion))
        return completions

class Directory(File):
    def __init__(self, multiple=False, default=None, help=""):
        File.__init__(self, mode=File.DIR, multiple=multiple, default=default, help=help)

    @staticmethod
    def ONE_OF(choice_list=['CURRENTPROJECT', 'CURRENTDOC', 'CURRENT']):
        def function():
            for choice in choice_list:
                if choice == 'CURRENTPROJECT':
                    try:
                        return Directory.CURRENTPROJECT()
                    except NoDefault:
                        pass
                if choice == 'CURRENTDOC':
                    try:
                        return Directory.CURRENTDOC()
                    except NoDefault:
                        pass
                if choice == 'CURRENT':
                    return os.getcwd()
            raise NoDefault()
        return function


    @staticmethod
    def CURRENT():
        return os.getcwd()

    @staticmethod
    def CURRENTDOC():
        document = session.get_currentDocument()
        path = currentDoc.get_path()
        if path:
            return os.path.dirname(path)
        raise NoDefault()

    @staticmethod
    def CURRENTPROJECT():
        from devparrot.core import session
        document = session.get_currentDocument()
        try:
            path = session.config.get('projectdir', keys=document.get_config_keys())
            if path:
                return path
        except KeyError:
            pass
        raise NoDefault()

def parse_range_index_text(text):
    from devparrot.core.session import get_documentManager, get_currentDocument
    from .index import parse_something
    splitted = text.split("@")
    if len(splitted) > 1:
        try:
            document = get_documentManager().get_file_from_title(splitted[0])
        except KeyError:
            try:
                document = get_documentManager().get_file(splitted[0])
            except KeyError:
                return False, None
        text = '@'.join(splitted[1:])
    else:
        document = get_currentDocument()

    model = document.model
    tags = set(model.tag_names())
    marks = set(model.mark_names())

    unresolved_idx = parse_something(text, marks, tags)
    idx = unresolved_idx.resolve(model)
    return document, idx

class Index(_Constraint):
    """Must be a index"""
    def __init__(self, *args, **kwords):
        _Constraint.__init__(self, *args, **kwords)

    def check(self, text):
        from .index import NoMatch
        try:
            document, idx = parse_range_index_text(text)
            return self.check_direct((document, idx))
        except NoMatch:
            return False, None

    @classmethod
    def check_direct(cls, arg):
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

    @staticmethod
    def DEFAULT(text):
        def _default():
            document, idx = parse_range_index_text(text)
            ok, result = Index.check_direct((document, idx))
            return result
        return _default

class Range(_Constraint):
    """Must be a range"""
    def __init__(self, *args, **kwords):
        _Constraint.__init__(self, *args, **kwords)

    def check(self, text):
        from .index import NoMatch
        try:
            document, idx = parse_range_index_text(text)
            return self.check_direct((document, idx))
        except NoMatch:
            return False, None

    @classmethod
    def check_direct(cls, arg):
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

    @staticmethod
    def DEFAULT(text):
        def _default():
            document, idx = parse_range_index_text(text)
            ok, result = Range.check_direct((document, idx))
            return result
        return _default
    
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
        if token.value is None:
            return []
        completionClass = type_to_completion[token.get_type()]
        create_completion = lambda v : completionClass(token.index, v, True, len(token.value))
        return [create_completion(d.get_title()) for d in documentManager.documents if d.get_title().startswith(token.value)]

    @staticmethod
    def CURRENT():
        from devparrot.core import session
        return session.get_currentDocument()

class ConfigEntry(_Constraint):
    """Must be a config entry"""
    def __init__(self, *args, **kwords):
        _Constraint.__init__(self, *args, **kwords)
        
    def check(self, arg):
        from devparrot.core import session
        try:
            return True, session.config.get_option(arg)
        except KeyError:
            return False, None

    def check_direct(self, arg):
        from devparrot.core.utils.config import Option
        return isinstance(arg, Option), arg

    def complete(self, token):
        from devparrot.core import session

        value = token.value or ''

        names = value.split('.')
        sections, name = names[:-1], names[-1]
        section = session.config
        for sectionName in sections:
            section = section._get(sectionName)

        completionClass = type_to_completion[token.get_type()]
        create_completion = lambda v : completionClass(token.index, v, True, len(value))
        completions = [create_completion(sectionName) for sectionName in section.options.keys() if sectionName.startswith(value)]

        return completions


class HelpEntry(_Constraint):
    """Must be a command name"""
    def __init(self, *args, **kwords):
        _Constraint.__init__(self, *args, **kwords)

    def complete(self, token):
        from devparrot.core import session
        from devparrot.core.help import HelpSection
        if token.value is None:
            return []
        completionClass = type_to_completion[token.get_type()]
        create_completion = lambda v,f : completionClass(token.index, v, f, len(token.value))
        return [create_completion(v=entry.get_name(), f=not isinstance(entry,HelpSection))
                       for name, entry in session.help_entries.items() if name.startswith(token.value)]

    def check(self, token):
        from devparrot.core import session
        if token == "devparrot":
            return True, session.help_entries
        sectionNames = token.split('.')
        section = session.help_entries
        while True:
            #We advance in help section as far as possible
            try:
                sectionName = sectionNames[0]
            except IndexError:
                # No more section to found, we have found it
                return True, section
            if sectionName == "devparrot":
                section = session.help_entries
            else:
                try:
                    section = section.entries[sectionName]
                except KeyError:
                    break
            sectionNames = sectionNames[1:]
        name = ".".join(sectionNames)
        try:
            return True, section.entries[name]
        except KeyError:
            return False, None

    def check_direct(self, arg):
        return hasattr(arg, "get_help"), arg

class ModuleEntry(_Constraint):
    """Must be a existing module name"""
    def __init(self, *args, **kwords):
        _Constraint.__init__(self, *args, **kwords)

    def complete(self, token):
        from devparrot.core import session
        from devparrot.core.help import HelpSection
        if token.value is None:
            return []
        completionClass = type_to_completion[token.get_type()]
        create_completion = lambda v : completionClass(token.index, v, True, len(token.value))
        return [create_completion(v=name) for name in session.modules if name.startswith(token.value)]

    def check(self, token):
        from devparrot.core import session
        try:
            return True, session.modules[token]
        except KeyError:
            return False, None

    def check_direct(self, arg):
        from devparrot.core.modules import BaseModule
        return isinstance(arg, BaseModule), arg
