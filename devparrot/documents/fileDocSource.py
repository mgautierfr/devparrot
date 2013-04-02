#    This file is part of DevParrot.
#
#    Author: Matthieu Gautier <matthieu.gautier@mgautier.fr>
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
#    Copyright 2011 Matthieu Gautier

import os, sys

class FileDocSource(object):
    """This class is used for document comming from a file (most of document)"""
    def __init__(self, path):
        self.path = os.path.abspath(path)
        self.timestamp = None
        
    def __getattr__(self, name):
        if name == "title":
            return os.path.basename(self.path)
        if name == "longTitle":
            return self.path
        raise AttributeError
        
    def __eq__(self, other):
        if self.__class__ == other.__class__:
            return self.path == other.path
        return False
        
    def get_path(self):
        """ return the path of the file """
        return self.path

    def has_path(self):
        """
        return True if the source has a path.
        Always True for fileDocSource
        """
        return True
    
    def get_content(self):
        """
        return the content of the file
        """
        if not os.path.exists(self.path):
            return ""

        text = ""
        try:
            with open(self.path, 'r') as fileIn:
                text = fileIn.read()
            if text and text[-1] == '\n':
                text = text[:-1]
            self.init_timestamp()
        except IOError:
            sys.stderr.write("Error while loading file %s\n"%self.path)
        return text
    
    def init_timestamp(self):
        """ reinit the timestamp saved from the file """
        try:
            self.timestamp = os.stat(self.path).st_mtime
        except OSError:
            pass

    def set_content(self, content):
        """ set the content of the file (save it) """
        try :
            with open(self.path, 'w') as fileOut:
                fileOut.write(content.encode('utf8'))
            self.init_timestamp()
            return True
        except IOError:
            sys.stderr.write("Error while writing file %s\n"%self.path)
            return False
    
    def need_reload(self):
        """return True if the file has been modified since last init_timestamp"""
        if not self.timestamp:
            return False
        try:
            modif = os.stat(self.path).st_mtime
            return  modif > self.timestamp
        except OSError:
            return False


    def is_readonly(self):
        return not os.access(self.path, os.W_OK)
