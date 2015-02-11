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


from devparrot.core.command import Command, Alias, Macro
from devparrot.core.constraints import Boolean, Default, Range
from devparrot.core.session import bindings

from itertools import dropwhile, takewhile

lastSearch = None

@Command(_section='core',
         where = Range(default=Range.DEFAULT('all'))
        )
@Macro(where = Range(default=Range.DEFAULT('all')))
def search(searchText, where):
    document, where = where
    if not searchText:
        return []

    return [(document, r) for r in document.model.search(searchText, where.first, where.last)]


@Command(
    searchText = Default(default=lambda : lastSearch),
    where = Range(default=Range.DEFAULT('all')),
    backward = Boolean(default=lambda :False)
)
def search(searchText, where, backward):
    """search for searchText in document
    """
    from devparrot.core import session
    searchChar = "?" if backward else "/"
    document, where = where

    global lastSearch
    lastSearch = searchText

    session.commands.tag.subCommands['clean']('search_tag', document)
    searches_results = list(document.model.search(searchText, where.first, where.last))
    if searches_results:
        document.model.tag_add('search_tag', *(item for tag in searches_results for item in tag))

        insert = document.model.index('insert')

        if backward:
            try:
                next_to_go = list(takewhile(lambda x: x[0] < insert, searches_results))[-1]
            except IndexError:
                next_to_go = searches_results[-1]
        else:
            try:
                next_to_go = next(dropwhile(lambda x: x[0] <= insert, searches_results))
            except StopIteration:
                next_to_go = searches_results[0]

        session.commands.goto((document, next_to_go[0]))

@Alias()
def bsearch(searchText):
    return "search {0!r} backward=True".format(searchText)

bindings["<F3>"] = "search\n"
bindings["<Alt-F3>"] = "search backward=True\n"
bindings["<Control-f>"] = "search "
