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


from devparrot.core.command import Command
from devparrot.core.constraints import Stream, Default, Directory

@Command(
command  = Default(help="The command to launch"),
stdinput = Stream(help="A content to send to the stdinput of the subprocess"),
cwd      = Directory(help="The directory to use as 'current directory'", default=Directory.CURRENT),
args     = Default(help="A list of arguments to use when launching the command")
)
def shell(command, stdinput, cwd, *args):
    """
    run a external command
    """
    from subprocess import Popen, PIPE, STDOUT
    import shlex
    import pty, os, select
    commands = shlex.split(command)
    commands += ['"%s"'%arg for arg in args]
    master_fd, slave_fd = pty.openpty()
    popen = Popen(commands, bufsize=0, stdin=PIPE, stdout=slave_fd, stderr=STDOUT, cwd=cwd, close_fds=True)

    have_data = True
    left = b""
    closed = False
    write_list = [popen.stdin]
    read_list =  [master_fd]
    while True:
        read_ready, write_ready, _ = select.select(read_list, write_list, [], 0.01)
        while read_ready or write_ready:
            if have_data and write_ready:
                try:
                    line = next(stdinput)
                except StopIteration:
                    have_data = False
                    write_list = []
                    popen.stdin.close()
                else:
                    if line is not None:
                        try:
                            popen.stdin.write(line.encode())
                        except Exception as e:
                            raise

            if read_ready:
                string = left + os.read(master_fd, 1024)
                string = string.replace(b"\r\n", b"\n")
                string = string.replace(b"\r", b"\n")
                lines = string.split(b'\n')
                for line in lines[:-1]:
                    yield (line+b'\n').decode()
                left = lines[-1]

            read_ready, write_ready, _ = select.select(read_list, write_list, [], 0.01)
            if popen.poll() is not None:
                read_list = []
        if closed:
            break
        elif popen.poll() is not None:
            # Do not handle return code
            closed = True
        else:
            # we must not be blocking !
            # yield some stuff te let the ui works
            yield None

    os.close(slave_fd)
    os.close(master_fd)

    if left:
        yield left.decode()

@Command(
stream =Stream()
)
def stdoutput(stream):
    """Echo a stream to stdout
    """
    import sys
    for line in stream:
        sys.stdout.write(line.encode())
