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

from devparrot.core.command import MasterCommand, SubCommand
from devparrot.core import session
from devparrot.core.constraints import Default, ModuleEntry
import importlib

class module(MasterCommand):
    @SubCommand(module=ModuleEntry())
    def activate(module):
        """activate a module"""
        module._activate()

    @SubCommand(module=ModuleEntry())
    def deactivate(module):
        """deactivate a module"""
        module._deactivate()

    @SubCommand(
    name       = Default(help="The name to use for the devparrot module"),
    modulePath = Default(help="""The python module path.
This must follow the same syntax than setuptools entrypoint
aka : PathToModule:ObjectEntryPoint"""),
    )
    def load(name, modulePath):
        """load a python module/package as a devparrot module"""
        modulePath, creatorName = modulePath.split(':')
        loader =importlib.machinery.SourceFileLoader(name, modulePath)
        try:
            module = loader.load_module()
        except ImportError:
            raise InvalidArgument("%r is not a valid module path"%modulePath)
        module_section = session.config.modules.add_section(name)
        module_section.add_option("activate", default=False)
        creator = getattr(module, creatorName)
        creator.update_config(session.config)
        session.modules[name] = creator(name)

