
import constraints
from baseCommand import CommandWrapper

class AliasWrapper(CommandWrapper):
    def __init__(self, constraints):
        CommandWrapper.__init__(self, constraints, None)

    def __call__(self, *args, **kwords):
        try:
            call_list, call_kwords = self._get_call_args(args, kwords)
            return self.functionToCall(*call_list, **call_kwords)
        except constraints.userCancel:
            pass



class Alias(object):
    from devparrot.core import session
    def __init__(self, **kwords):
        self.wrapper = AliasWrapper(kwords)

    def __call__(self, function, section=None):
        from devparrot.core.commandLauncher import add_command
        self.wrapper._set_function(function)
        add_command(function.__name__, self.wrapper, section)
        return function
