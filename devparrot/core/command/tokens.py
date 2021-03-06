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


class Token:
    def __init__(self, **kw):
        self.index = kw['index']
        self.len = kw['len']

    def get_type(self):
        return self.__class__.__name__

    def __eq__(self, other):
        try:
            return self.get_type() == other.get_type() and self.index == other.index and self.len == other.len
        except AttributeError:
            return False

    def pprint(self, ident):
        print(ident, "%s : %s(%s)"%(self.__class__.__name__, self.index, self.len))

class Identifier(Token):
    def __init__(self, **kw):
        super(Identifier, self).__init__(**kw)
        self.name = kw['name']

    def __eq__(self, other):
        return super(Identifier, self).__eq__(other) and self.name == other.name

    def __str__(self):
        return self.name

    def rewrited(self):
        return '"%s"'%self.name

    def pprint(self, ident):
        super(Identifier, self).pprint(ident)
        if isinstance(self.name, Token):
            print(ident, " -name:")
            self.name.pprint(ident+"    ")
        else:
            print(ident, " -name :", self.name)

class Number(Token):
    def __init__(self, **kw):
        super(Number, self).__init__(**kw)
        self.value = kw['value']

    def __eq__(self, other):
        return super(Number, self).__eq__(other) and self.value == other.value

    def __str__(self):
        return '%s'%self.value

    def rewrited(self):
        return str(self)

    def pprint(self, ident):
        super(Number, self).pprint(ident)
        print(ident, " - value :",self.value)


class Section(Token):
    def __init__(self, **kw):
        super(Section, self).__init__(**kw)
        self.__dict__['closed'] = kw['closed']
        self.values = kw['values']

    def __eq__(self, other):
        return super(Section, self).__eq__(other) and self.closed == other.closed and self.values == other.values

    def pprint(self, ident):
        super(Section, self).pprint(ident)
        print(ident, " - closed:", self.closed)
        print(ident, " - values:")
        if isinstance(self.values, list):
            for v in self.values:
                if isinstance(v, Token):
                    v.pprint(ident+"    ")
                else:
                    print(ident,"    ", repr(v))
        else:
            print(ident+"    ", repr(self.values))

    def enclose(self, text):
        return "%s%s%s"%(self.__class__.opener, text, self.__class__.closer if self.closed else "")

    def rewrited_enclose(self, text):
        return "%s%s%s"%(self.__class__.opener, text, self.__class__.closer)

    def __str__(self):
        text = ", ".join((str(v) for v in self.values))
        return self.enclose(text)

    def rewrited(self):
        text = ", ".join((v.rewrited() for v in self.values))
        return self.rewrited_enclose(text)

class CommandCall(Section, Identifier):
    opener, closer = "()"
    def __init__(self, **kw):
        super(CommandCall, self).__init__(**kw)

    def __eq__(self, other):
        return super(CommandCall, self).__eq__(other)

    def __str__(self):
        return "%(name)s%(parameters)s"%{
            'name' : self.name,
            'parameters' : Section.__str__(self)
          }

    def __setattr__(self, name, value):
        if name == "closed" and value:
            if self.values[-1].get_type() == "New":
                del self.values[-1]
        super(CommandCall, self).__setattr__(name, value)

    def rewrited(self):
        return "%(name)s.resolve%(parameters)s"%{
            'name' : self.name,
            'parameters' : Section.rewrited(self)
          }

    def pprint(self, ident):
        super(CommandCall, self).pprint(ident)

class MacroCall(CommandCall):
    opener, closer = "()"
    def __init__(self,  **kw):
        self.opened = kw['opened']
        self.expanded = kw['expanded']
        super(MacroCall, self).__init__(**kw)

    def __eq__(self, other):
        return super(MacroCall, self).__eq__(other)

    def __str__(self):
        return super(MacroCall, self).__str__()

    def rewrited(self):
        return "%(expanded)s_macros['%(name)s'].resolve%(parameters)s)"%{
            'name' : self.name,
            'parameters' : Section.rewrited(self),
            'expanded' : '*_MacroListResult(' if self.expanded else '_MacroResult('
          }

    def pprint(self, ident):
        super(MacroCall, self).pprint(ident)
        print(ident, " - opened:", self.opened)
        print(ident, " - expanded:", self.expanded)

class Pipe(Token):
    def __init__(self, **kw):
        super(Pipe, self).__init__(**kw)
        self.values = kw['values']

    def __eq__(self, other):
        return super(Pipe, self).__eq__(other) and self.values == other.values

    def pprint(self, ident):
        super(Pipe, self).pprint(ident)
        print(ident, " - values:")
        if isinstance(self.values, list):
            for v in self.values:
                if isinstance(v, Token):
                    v.pprint(ident+"    ")
                else:
                    print(ident, "    ", repr(v))
        else:
            print(ident+"    ", self.values)

    def __str__(self):
        text = " | ".join((str(v) for v in self.values))
        return text

    def rewrited(self):
        text = " | ".join((v.rewrited() for v in self.values))
        return text

class String(Section):
    def __init__(self, **kw):
        super(String, self).__init__(**kw)

    def __eq__(self, other):
        return super(String, self).__eq__(other)

    def __str__(self):
        return self.enclose(self.values)

    @property
    def value(self):
        return self.values

    def rewrited(self):
        return "%s%s%s"%('"""', self.values.replace("\\", "\\\\"), '"""')

    def pprint(self, ident):
        super(String, self).pprint(ident)

class SimpleString(String):
    opener, closer = "''"
    def __init__(self, **kw):
        super(SimpleString, self).__init__(**kw)

    def __eq__(self, other):
        return super(SimpleString, self).__eq__(other)

    def pprint(self, ident):
        super(SimpleString, self).pprint(ident)


class DoubleString(String):
    opener, closer = '""'
    def __init__(self, **kw):
        super(DoubleString, self).__init__(**kw)

    def __eq__(self, other):
        return super(DoubleString, self).__eq__(other)

    def pprint(self, ident):
        super(DoubleString, self).pprint(ident)

class UnquotedString(String):
    opener, closer = '""'
    def __init__(self, **kw):
        super(UnquotedString, self).__init__(**kw)

    def __eq__(self, other):
        return super(UnquotedString, self).__eq__(other)

    def pprint(self, ident):
        super(UnquotedString, self).pprint(ident)

class List(Section):
    opener, closer = "()"
    def __init__(self, **kw):
        super(List, self).__init__(**kw)

    def __eq__(self, other):
        return super(List, self).__eq__(other)

    def pprint(self, ident):
        super(List, self).pprint(ident)

class KeywordArg(Identifier):
    def __init__(self, **kw):
        super(KeywordArg, self).__init__(**kw)
        self.value = kw['value']

    def __eq__(self, other):
        return super(KeywordArg, self).__eq__(other) and self.value == other.value

    def __str__(self):
        return "%s=%s"%(self.name, str(self.value))

    def rewrited(self):
        return "%s=%s"%(self.name, self.value.rewrited())

    def pprint(self, ident):
        super(KeywordArg, self).pprint(ident)
        print(ident, " - value:")
        try:
            self.value.pprint(ident+"    ")
        except AttributeError:
            print(ident+"    ", self.value)

class New(Token):
    def __init__(self, **kw):
        kw['len'] = 0
        super(New, self).__init__(**kw)

    def __eq__(self, other):
        return super(New, self).__eq__(other)

    def __str__(self):
        return ""

    @property
    def value(self):
        return ""

    def rewrited(self):
        return ""

    def pprint(self,ident):
        super(New, self).pprint(ident)
