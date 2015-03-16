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

class HelpSection:
    def __init__(self, section, name, header=None):
        self.section = section
        self.name = name
        if header is None:
            self.header = "%s Section"%name
        else:
            self.header = header
        self.entries = {}

    def __str__(self):
        return "<Section %s>"%self.name

    def add_entry(self, name, entry):
        self.entries[name] = entry

    def get_helpName(self):
        if self.section:
            return "%s.%s"%(self.section.get_helpName(), self.name)
        else:
            return "%s"%self.name

    def get_help(self):
        yield self.header+"\n"
        yield "="*len(self.header)+"\n"
        yield "\n"

        yield "helpEntries:\n"
        yield "------------\n"
        yield "\n"    

        for entry in sorted(self.entries):
            yield [(None, " - "), ("autocmd.help '%s'"%self.entries[entry].get_helpName(), entry), (None, "\n")]

def add_helpEntry(name, obj, in_=[]):
    from devparrot.core import session
    section = session.help_entries
    for sectionName in in_:
        if not sectionName:
            continue
        try:
            section = section.entries[sectionName]
        except KeyError:
            if section is session.help_entries:
                newSection = HelpSection(None, sectionName)
            else:
                newSection = HelpSection(section, sectionName)
            section.add_entry(sectionName, newSection)
            section = newSection
    section.add_entry(name, obj)

def help_entry(name, in_=[]):
    def add_to_entries(obj):
        add_helpEntry(name, obj, in_)
        return obj
    return add_to_entries

