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


import utils.event
from devparrot.core.errors import InvalidName, UserCancel


def add_command(name, command, parentSection=None):
    import session
    if parentSection is None:
        session.commands.add_command(name, command)
    else:
        parentSection.add_command(name, command)


def create_section(name=None, parentSection=None):
    from devparrot.core.command.section import Section
    import session
    if name is None:
        session.commands = Section(None, None)
        return session.commands
    else:
        if parentSection is None:
            return session.commands.setdefault(name, Section(name))
        else:
            return parentSection.setdefault(name,Section(name, parentSection))


class ListGenerator:
    def __init__(self, l):
        self.l = l
        self.index = 0
        self.bend = (len(l) == 0)
    
    def next(self):
        if self.index >= len(self.l):
            self.bend = True
            return None
        self.index += 1
        return self.l[self.index-1]
    
    def back(self):
        self.index = max(0, self.index-1)
    
    def end(self):
        return self.index >= len(self.l)

class History(object):
    def __init__(self):
        self.history = list()
        self.currentIndex = 0

    def push(self, line):
        self.history.append(line)
        self.currentIndex = 0

    def get_previous(self):
        if self.currentIndex < len(self.history):
            self.currentIndex += 1
        if self.currentIndex == 0:
            return ""
        return self.history[-self.currentIndex]

    def get_next(self):
        if self.currentIndex != 0:
            self.currentIndex -= 1
        if self.currentIndex == 0:
            return ""
        return self.history[-self.currentIndex]

def expand_alias(commands, first=False):
    from devparrot.core import session
    from devparrot.core.errors import InvalidArgument
    from devparrot.core.command.parserGrammar import parse_input_text
    from devparrot.core.command.wrappers import AliasWrapper
    for command in commands:
        if command == "\n":
            yield command
            continue

        l = command.name.split('.')
        sections, commandName = l[:-1], l[-1]
        lastSection = session.commands
        for section in sections:
            lastSection = lastSection[section]
        aliases = dict([(key, alias) for key, alias in lastSection.items() if isinstance(alias, AliasWrapper)])
        if commandName in aliases:
            #it is an alias, lets expand it
            #command with rewrite with all the section
            try:
                alias_expansion = eval(command.rewrited(), dict(session.commands), {})
            except TypeError as err:
                raise InvalidArgument(err.message)
            #parse new text and redo the work for it
            pipe = parse_input_text(alias_expansion, forCompletion=False)
            for com in expand_alias(pipe.values):
                yield com
        else:
            #it is a command, just yield it
            yield command
    if first:
        yield "\n"

class CommandLauncher:
    def __init__(self):
        self.history = History()

    def run_command(self, text):
        from devparrot.core import session
        from devparrot.core.command.parserGrammar import parse_input_text
        from devparrot.core.command.stream import PseudoStream, DefaultStreamEater
        session.logger.debug("running command %s", repr(text))
        pipe = parse_input_text(text, forCompletion=False)
        commands = expand_alias(pipe.values, True)

        while True:
            try:
                stream = PseudoStream()
                while True:
                    command = commands.next()
                    if command == "\n":
                        DefaultStreamEater(stream)
                        break # one pipe, start a new line (pipe)
                    l = command.name.split('.')
                    sections, commandName = l[:-1], l[-1]
                    try:
                        lastSection = session.commands
                        for section in sections:
                                    lastSection = lastSection[section]
                    except KeyError:
                         raise InvalidName("{0} is not a valid command name".format(command.name))
                    try:
                        streamEater = eval(command.rewrited(), dict(session.commands), {})
                        stream = streamEater(stream)
                    except UserCancel:
                        raise StopIteration

            except StopIteration:
                break # cause no more command at all
        self.history.push(text)

    def run_command_nofail(self, text):
        from devparrot.core import session
        from devparrot.core.errors import ContextError, InvalidError
        try:
            self.run_command(text)
            session.userLogger.info(text)
        except ContextError as err:
            session.userLogger.error(err)
        except InvalidError as err:
            session.userLogger.invalid(err)
        except Exception as err:
            session.logger.exception(err)
