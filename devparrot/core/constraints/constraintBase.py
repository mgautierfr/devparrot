
from devparrot.core.completion import BaseCompletion
from devparrot.core.errors import UserCancel, NoDefault
from devparrot.core.command.tokens import New
from functools import reduce
import inspect

class DoubleStringCompletion(BaseCompletion):
    def __init__(self, startIndex, value, final, already):
        BaseCompletion.__init__(self, startIndex=startIndex)
        self.value = value
        self._final = final
        self.already = already

    def name(self):
        template = '"%s"' if self._final else '"%s'
        return template % self.value

    def complete(self):
        template = '"%s"' if self._final else '"%s'
        return template % self.value[self.already:]

    def final(self):
        return self._final


class SimpleStringCompletion(BaseCompletion):
    def __init__(self, startIndex, value, final, already):
        BaseCompletion.__init__(self,startIndex=startIndex)
        self.value = value
        self._final = final
        self.already = already

    def name(self):
        template = "'%s'" if self._final else "'%s"
        return template % self.value

    def complete(self):
        template = "'%s'" if self._final else "'%s"
        return template % self.value[self.already:]

    def final(self):
        return self._final


class Completion(BaseCompletion):
    def __init__(self, startIndex, value, final, already):
        BaseCompletion.__init__(self,startIndex=startIndex)
        self.value = value
        self._final = final
        self.already = already

    def name(self):
        return self.value + (" " if self._final else "")

    def complete(self):
        return self.value[self.already:] + (" " if self._final else "")

    def final(self):
        return self._final

type_to_completion = {
    'DoubleString'   : DoubleStringCompletion,
    'SimpleString'   : SimpleStringCompletion,
    'UnquotedString' : Completion,
    'Identifier'     : Completion,
    'New'            : Completion
}

class ConstraintMeta(type):
    def __new__(cls, name, bases, dct):
        if name =="_Constraint":
            return type.__new__(cls, name, bases, dct)
        from devparrot.core.help import add_helpEntry
        _class = type.__new__(cls, name, bases, dct)
        add_helpEntry(name, _class, ["constraints"])
        return _class


class _Constraint(metaclass=ConstraintMeta):
    class _NoDefault:
        def __call__(self):
            raise NoDefault()

        def __bool__(self):
            return False

    def __init__(self, multiple=False, default=None, askUser=False, help=""):
        self.askUser = askUser
        if default is None:
            self.default = _Constraint._NoDefault()
        else:
            self.default = default
        self.multiple = multiple
        self.isVararg = False
        self.help=help

    def check_arg(self, args):
        if self.multiple:
            valids, args = zip(*[self._check(arg) for arg in args])
            valid = reduce(lambda x, y: x and y, valids)
            if not valid:
                return False, None
            return True, args
        else:
            return self._check(args)

    def _check(self, arg):
        from devparrot.core.command.wrappers import MacroResult
        if isinstance(arg, MacroResult):
            return self.check_direct(arg())
        else:
            return self.check(arg)

    def complete_context(self, context):
        if not self.multiple and context.get_type() == "List":
            return []

        if self.multiple and context.get_type() == 'New':
            return (None, [Completion(context.index, "[", False, 0)])

        if self.multiple:
            if context.get_type() != "List":
                return []
            if context.values:
                context = context.values[-1]
            else:
                context = New(index=context.index+1)

        if context.get_type() == "List":
            # more than one open context. can't handle it (for now?)
            return []

        return self.complete(context)

    def check(self, token):
        return True, token

    check_direct = check
    
    def ask_user(self):
        raise UserCancel()

    def complete(self, token):
        if token.get_type().endswith('String'):
            return [type_to_completion[token.get_type()](token.index, token.values, token.closed, len(token.values))]
        if token.get_type() == 'Identifier':
            return [Completion(token.index, token.name, False, len(token.name))]
        return []

    def get_userHelp(self):
        return self.help

    @classmethod
    def get_help(cls):
        last = "%s constraint:"%cls.__name__
        yield last+"\n"
        yield "="*len(last)+"\n"
        yield "\n"

        yield inspect.getdoc(cls) or "no description...\n"
        yield "\n"

    @classmethod
    def get_helpName(cls):
        return "constraints.%s"%cls.__name__
