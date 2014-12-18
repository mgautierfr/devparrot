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

class HelpSection(object):
    def __init__(self, name):
        self.name = name
        self.entries = {}

    def add_entry(self, name, entry):
        self.entries[name] = entry

    def get_name(self):
        return self.name

    def get_help(self):
        last = "%s Section"%self.name
        yield last+"\n"
        yield "="*len(last)+"\n"
        yield "\n"

        yield "helpEntries:\n"
        yield "------------\n"
        yield "\n"    

        for entry in self.entries:
            yield [(None, " - "), ("autocmd.help %s"%entry, entry), (None, "\n")]

class DevparrotHelp(object):
    def get_name(self):
        return "devparrot"

    def get_help(self):
        from devparrot.core import session
        from devparrot.core.command.section import Section
        from devparrot.core.command import wrappers
        yield "Devparrot help\n"
        yield "==============\n"
        yield "\n"
        
        yield "helpEntries:\n"
        yield "------------\n"
        yield "\n"

        for entry in session.help_entries:
            yield [(None, " - "), ("autocmd.help %s"%entry, entry), (None, "\n")]

def add_helpEntry(name, obj, in_=[]):
    from devparrot.core import session
    session.help_entries[name] = obj
    for sectionName in in_:
        if not sectionName:
            continue
        try:
            section = session.help_entries[sectionName]
        except KeyError:
            section = HelpSection(sectionName)
            session.help_entries[sectionName] = section
        section.add_entry(name, obj)

def help_entry(name, in_=[]):
    def add_to_entries(obj):
        add_helpEntry(name, obj)
        return obj
    return add_to_entries

