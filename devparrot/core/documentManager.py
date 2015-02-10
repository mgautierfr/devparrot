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

import os

def get_path_end(path, level):
    parts = []
    for i in range(level):
        if not path:
            raise IndexError
        path, tail = os.path.split(path)
        parts.append(tail)
    return os.path.join(*parts[::-1])

def generate_titles(documents):
    from devparrot.documents import FileDocSource
    documents = {d:None for d in documents}
    # get names for buffer and new documents
    for document, infos in documents.items():
        if isinstance(document.documentSource, FileDocSource):
            continue
        documents[document] = document.documentSource.name

    # generate uniq name for file documents
    level = 1
    while True:
        documents_to_test = (d for d, t in documents.items() if t is None)
        documents_to_test = sorted(documents_to_test, key=lambda d:len(d.get_path()), reverse=True)

        if not documents_to_test:
            break

        dtitles = {}
        for document in documents_to_test:
            t = get_path_end(document.get_path(), level)
            dtitles.setdefault(t, []).append(document)

        knowns_titles = set(t for d,t in documents.items() if t)
        for t, ds in dtitles.items():
            if len(ds) > 1:
                continue
            if t in knowns_titles:
                continue
            documents[ds[0]] = t

        level += 1
    return documents

class DocumentManager:
    def __init__(self):
        self.documents = dict()
    
    def get_nbDocuments(self):
        return len(self.documents)

    def has_file(self, path):
        try :
            self.get_file(path)
            return True
        except KeyError:
            return False

    def get_file(self, path):
        try:
            return next(doc for doc in self.documents.values() if doc.get_path()==path)
        except StopIteration:
            raise KeyError

    def get_file_from_title(self, title):
        return self.documents[title]

    def del_file(self, document):
        from . import session
        del self.documents[document.title]
        titles = generate_titles(list(self.documents.values()))
        for t, d in self.documents.items():
            if titles[d] == t:
                continue
            else:
                del self.documents[t]
                self.documents[titles[d]] = d
                d.title = titles[d]
        session.eventSystem.event('documentDeleted')(document)
        return True

    def add_file(self, document):
        from . import session
        titles = generate_titles(list(self.documents.values())+[document])
        for t, d in self.documents.items():
            if titles[d] == t:
                continue
            else:
                del self.documents[t]
                self.documents[titles[d]] = d
                d.title = titles[d]
        self.documents[titles[document]] = document
        document.title = titles[document]
        session.eventSystem.event('documentAdded')(document)
    
    def __str__(self):
        return "Open Files\n[\n%(openfiles)s\n]" % {
            'openfiles' : "\n".join([str(doc) for doc in self.documents])
        }

    def __iter__(self):
        return iter(self.documents.values())

