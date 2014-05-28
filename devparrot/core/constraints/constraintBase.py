
from devparrot.core.completion import Completion
from devparrot.core.command.commandCompleter import DoubleStringCompletion, SimpleStringCompletion
from devparrot.core.errors import UserCancel, NoDefault
from devparrot.core.command.tokens import New

type_to_completion = {
    'DoubleString'   : DoubleStringCompletion,
    'SimpleString'   : SimpleStringCompletion,
    'UnquotedString' : Completion,
    'Identifier'     : Completion,
    'New'            : Completion
}


class _Constraint(object):
    class _NoDefault(object):
        def __call__(self):
            raise NoDefault()

        def __nonzero__(self):
            return False

    def __init__(self, optional=False, multiple=False, default=None, askUser=False, help=""):
        self.optional = optional
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
            valids, args = zip(*[self.check(arg) for arg in args])
            valid = reduce(lambda x, y: x and y, valids)
            if not valid:
                return False, None
            return True, args
        else:
            return self.check(args)

    def complete_context(self, context):
        if not self.multiple and context.get_type() == "List":
            return (None, [])

        if self.multiple and context.get_type() == 'New':
            return (None, [Completion("[", False)])

        if self.multiple:
            if context.get_type() != "List":
                return (None, [])
            if context.values:
                context = context.values[-1]
            else:
                context = New(index=context.index+1)

        if context.get_type() == "List":
            # more than one open context. can't handle it (for now?)
            return (None, [])

        return (context.index, self.complete(context))

    def check(self, token):
        return True, token
    
    def ask_user(self):
        raise UserCancel()

    def complete(self, token):
        if token.get_type().endswith('String'):
            return [type_to_completion[token.get_type()](token.values, token.closed)]
        if token.get_type() == 'Identifier':
            return [Completion(token.name, False)]
        return []

    def get_help(self):
        return self.help
