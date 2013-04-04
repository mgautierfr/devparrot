from devparrot.core.command.baseCommand import Command
from devparrot.core.command import constraints, binder
from devparrot.core import capi
from devparrot.core.utils.posrange import Index

@Command(
stdinput = constraints.Stream()
)
def shell(command, stdinput, *args):
    """
    run a external command
    """
    from subprocess import Popen, PIPE
    commands = [command]+list(args)
    popen = Popen([command]+list(args), bufsize=0, shell=False, stdin=PIPE, stdout=PIPE, universal_newlines=True)
    outPipe = popen.stdout
    inPipe = popen.stdin

    for line in stdinput:
        line = "%s\n"%line
        inPipe.write(line)
    inPipe.close()

    for line in outPipe:
        yield line

