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

import Tkinter, ttk
from devparrot.core.command import Command, Alias
from devparrot.core.constraints import Stream

from devparrot.core import ui, session

import re


tagParsing = [re.compile(r"(error|erreur|note|warning|attention)")]
fileParsing = [re.compile(r"(?P<file>[^:]+):(?P<line>[0-9]+):(?P<pos>[0-9]+)"),  # gcc output
               re.compile(r'File (?P<file_link>"(?P<file>.*)", line (?P<line>[0-9]+))') # pythen exception
              ]

configSection = None

def init(_configSection, name):
    global configSection
    configSection = _configSection
    configSection.add_variable("command", "make")
    configSection.active.register(activate)

def activate(var, old):
    if var.get():
        pass

class CommandOutput(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self.vScrollbar = ttk.Scrollbar(self, orient=ttk.Tkinter.VERTICAL)
        self.vScrollbar.grid(column=1, row=0, sticky="nsew")
        self.textView = Tkinter.Text(self)
        self.textView.grid(column=0, row=0, sticky="nsew")
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.rowconfigure(0, weight=1)

        self.vScrollbar['command'] = self.textView.yview
        self.textView['yscrollcommand'] = self.vScrollbar.set

        bindtags = list(self.textView.bindtags())
        bindtags.insert(1,"Command")
        bindtags = " ".join(bindtags)
        self.textView.bindtags(bindtags)

        self.textView.tag_configure("error", foreground="red")
        self.textView.tag_configure("warning", foreground="purple")
        self.textView.tag_configure("note", foreground="blue")

    def insert_line(self, line):
        index = self.textView.index('insert')
        self.textView.insert('insert', line)

        fileMatch = None
        for reg in fileParsing:
            fileMatch = reg.search(line)
            if fileMatch:
                break

        if not fileMatch:
            return


        pos = 0
        try:
            pos = int(fileMatch.group('pos')) - 1
        except IndexError:
            pass
        def goto(event):
            session.commandLauncher.run_command_nofail('open "{file}"\n goto {line}.{pos}'.format(file=fileMatch.group('file'), line=fileMatch.group('line'), pos=pos))

        tagName = "tag_{file}_{line}_{pos}".format(file=fileMatch.group('file'), line=fileMatch.group('line'), pos=pos)
        self.textView.tag_configure(tagName, foreground="blue", underline=True)
        self.textView.tag_bind(tagName, "<1>", goto)

        start = fileMatch.start()
        end   = fileMatch.end()
        self.textView.tag_add(tagName, "{} linestart + {} c".format(index, start), "{} linestart + {} c".format(index, end))

        tagMatch = None
        for reg in tagParsing:
            tagMatch = reg.search(line)
            if tagMatch:
                break

        if tagMatch:
            tag_str = tagMatch.group()
            if tag_str in ('error', 'erreur'):
                tag = 'error'
            elif tag_str in ('note', ):
                tag = 'note'
            elif tag_str in ('warning', 'attention'):
                tag = 'warning'
            self.textView.tag_add(tag, "{} linestart + {} c".format(index, tagMatch.start()), "{} linestart + {} c".format(index, tagMatch.end()))

        self.textView.see('insert')

@Command(content=Stream())
def commandOutput(name, content):
    output = CommandOutput(ui.window)

    def on_delete():
        ui.helperManager.remove_helper(output, 'bottom')
        output.destroy()
    ui.helperManager.add_helper(output, name, 'bottom', True, on_delete)


    def read_line():
        try:
            line = content.next()
            while line is not None:
                output.insert_line(line)
                line = content.next()
            output.after(100, read_line)
        except StopIteration:
            pass

    output.after(100, read_line)


@Alias()
def runtool():
    return "shell {command}  | commandOutput {command}".format(command=configSection.get('command'))
