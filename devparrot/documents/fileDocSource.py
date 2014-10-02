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


import os, sys, magic, re

from xdg import Mime
import codecs
from contextlib import contextmanager
from devparrot.core import session
import subprocess

coding_re = re.compile(r"coding[:=]\s*([-\w.]+)")
charset_ret = re.compile(r"charset=([-\w.]+)")


class FileDocSource(object):
    """This class is used for document comming from a file (most of document)"""
    def __init__(self, path, guess_encoding=True):
        self.path = os.path.abspath(path)
        self.timestamp = None

        self.mimetype = Mime.get_type_by_name(self.path)
        if not self.mimetype:
            try:
                self.mimetype = Mime.lookup(*magic.from_file(self.path, mime=True).split("/"))
            except IOError:
                self.mimetype = Mime.lookup("text", "plain")

        self._encoding = None
        if guess_encoding:
            try:
                self.guess_encoding()
            except IOError:
                pass

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

    @property
    def encoding(self):
        return self._encoding or session.config.encoding.get([self.mimetype])

    def guess_encoding(self):
        i = 0
        with open(self.path, 'r') as fileIn:
            for line in fileIn:
                if i < 5:
                    encoding = coding_re.search(line)
                    if encoding:
                        self._encoding = encoding.group(1)
                        return
                    i += 1
                else:
                    break
        output = subprocess.check_output(["file", "-i", self.path])
        encoding = charset_ret.search(output)
        if "x-empty" in output:
            encoding = None
        else:
            encoding = charset_ret.search(output)
        if encoding:
            self._encoding = encoding.group(1)
        if self._encoding == "ascii":
            self._encoding = None

    @contextmanager
    def get_content(self):
        """
        return the content of the file
        """
        if not os.path.exists(self.path):
            yield [u""]
        else:
            with codecs.open(self.path, 'r', self.encoding) as fileIn:
                yield fileIn
            self.init_timestamp()
    
    def init_timestamp(self):
        """ reinit the timestamp saved from the file """
        try:
            self.timestamp = os.stat(self.path).st_mtime
        except OSError:
            pass

    def set_content(self, content):
        """ set the content of the file (save it) """
        with codecs.open(self.path, 'w', self.encoding) as fileOut:
            fileOut.write(content)
        self.init_timestamp()
    
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
        if not os.path.exists(self.path):
            return False
        return not os.access(self.path, os.W_OK)
