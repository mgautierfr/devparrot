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


class Section(dict):
    def __init__(self, name, parentSection=None):
        self.name = name
        self.parentSection = parentSection
        
    def __getattr__(self, commandName):
        return self[commandName]

    def add_command(self, name, wrapper):
        self[name] = wrapper

    def __str__(self):
        if not self.name:
            return ""
        if not self.parentSection:
            return "%s."%self.name
        return "%s%s."%(self.parentSection, self.name)

    def get_constraint(self, *args):
        raise IndexError
    
