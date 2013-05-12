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


class NewDocSource(object):
    """ This class is used for new document """
    newFileNumber = 0
    def __init__(self):
        self.name = "NewFile{}".format(NewDocSource.newFileNumber)
        NewDocSource.newFileNumber += 1
        
    def __getattr__(self, name):
        if name in ["title", "longTitle"]:
            return self.name
        raise AttributeError

    def __eq__(self, other):
        if self.__class__ == other.__class__:
            return self.name == other.name
        return False
        
    def get_path(self):
        return self.title

    def has_path(self):
        """
        return True if the source has a path.
        Always False for newDocSource
        """
        return False
        
    def get_content(self):
        """ return the content of the file """
        return ""
    
    def set_content(self):
        """ set the contente of the file """
        pass

    def need_reload(self):
        """ return True if the file has been modified since last time """
        return False

    def is_readonly(self):
        return False

