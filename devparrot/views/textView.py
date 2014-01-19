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
import ttk, Tkinter

class TextView():
    def __init__(self, document):
        self.uiContainer = ttk.Frame(session.get_globalContainer())
        self.hScrollbar = ttk.Scrollbar(session.get_globalContainer(),
                                        orient=ttk.Tkinter.HORIZONTAL)
        self.hScrollbar.grid(column=0,
                             row=1,
                             columnspan=10,
                             in_=self.uiContainer,
                             sticky="nsew"
                            )
        self.hScrollbar.grid_remove()

        self.vScrollbar = ttk.Scrollbar(session.get_globalContainer(),
                                        orient=ttk.Tkinter.VERTICAL)
        self.vScrollbar.grid(column=10,
                             row=0,
                             in_=self.uiContainer,
                             sticky="nsew")
        self.vScrollbar.grid_remove()

        self.lineNumbers = ttk.Tkinter.Canvas(session.get_globalContainer(),
                                              highlightthickness = 0,
                                              takefocus = 0,
                                              bd=0,
                                              background = 'lightgrey',
                                              state='disable')
        self.lineNumbers.grid(column=0,
                              row=0,
                              in_=self.uiContainer,
                              sticky="nsw")

        self.uiContainer.columnconfigure(0, weight=0)
        self.uiContainer.columnconfigure(1, weight=1)
        self.uiContainer.columnconfigure(10, weight=0)
        self.uiContainer.rowconfigure(0, weight=1)
        self.uiContainer.rowconfigure(1, weight=0)
        
        self.vScrollbar['command'] = self.proxy_yview

        self.document = document
        self.view = None
        
        self.firstLine = 1
        self.lastLine = 1
        self.lastLineCreated = 0
        self.actualLineNumberWidth = 0

    def focus(self):
        return self.view.focus()

    def proxy_yview(self, *args, **kwords):
        if self.view:
            self.view.yview(*args, **kwords)
            self.set_lineNumbers()

    def proxy_yscrollcommand(self, *args, **kwords):
        if args == ('0.0' , '1.0'):
            self.vScrollbar.grid_remove()
        else:
            self.vScrollbar.grid_configure()
        self.vScrollbar.set(*args, **kwords)
        self.set_lineNumbers()

    def proxy_xscrollcommand(self, *args, **kwords):
        if args == ('0.0' , '1.0'):
            self.hScrollbar.grid_remove()
        else:
            self.hScrollbar.grid_configure()
        self.hScrollbar.set(*args, **kwords)

    def _create_textLine(self, name):
        self.lineNumbers.create_text("0", "0",
                                     anchor="nw",
                                     text=name,
                                     tags=name,
                                     state="hidden")


    def set_lineNumbers(self):
        self.lineNumbers.config(state='normal')

        nbLine = int(self.view.index('end').split('.')[0])
        if self.lastLineCreated < nbLine:
            map(self._create_textLine, [str(i+1) for i in range(self.lastLineCreated, nbLine)])
            self.lastLineCreated = nbLine
        
        firstLine = int(self.view.index('@0,0').split('.')[0])-1
        lastIndex = self.view.index('@0,{}'.format(self.view.winfo_height()))
        lastLine = int(lastIndex.split('.')[0])+1
        
        firstLine = max(firstLine, 1)
        lastLine = min(lastLine, nbLine)

        for i in range( min(firstLine, self.firstLine) , max(lastLine, self.lastLine)+1 ):
            name = str(i)
            pos = self.view.bbox("{}.0".format(i))
            if pos:
                self.lineNumbers.coords(name, "0", str(pos[1]))
                self.lineNumbers.itemconfig(name, state="disable")
            else:
                self.lineNumbers.itemconfig(name, state="hidden")

        self.firstLine = firstLine
        self.lastLine = lastLine

        bbox = self.lineNumbers.bbox('all')
        if bbox:
            w = int(bbox[2])
            if self.actualLineNumberWidth < w:
                self.actualLineNumberWidth = w
                self.lineNumbers.config(width=self.actualLineNumberWidth)

        self.lineNumbers.config(state='disable')
    
    def on_event_lineChanged(self, *args):
        self.set_lineNumbers()


    def set_model(self, model):
        self.view = model
        self.view['yscrollcommand'] = self.proxy_yscrollcommand
        self.view['xscrollcommand'] = self.proxy_xscrollcommand
        self.hScrollbar['command'] = self.view.xview
        self.view.grid(column=1, row=0, in_=self.uiContainer, sticky=(ttk.Tkinter.N, ttk.Tkinter.S, ttk.Tkinter.E, ttk.Tkinter.W))
        self.view.lift(self.uiContainer)
        self.view.connect('insert', self.on_event_lineChanged)
        self.view.connect('delete', self.on_event_lineChanged)

    def lift(self, above):
        self.uiContainer.lift(above)
        self.vScrollbar.lift(self.uiContainer)
        self.hScrollbar.lift(self.uiContainer)
        ttk.Tkinter.Misc.lift(self.lineNumbers, aboveThis=self.uiContainer)
        self.view.lift(self.uiContainer)
    
    def get_context(self):
        had = self.view.get_hadjustment()
        vad = self.view.get_vadjustment()
        hadjustment = (had.value-had.lower)/(had.upper-had.lower)
        vadjustment = (vad.value-vad.lower)/(vad.upper-vad.lower)
        return (hadjustment, vadjustment)

    def set_context(self, ctx):
        had = self.view.get_hadjustment()
        vad = self.view.get_vadjustment()
        had.set_value(ctx[0]*(had.upper-had.lower)+had.lower)
        vad.set_value(ctx[1]*(vad.upper-vad.lower)+vad.lower)
        return False
