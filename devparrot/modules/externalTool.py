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

import tkinter, tkinter.ttk
from devparrot.core.command import Command, Alias
from devparrot.core.constraints import Stream

from devparrot.core import ui, session
from devparrot.core.modules import BaseModule

import re, os.path


tagParsing = [re.compile(br"(error|erreur|note|warning|attention)")]
fileParsing = [re.compile(br"(^|(.* ))(?P<file>[^: ]+):(?P<line>[0-9]+):(?P<pos>[0-9]+)?"),  # gcc output
               re.compile(br'File (?P<file_link>"(?P<file>.*)", line (?P<line>[0-9]+))') # pythen exception
              ]

class ExternalTool(BaseModule):
    @staticmethod
    def update_config(config):
        config.add_option("command", default="make")

class CommandOutput(tkinter.ttk.Frame):
    def __init__(self, parent):
        tkinter.ttk.Frame.__init__(self, parent)
        self.vScrollbar = tkinter.ttk.Scrollbar(self, orient=tkinter.VERTICAL)
        self.vScrollbar.grid(column=1, row=0, sticky="nsew")
        self.textView = tkinter.Text(self)
        self.textView.grid(column=0, row=0, sticky="nsew")
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.rowconfigure(0, weight=1)

        self.vScrollbar['command'] = self.textView.yview
        self.textView['yscrollcommand'] = self.vScrollbar.set

        bindtags = list(self.textView.bindtags())
        bindtags.insert(1,"devparrot")
        bindtags = " ".join(bindtags)
        self.textView.bindtags(bindtags)

        self.textView.tag_configure("error", foreground="red")
        self.textView.tag_configure("warning", foreground="purple")
        self.textView.tag_configure("note", foreground="blue")
        self.textView.configure(state="disable")

        self.set_normal_cursor()

    def set_hand_cursor(self):
        self.textView.configure(cursor="hand2")

    def set_normal_cursor(self):
        self.textView.configure(cursor="")

    def insert_line(self, line):
        index = self.textView.index('end - 1c')
        self.textView.configure(state="normal")
        self.textView.insert('end', line)
        self.textView.configure(state="disable")

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
        except (IndexError, TypeError):
            pass
        def goto(event):
            command = 'open "{file}"\n goto {file}@{line}.{pos}'.format(file=os.path.abspath(fileMatch.group('file')).decode(),
                                                                        line=fileMatch.group('line').decode(),
                                                                        pos=pos)
            session.commandLauncher.run_command_nofail(command)

        tagName = "tag_{file}_{line}_{pos}".format(file=fileMatch.group('file'), line=fileMatch.group('line'), pos=pos)
        self.textView.tag_configure(tagName, foreground="blue", underline=True)
        self.textView.tag_bind(tagName, "<Enter>", lambda e:self.set_hand_cursor())
        self.textView.tag_bind(tagName, "<Leave>", lambda e:self.set_normal_cursor())
        self.textView.tag_bind(tagName, "<1>", goto)

        start = fileMatch.start('file')
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
            line = next(content)
            while line is not None:
                output.insert_line(line)
                line = next(content)
            output.after(100, read_line)
        except StopIteration:
            pass

    output.after(100, read_line)


@Alias()
def runtool():
    document = session.get_currentDocument()
    command = session.config.get("command", document.get_config_keys())
    return "shell {0!r}  | commandOutput {0!r}".format(command)


