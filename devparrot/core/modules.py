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


from devparrot.core import session
from devparrot.core.utils.event import auto_bind
import pkg_resources

def create_auto_call(module, attr):
    def auto_call(*args, **kwords):
        if module.active:
            return attr(*args, **kwords)
    return auto_call

class BaseModule:
    def __init__(self, name):
        self.name = name
        self.active = False
        auto_bind(self, session.eventSystem, wrapper=lambda attr:create_auto_call(self, attr))

    def activate(self):
        pass

    def _activate(self):
        if self.active:
            return
        ret = self.activate()
        self.active = True
        session.config.modules[self.name].activate.set(True)
        return ret

    def deactivate(self):
        pass

    def _deactivate(self):
        if not self.active:
            return
        ret = self.deactivate()
        self.active = False
        session.config.modules[self.name].activate.set(False)
        return ret

    @staticmethod
    def update_config(config, name):
        pass

def update_config(config):
    global_module_section = config.add_section('modules')
    for entrypoint in pkg_resources.iter_entry_points(group='devparrot.module'):
        module = entrypoint.load()
        module_section = global_module_section.add_section(entrypoint.name)
        module_section.add_option("activate", default=False)
        module.update_config(config, entrypoint.name)

def load():
    for entrypoint in pkg_resources.iter_entry_points(group='devparrot.module'):
        # get the module creator (class or fonction)
        name = entrypoint.name
        module = entrypoint.load()
        # create the associated config section
        # create the module instance
        session.modules[name] = module(name)

def activate_modules():
    for name, module in session.modules.items():
        if session.config.modules[name].activate.get():
            module._activate()
