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
from devparrot.core.constraints import File, Integer
from devparrot.core.session import get_currentDocument
from pprint import pprint
import gc

def count():
    d = dict()
    for o in gc.get_objects():
        d[type(o).__name__] = d.get(type(o).__name__, 0)+1
    pprint(d)

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

    @SubCommand(
       ofile= File(mode=File.SAVE, default=lambda: "dump_info.txt")
    )
    def after_info(ofile):
        """set a config entry to value"""
        from devparrot.core import ui
        content = ui.window.tk.call("after", "info")
        #content = ui.window.after_info()
        with open(ofile, "w") as f:
            import pprint
            printer = pprint.PrettyPrinter(stream=f)
            printer.pprint(content)

    @SubCommand(
        #ofile = File(mode=File.SAVE, default=lambda: "backref.png"),
    )
    def back_ref():
        import objgraph
        gc.collect()
        #classtypes = ('TextView', 'Document', 'RangeInfo', 'SourceBuffer', 'FileDocSource', 'DocumentView')
        classtypes = ('TopContainer', 'Workspace', 'SplittedContainer', 'NotebookContainer', 'DocumentView')
        #i = 0
        #for o in objgraph.by_type(classtype):
        #    l = objgraph.find_backref_chain(o, objgraph.is_proper_module)
        #    objgraph.show_chain(l, filename="backref%d.png"%i)
        #    i += 1
        #print "test |%s|"% classtype
        #count()
        list_ = []
        for type_ in classtypes:
            list_.extend(objgraph.by_type(type_))
        #print list_
        objgraph.show_backrefs(list_, max_depth=3, too_many=100, filename="backref.png")
