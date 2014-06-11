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
from devparrot.core.constraints import File
from devparrot.core.session import get_currentDocument

class debug(MasterCommand):

    @SubCommand(
       ofile= File(mode=File.SAVE, default=lambda: "dump.txt")
    )
    def dump_buffer(ofile):
        """set a config entry to value"""
        content = get_currentDocument().model.dump("1.0", "end", all=True)
        with open(ofile, "w") as f:
            import pprint
            printer = pprint.PrettyPrinter(stream=f)
            printer.pprint(content)
