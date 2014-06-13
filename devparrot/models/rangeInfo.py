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


import re
from operator import attrgetter

sectionsDef = {}


class SectionDefMeta(type):
    def __new__(cls, name, bases, dct):
        if name == "SectionDef":
            return type.__new__(cls, name, bases, dct)
        dct.setdefault('start', '')
        _class = type.__new__(cls, name, bases, dct)
        sectionsDef[name] = _class
        return _class


def filter_enclosing(index):
    def filter_(section):
        if section.startIndex <= index:
            if section.length is None:
                return 0
            if section.startIndex+section.length > index:
                return 0
        return section.startIndex - index
    return filter_

class SectionDef(object):
    __metaclass__ = SectionDefMeta

    def __init__(self, startIndex):
        self.length = None
        self.startIndex = startIndex
        self.innerSections = []
        self.innerGhosts = []
        self.lengthGhost = None

    def get_regex(self):
        exclude = getattr(self, 'exclude', None)
        contains = getattr(self, 'contains', [])
        end = getattr(self, 'end', None)
        regs = []
        if exclude:
            regs.append("(?P<exclude>%s)"%re.escape(exclude))

        if end:
            regs.append("(?P<end>%s)"%re.escape(end))
            
        if contains:
            regs.append("(?P<start>%s)"%("|".join(set(re.escape(sectionsDef[sect].start) for sect in contains if sectionsDef[sect].start))))

        return "(%s)"%("|".join(regs))

    def close(self, length):
        if self.length == length:
            # Everything is good
            return False
        self.length = length
        return True

    def insert_section(self, section):
        self.innerSections.append(section)
        self.innerSections.sort(key=attrgetter('startIndex'))

    def get_section(self, filter_):
        if not self.innerSections:
            #print "get_section, no inner"
            return None, None
        start, end = 0, len(self.innerSections)
        middle = (end+start)/2
        while True:
            middle = (end+start)/2
            needStop = (middle == start)
            #print "get_section1", start, middle, end
            section = self.innerSections[middle]
            ret = filter_(section)
            if ret == 0:
                return middle, section
            if ret > 0:
                end = middle
            else:
                start = middle
            
            if needStop :
                break
        return None, None

    def clean_section(self, index1, index2):
        #print "clean section between", index1, index2
        #print self.innerSections
        self.innerSections = [section for section in self.innerSections if (section.startIndex < index1 or section.startIndex >= index2)]
        #print self.innerSections

    def ghost_section(self, section_index):
        """put all section after section_index in the ghost containers"""
        self.innerGhosts = self.innerSections[section_index+1:]
        self.innerSections = self.innerSections[:section_index+1]
        self.lengthGhost = self.length

    def ghost_section_after(self, index):
        """put all section starting after index in the ghost containers"""
        try:
            section_index = next(idx for idx, section in enumerate(self.innerSections) if section.startIndex > index)
            self.ghost_section(section_index-1)
        except StopIteration:
            pass

    def _update_metadata_pos(self, changeIndex, changeLen):
        if self.length:
            self.length += changeLen
        for section in self.innerSections:
            if section.startIndex > changeIndex:
                section.startIndex += changeLen

    def _update_metadata_neg(self, changeIndex, changeLen):
        if self.length:
            self.length -= changeLen
        self.clean_section(changeIndex, changeIndex+changeLen)
        for section in self.innerSections:
            if section.startIndex > changeIndex+changeLen:
                section.startIndex -= changeLen

    def parse_text(self, content, changeIndex=0, changeLen=None, debug=False):
        """
        parse a content to update ourselves

        @param content             The content to parse
        @param changeIndex         Where the change append (default to 0)
        @param changeLen           How many char have been added (deleted if <0), if None (default), equal to len(content)
        @return (changed, eated)   changed  : True if section has changed. (index update doesn't count)
                                   eated    : How many char have beend consumed
        """
        #print self.__class__.__name__, ": parse_text", repr(content), "changeIndex=", changeIndex, "changeLen=", changeLen
        if debug:
            import pdb; pdb.set_trace()
        if changeLen is None:
            changeLen = len(content)
        changed = False

        if not changeLen:
            return False, 0

        # first of all, update our section about index change
        if changeLen > 0:
            self._update_metadata_pos(changeIndex, changeLen)
        else:
            self._update_metadata_neg(changeIndex, -changeLen)

        #remove our start token
        index = len(self.start)

        # do we have a section enclosing the change ?

        section_index, section = self.get_section(filter_enclosing(changeIndex))
        if section:
            #print "matching section" ,section
            changed, index = section.parse_text(content[section.startIndex:], changeIndex-section.startIndex, changeLen)
            index += section.startIndex
            if not changed:
                # the parse of the subsection doesn't change what we already know, just return False
                #print "not changed"
                return False, index
            if section.length is None:
                # inner section is not closed, we can't be closed ourself
                #print "no length"
                self.ghost_section(section_index)
                changed |= self.close(None)
                return changed, index
            
            # some thing change, keep analysing
            #print "keep analy", index, section.startIndex
            self.ghost_section_after(section.startIndex)
        else:
            index = max(index, changeIndex)
            

        content = content[index:]
        
        # then parse the text to see if we've got some changes
        while True:
            resultats = {'exclude':None, 'end':None, 'start':None}
            regex = self.get_regex()
            #print "search for", regex #, "in", repr(content),
            match = re.search(regex, content)
            if match is None:
                #print "=> None"
                changed |= self.close(None)
                return changed, index


            self.clean_section(index, index+match.start())
            resultats.update(match.groupdict())
            #print "=>", resultats, match.start(), match.end()

            if resultats['exclude']:
                # we found our exclude, skip it
                index += match.end()
                content = content[match.end():]

            elif resultats['end']:
                # we found our end, close ourself
                index += match.end()
                changed |= self.close(index)
                self.ghost_section_after(index)
                break
            else:
                # we found a start of a section
                #print "found section", repr(match.group()), "at pos", match.start()
                # it is a new one ?
                new = False
                try:
                    section_index, section = next((idx, section) for idx, section in enumerate(self.innerSections) if (section.startIndex == index+match.start() and section.start == resultats['start']))
                    if section.startIndex >= changeIndex+changeLen:
                        #we have found an already known section after the modif. Just finish
                        return changed, index
                    self.ghost_section(section_index)
                except StopIteration:
                    # Do we have ghosts sections corresponding ?
                    if self.innerGhosts and index+match.start() >= changeIndex+changeLen:
                        # we are after the changes
                        if self.innerGhosts[0].startIndex == index+match.start() and self.innerGhosts[0].start == resultats['start']:
                            self.innerSections.extend(self.innerGhosts)
                            self.close(self.lengthGhost)
                            self.lengthGhost = None
                            self.innerGhosts = []
                            return True, self.length
                        self.lengthGhost = None
                        self.innerGhosts = []

                    # no section, create a new one and insert it
                    section = next(sectionsDef[name] for name in self.contains if sectionsDef[name].start == match.group())(index+match.start())
                    new = True
                    changed = True

                index += match.start()
                content = content[match.start():]
                changed_ , index_ = section.parse_text(content)

                self.clean_section(index, index+index_)
                if new:
                    #self.ghost_section(index_)
                    
                    self.insert_section(section)
                changed |= changed_
                index   += index_
                if section.length is None:
                    # inner section is not closed, we can't be closed ourself
                    #self.ghost_section(index_)
                    changed |= self.close(None)
                    return changed, index
                content = content[index_:]
            #print self.innerSections

        return changed, index


    def __str__(self):
        return "<section %(id)s %(name)s %(start)s:%(len)s [%(contains)s] {%(ghosteds)s}>"%{'id':id(self),'name':self.__class__.__name__, 'contains':', '.join(str(sect) for sect in self.innerSections), 'start':self.startIndex, 'len':self.length, 'ghosteds':','.join(str(sect) for sect in self.innerGhosts)}

    __repr__ = __str__

expression = ['Comment', 'MultiLine_Comment', 'Paren', 'Bracket', 'Brace', 'String']

class Comment(SectionDef):
    start = '//'
    end='\n'

class MultiLine_Comment(SectionDef):
    start='/*'
    end='*/'
    
class Paren(SectionDef):
    start='('
    end=')'
    contains=expression

class Bracket(SectionDef):
    start='['
    end=']'
    contains=expression

class Brace(SectionDef):
    start='{'
    end='}'
    contains=expression

class String(SectionDef):
    start='"'
    end='"'
    exclude=r'\"'


class Document(SectionDef):
    contains = expression
    def __init__(self):
        SectionDef.__init__(self, 0)

def parse_text(content):
    document = Document()
    #import pdb; pdb.set_trace()
    document.parse_text(content)
    return document



