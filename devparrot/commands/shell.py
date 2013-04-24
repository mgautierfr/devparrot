from devparrot.capi import Command
from devparrot.capi.constraints import Stream

@Command(
stdinput = Stream()
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
        line = "{}\n".format(line)
        inPipe.write(line)
    inPipe.close()

    for line in outPipe:
        yield line

