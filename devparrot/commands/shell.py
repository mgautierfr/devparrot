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

