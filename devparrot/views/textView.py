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
from devparrot.core.utils.posrange import Start
from itertools import dropwhile, takewhile
import ttk, Tkinter

class DisplayedRange(object):
    def __init__(self, view, lineId):
        self.view = view
        self.lineId = lineId
        self.subRange = set()

    def destroy(self):
        self.view.sectionInfo.itemconfig(self.lineId, state="hidden")
        self.view.freeLines.add(self.lineId)
        [s.destroy() for s in self.subRange]
        self.subRange.clear()

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
        self.vScrollbar.grid(column=100,
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

        self.sectionInfo = ttk.Tkinter.Canvas(session.get_globalContainer(),
                                              highlightthickness = 0,
                                              takefocus = 0,
                                              bd=0,
                                              background = 'lightgrey',
                                              state='disable')
        self.sectionInfo.grid(column=1,
                              row=0,
                              in_=self.uiContainer,
                              sticky="nsw")

        self.uiContainer.columnconfigure(0, weight=0)
        self.uiContainer.columnconfigure(1, weight=0)
        self.uiContainer.columnconfigure(10, weight=1)
        self.uiContainer.columnconfigure(100, weight=0)
        self.uiContainer.rowconfigure(0, weight=1)
        self.uiContainer.rowconfigure(1, weight=0)
        
        self.vScrollbar['command'] = self.proxy_yview

        self.document = document
        self.view = None

        self.actualLineNumberWidth = 0
        self.maxDepth = 0
        self.knownSection = set()
        self.freeLines = set()
        self.createdLabels = 0

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
        
        _firstLine = self.view.index('@0,0').line-1
        firstLine = max(_firstLine, 1)

        lastIndex = self.view.index('@0,{}'.format(self.view.winfo_height()))
        _lastLine = lastIndex.line
        lastLine = _lastLine

        ilabel = 1
        for i in xrange( firstLine , lastLine+1 ):
            pos = self.view.bbox("{}.0".format(i))
            if not pos:
                continue
            label = "t%d"%ilabel
            if ilabel > self.createdLabels:
                self.lineNumbers.create_text("0", "0", anchor="nw", tags=[label], state="hidden")
                self.createdLabels += 1

            self.lineNumbers.coords(label, "0", str(pos[1]))
            self.lineNumbers.itemconfig(label, state="disable", text=str(i))
            ilabel += 1

        for i in xrange(ilabel, self.createdLabels+1):
            self.lineNumbers.itemconfig("t%d"%i, state="hidden")

        bbox = self.lineNumbers.bbox('all')
        if bbox:
            w = int(bbox[2])
            if self.actualLineNumberWidth < w:
                self.actualLineNumberWidth = w
                self.lineNumbers.config(width=self.actualLineNumberWidth)

        self.lineNumbers.config(state='disable')

        firstIndex = self.view.calculate_distance(Start, self.view.index("%d.0"%_firstLine))
        lastIndex = self.view.calculate_distance(Start, self.view.index("%d.0 lineend"%_lastLine))
        for displayed in self.knownSection:
            displayed.destroy()
        self.knownSection.clear()
        self.set_rangeInfo(Start, firstIndex, lastIndex, _firstLine+1, _lastLine-1, self.view.rangeInfo.innerSections, 0, self.knownSection)
        self.sectionInfo.config(width=self.maxDepth+2)

    def set_rangeInfo(self, start, firstIndex, lastIndex, firstLine, lastLine, sections, depth, container):
        pixelDepth = 4*depth

        _sections = dropwhile(lambda s: s.length is not None and s.startIndex+s.length <= firstIndex, sections)
        _sections = takewhile(lambda s: s.startIndex <= lastIndex, _sections)

        for section in _sections:
            newStartIndex = max(section.startIndex, firstIndex) - section.startIndex
            startIndex = self.view.addchar(start, section.startIndex)
            if section.length is not None:
                endIndex = self.view.addchar(startIndex, section.length)
                if endIndex.line <= firstLine or startIndex.line >= lastLine:
                    continue
                if endIndex.line == startIndex.line:
                    continue
                self.maxDepth = max(self.maxDepth, pixelDepth)

                startPos =  self.view.dlineinfo("%d.0"%startIndex.line)
                endPos   =  self.view.dlineinfo("%d.0"%endIndex.line)
                startPos = startPos or [0, 0, 0, 0, 0]
                endPos = endPos or [0, self.view.winfo_height(), 0, 0, 0]
                startPos = int(startPos[1]) + int(startPos[3])/2
                endPos = int(endPos[1]) + int(endPos[3])/2
                try:
                    lineId = self.freeLines.pop()
                    self.sectionInfo.itemconfig(lineId, state="disable")
                    self.sectionInfo.coords(lineId, pixelDepth, startPos, pixelDepth, endPos)
                except KeyError:
                    lineId = self.sectionInfo.create_line(pixelDepth, startPos, pixelDepth, endPos)
                drange = DisplayedRange(self, lineId)
                container.add(drange)
                newLastIndex = min(section.startIndex+section.length, lastIndex) - section.startIndex
                subContainer = drange.subRange
                depth += 1
            else:
                newLastIndex = lastIndex - section.startIndex
                subContainer = container
            self.set_rangeInfo(startIndex, newStartIndex, newLastIndex, firstLine, lastLine, section.innerSections, depth, subContainer)


    
    def on_event_lineChanged(self, *args):
        self.set_lineNumbers()


    def set_model(self, model):
        self.view = model
        self.view['yscrollcommand'] = self.proxy_yscrollcommand
        self.view['xscrollcommand'] = self.proxy_xscrollcommand
        self.hScrollbar['command'] = self.view.xview
        self.view.grid(column=10, row=0, in_=self.uiContainer, sticky=(ttk.Tkinter.N, ttk.Tkinter.S, ttk.Tkinter.E, ttk.Tkinter.W))
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
