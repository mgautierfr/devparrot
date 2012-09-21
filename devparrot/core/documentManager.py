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

import utils.event

class DocumentManager(utils.event.EventSource):
    def __init__(self):
        utils.event.EventSource.__init__(self)
        self.documents = {}
        self.signalConnections = {}
    
    def get_nbDocuments(self):
        return len(self.documents)
    
    def get_nthFile(self, index):
        index = int(index)
        for i, doc in enumerate(sorted(self.documents)):
            if i==index:
                return self.documents[doc]
        return None

    def has_file(self, path):
        return (path in self.documents)

    def get_file(self, path):
        return self.documents[path]

    def del_file(self, document):
        del self.documents[document.get_path()]
        self.event('documentDeleted')(document)
        return True

    def add_file(self, document):
        self.documents[document.get_path()] = document
        self.event('documentAdded')(document)
    
    def __str__(self):
        return "Open Files\n[\n%(openfiles)s\n]"%{
            'openfiles' : "\n".join([str(doc) for (doc) in self])
        }

documentManager = DocumentManager()
