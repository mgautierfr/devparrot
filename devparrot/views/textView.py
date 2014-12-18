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
from itertools import islice
import ttk, Tkinter

class TextView(object):
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
        self.createdLines = 0
        self.createdLabels = 0
        self.idle_handle = None

    def destroy(self):
        if self.view:
            self.view.destroy()
        self.uiContainer.destroy()
        self.hScrollbar.destroy()
        self.vScrollbar.destroy()
        self.lineNumbers.destroy()
        self.sectionInfo.destroy()
        self.uiContainer = self.hScrollbar = self.vScrollbar = None
        self.lineNumbers = self.sectionInfo = self.view = self.document = None

    def focus(self):
        return self.view.focus()

    def proxy_yview(self, *args, **kwords):
        if self.view:
            self.view.yview(*args, **kwords)
            self.update_infos()

    def proxy_yscrollcommand(self, *args, **kwords):
        if args == ('0.0' , '1.0'):
            self.vScrollbar.grid_remove()
        else:
            self.vScrollbar.grid_configure()
        self.vScrollbar.set(*args, **kwords)
        self.update_infos()

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

    def update_infos(self):
        if self.idle_handle:
            self.view.after_cancel(self.idle_handle)

        self.idle_handle = self.view.after(0, self._update_infos)

    def _update_infos(self):
        self.idle_handle = None
        firstLine = self.view.index('@0,0').line
        firstLine = max(firstLine, 1)

        lastIndex = self.view.index('@0,{}'.format(self.view.winfo_height()))
        lastLine = lastIndex.line

        firstIndex = self.view.calculate_distance(Start, self.view.index("%d.0"%firstLine))
        lastIndex = self.view.calculate_distance(Start, self.view.index("%d.0 lineend"%lastLine))

        self.set_lineNumbers(firstLine, lastLine)
        self.set_rangeInfo(firstIndex, lastIndex)


    def set_lineNumbers(self, firstLine, lastLine):
        self.lineNumbers.config(state='normal')

        ilabel = 1
        for i in xrange( firstLine , lastLine+1 ):
            pos = self.view.bbox("{}.0".format(i))
            if not pos:
                continue
            label = "t%d"%ilabel
            if ilabel > self.createdLabels:
                self.lineNumbers.create_text("0", "0", anchor="nw", tags=[label], state="hidden")
                self.createdLabels += 1
            ilabel += 1

            self.lineNumbers.coords(label, "0", str(pos[1]))
            self.lineNumbers.itemconfig(label, state="disable", text=str(i))

        for i in xrange(ilabel, self.createdLabels+1):
            self.lineNumbers.itemconfig("t%d"%i, state="hidden")

        bbox = self.lineNumbers.bbox('all')
        if bbox:
            w = int(bbox[2])
            if self.actualLineNumberWidth < w:
                self.actualLineNumberWidth = w
                self.lineNumbers.config(width=self.actualLineNumberWidth)

        self.lineNumbers.config(state='disable')

    def set_rangeInfo(self, firstIndex, lastIndex):
        class NonLocal: pass
        nonlocal = NonLocal()
        nonlocal.ilabel = 1
        nonlocal.loopCounter = 0

        def inner(sectionStart, visibleStart, visibleStop, sections, depth):
            pixelDepth = 4*depth

            if not sections:
                return

            start, end = 0, len(sections)
            middle = None

            startSectionIndex = None
            needBreak = False
            #import pdb; pdb.set_trace()
            while True:
                if needBreak:
                    break
                nonlocal.loopCounter += 1
                middle = (start+end)/2
                #print " "*depth, visibleIndex[1], start, middle, end
                # we need to stop
                if middle == start:
                    needBreak = True

                section = sections[middle]

                if section.startIndex >= visibleStop:
                    # this section start after being visible
                    end = middle
                    continue

                if section.length is not None and section.startIndex + section.length <= visibleStart:
                    # this section finish before being visible, 
                    start = middle
                    continue

                # From here, this section is visible. It start before, finish after or is fully visible.
                # As it may be the one so :
                startSectionIndex = middle

                if section.startIndex < visibleStart:
                    # This section start befoer and is visible. We have found the good one.
                    break

                # Test if sections before the current one are visible (and so the current one is not the good)
                end = middle

            if startSectionIndex is None:
                #we do not have any section visible:
                return

            #print " "*depth, "startIndex is", startSectionIndex

            for section in islice(sections, startSectionIndex, None):
                if section.startIndex >= visibleStop:
                    # we arrive to a section no more visible => stop
                    break

                # update start indices accordingly to the current section
                newVisibleStart = visibleStart - section.startIndex
                newVisibleStop = visibleStop - section.startIndex
                startIndex = self.view.addchar(sectionStart, section.startIndex)

                if section.length is not None:
                    endIndex = self.view.addchar(startIndex, section.length)

                    if endIndex.line == startIndex.line:
                        # section start and stop on same line, do no display it
                        continue

                    self.maxDepth = max(self.maxDepth, pixelDepth)
                    endPos   =  self.view.dlineinfo("%d.0"%endIndex.line)
                    endPos = endPos or [0, self.view.winfo_height(), 0, 0, 0]
                    endPos = int(endPos[1]) + int(endPos[3])/2
                else:
                    endPos = self.view.winfo_height()

                # Try to get the coordinates of the line to display.
                # If we can get them, this is cause they are out of the screen so get limite values.
                startPos =  self.view.dlineinfo("%d.0"%startIndex.line)
                startPos = startPos or [0, 0, 0, 0, 0]
                startPos = int(startPos[1]) + int(startPos[3])/2
                #print " "*depth, "visibleIndex %s | sectionStart %s | sectionEnd %s | startIndex %s | endIndex %s | startPos %s | endPos %s"%(visibleIndex, section.startIndex, section.startIndex+section.length, startIndex, endIndex, startPos, endPos)

                # Now get the tag corresponding to a available line else create a line.
                label = "t%d"%nonlocal.ilabel
                if nonlocal.ilabel > self.createdLines:
                    self.sectionInfo.create_line(pixelDepth, startPos, pixelDepth, endPos, tags=[label])
                    self.createdLines += 1
                nonlocal.ilabel += 1

                # Display the lines where we need to.
                self.sectionInfo.itemconfig(label, state="disable")
                self.sectionInfo.coords(label, pixelDepth, startPos, pixelDepth, endPos)

                # update end index and start again with children
                inner(startIndex, newVisibleStart, newVisibleStop, section.innerSections, depth+1)

            #print " "*depth, "checked for %s depth %s"%(visibleIndex, depth)

        inner(Start, firstIndex, lastIndex, self.view.rangeInfo.innerSections, 0)

        for i in xrange(nonlocal.ilabel, self.createdLines+1):
            self.sectionInfo.itemconfig("t%d"%i, state="hidden")
        self.sectionInfo.config(width=self.maxDepth+2)

        #print "loopCounter %s | ilabel %s"%(nonlocal.loopCounter, nonlocal.ilabel)
    
    def on_event_lineChanged(self, *args):
        self.update_infos()


    def set_model(self, model):
        self.view = model
        self.view['yscrollcommand'] = self.proxy_yscrollcommand
        self.view['xscrollcommand'] = self.proxy_xscrollcommand
        self.hScrollbar['command'] = self.view.xview
        self.view.grid(column=10, row=0, in_=self.uiContainer, sticky=(ttk.Tkinter.N, ttk.Tkinter.S, ttk.Tkinter.E, ttk.Tkinter.W))
        self.view.lift(self.uiContainer)
        session.eventSystem.connect('insert', self.on_event_lineChanged)
        session.eventSystem.connect('delete', self.on_event_lineChanged)

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
