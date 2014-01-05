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
    from subprocess import Popen, PIPE, STDOUT
    import pty, os, select
    master_fd, slave_fd = pty.openpty()
    commands = [command]+['"%s"'%arg for arg in args]
    commands = ' '.join(commands)
    popen = Popen(commands, bufsize=1024, shell=True, stdin=slave_fd, stdout=slave_fd, stderr=STDOUT, universal_newlines=False, close_fds=True)

    for line in stdinput:
        line = "{}\n".format(line)
        os.write(master_fd, line)


    left = ""
    closed = False
    while True:
        # master_fd will not be closed by itself.
        # If we try to read on it, it may (will) hang if subprocess has terminate.
        # So we need to read only if there is data.
        # We don't check subprocess termination first to avoid race condition when process terminate between the poll and the read.
        ready, _, _ = select.select([master_fd], [], [], 0.1)
        while ready:
            string = left + os.read(master_fd, 1024)
            string = string.replace("\r\n", "\n")
            string = string.replace("\r", "\n")
            lines = string.split('\n')
            for line in lines[:-1]:
                yield line+'\n'
            left = lines[-1]
            ready, _, _ = select.select([master_fd], [], [], 0.1)
        if closed:
            break
        elif popen.poll() is not None:
            # Do not handle return code
            closed = True

    os.close(slave_fd)
    os.close(master_fd)

    if left:
        yield left
