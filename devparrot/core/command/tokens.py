class Token(object):
    def __init__(self, **kw):
        self.index = kw['index']
        self.len = kw['len']

    def get_type(self):
        return self.__class__.__name__

    def pprint(self, ident):
        print ident, "%s : %s(%s)"%(self.__class__.__name__, self.index, self.len)

    def get_last_commandCall(self):
        return None

class Identifier(Token):
    def __init__(self, **kw):
        super(Identifier, self).__init__(**kw)
        self.name = kw['name']

    def __str__(self):
        return self.name

    def rewrited(self):
        return '"%s"'%self.name

    def pprint(self, ident):
        super(Identifier, self).pprint(ident)
        print ident, " - name :", self.name

class Number(Token):
    def __init__(self, **kw):
        super(Number, self).__init__(**kw)
        self.value = kw['value']

    def __str__(self):
        return '%s'%self.value

    def rewrited(self):
        return str(self)

    def pprint(self, ident):
        super(Number, self).pprint(ident)
        print ident, " - value :",self.value


class Section(Token):
    def __init__(self, **kw):
        super(Section, self).__init__(**kw)
        self.closed = kw['closed']
        self.values = kw['values']

    def pprint(self, ident):
        super(Section, self).pprint(ident)
        print ident, " - closed:", self.closed
        print ident, " - values:"
        if isinstance(self.values, list):
            for v in self.values:
                v.pprint(ident+"    ")
        else:
            print ident+"    ", self.values

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

    def get_last_commandCall(self):
        if self.closed or not self.values:
            return None
        return self.values[-1].get_last_commandCall()

class CommandCall(Section, Identifier):
    opener, closer = "()"
    def __init__(self, **kw):
        super(CommandCall, self).__init__(**kw)

    def __str__(self):
        return "%(name)s%(parameters)s"%{
            'name' : self.name,
            'parameters' : Section.__str__(self)
          }

    def rewrited(self):
        return "%(name)s%(parameters)s"%{
            'name' : self.name,
            'parameters' : Section.rewrited(self)
          }

    def pprint(self, ident):
        super(CommandCall, self).pprint(ident)

    def get_last_commandCall(self):
        ret = Section.get_last_commandCall(self)
        if not ret and not self.closed:
            return self
        return ret


class String(Section):
    def __init__(self, **kw):
        super(String, self).__init__(**kw)

    def __str__(self):
        return self.enclose(self.values)

    def rewrited(self):
        return self.rewrited_enclose(self.values)

    def pprint(self, ident):
        super(String, self).pprint(ident)

    def get_last_commandCall(self):
        return None

class SimpleString(String):
    opener, closer = "''"
    def __init__(self, **kw):
        super(SimpleString, self).__init__(**kw)

    def pprint(self, ident):
        super(SimpleString, self).pprint(ident)


class DoubleString(String):
    opener, closer = '""'
    def __init__(self, **kw):
        super(DoubleString, self).__init__(**kw)

    def pprint(self, ident):
        super(DoubleString, self).pprint(ident)

class UnquotedString(String):
    opener, closer = '""'
    def __init__(self, **kw):
        kw['closed'] = False
        super(UnquotedString, self).__init__(**kw)

    def pprint(self, ident):
        super(UnquotedString, self).pprint(ident)

class List(Section):
    opener, closer = "[]"
    def __init__(self, **kw):
        super(List, self).__init__(**kw)

    def pprint(self, ident):
        super(List, self).pprint(ident)

class KeywordArg(Identifier):
    def __init__(self, **kw):
        super(KeywordArg, self).__init__(**kw)
        self.value = kw['value']

    def __str__(self):
        return "%s=%s"%(self.name, str(self.value))

    def rewrited(self):
        return "%s=%s"%(self.name, self.value.rewrited())

    def pprint(self, ident):
        super(KeywordArg, self).pprint(ident)
        print ident, " - value:"
        try:
            self.value.pprint(ident+"    ")
        except AttributeError:
            print ident+"    ", self.value

class New(Token):
    def __init__(self, **kw):
        kw['len'] = 0
        super(New, self).__init__(**kw)

    def __str__(self):
        return ""

    def rewrited(self):
        return ""

    def pprint(self,ident):
        super(New, self).pprint(ident)