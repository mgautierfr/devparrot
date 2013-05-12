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


from Tkinter import TclError

class ContextError(Exception):
    """This error representes all errors that come from the context.
       It could be :
         - Open a non existant file
         - Open a file the no right to do so.
         - go to a non existant tag

       Those errors are mainly raised by commands or constraints themselves
    """
    pass


class FileAccessError(ContextError):
    """Something got wrong when trying to access a file"""
    def __init__(self, filePath):
        self.filePath = filePath

    def __str__(self):
        return "Can't access to {}".format(self.filePath)


class InvalidError(Exception):
    """This error represents all errors related to invalid input.
       It could be :
         - Invalid syntax
         - Too many (few) arguments
         - Invalid arguments (string instead of int)
         - non existant command name

        Those errors are mainly raised by core devparrot.
    """

class InvalidSyntax(InvalidError):
    """The syntax provided by user is invalid.
       Can't parse.
    """
    pass

class InvalidArgument(InvalidError):
    """Argument are invalid (too many, too few, wrong type)"""
    pass

class InvalidName(InvalidError):
    """User provide an invalid name (as command name)"""
    pass

class NoDefault(Exception):
    pass

class UserCancel(Exception):
    pass

class BadArgument(Exception):
    pass
