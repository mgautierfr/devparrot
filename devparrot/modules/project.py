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

from devparrot.core import session, configLoader
from devparrot.core.modules import BaseModule

import os, os.path

def search_project_dir(path):
    path = os.path.abspath(path)
    dir_ = os.path.dirname(path)
    while dir_ != "/":
        if os.path.exists(os.path.join(dir_, ".devproject")):
            yield dir_
        dir_ = os.path.dirname(dir_)
    

class Project(BaseModule):
    def __init__(self, name):
        BaseModule.__init__(self, name)
        self.loaded = set()

    def on_pathAccess(self, path):
        for project_dir in search_project_dir(path):
            if project_dir in self.loaded:
                continue
            self.loaded.add(project_dir)
            if os.path.exists(os.path.join(project_dir, ".devproject", "configrc")):
                configParser = configLoader.ConfigParser(session.config)
                configParser.add_file(os.path.join(project_dir, ".devproject", "configrc"))
                configParser.parse(in_keys=os.path.normpath(project_dir).split(os.sep))

    
        
