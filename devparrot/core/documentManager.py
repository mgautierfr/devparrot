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


import utils.event

class DocumentManager(utils.event.EventSource):
    def __init__(self):
        utils.event.EventSource.__init__(self)
        self.documents = set()
        self.signalConnections = {}
    
    def get_nbDocuments(self):
        return len(self.documents)
    
    def get_nthFile(self, index):
        index = int(index)
        try:
            return next(doc for (i, doc) in enumerate(sorted(self.documents)) if i==index)
        except StopIteration:
            raise IndexError

    def has_file(self, path):
        try :
            self.get_file(path)
            return True
        except KeyError:
            return False

    def get_file(self, path):
        try:
            return next(doc for doc in self.documents if doc.get_path()==path)
        except StopIteration:
            raise KeyError

    def get_file_from_title(self, title):
        try:
            return next(doc for doc in self.documents if doc.get_title()==title)
        except StopIteration:
            raise KeyError

    def del_file(self, document):
        self.documents.remove(document)
        self.event('documentDeleted')(document)
        return True

    def add_file(self, document):
        self.documents.add(document)
        self.event('documentAdded')(document)
    
    def __str__(self):
        return "Open Files\n[\n%(openfiles)s\n]" % {
            'openfiles' : "\n".join([str(doc) for doc in self.documents])
        }

    def __iter__(self):
        return iter(self.documents)

