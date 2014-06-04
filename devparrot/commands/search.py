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


from devparrot.capi import Command, Alias, create_section, get_currentDocument
from devparrot.capi import constraints
from devparrot.core.session import bindings

from itertools import dropwhile, takewhile

lastSearch = None
capi_section = create_section("capi")

class inner:
    @staticmethod
    def search(searchText):
        if not searchText:
            return None

        return get_currentDocument().model.search(searchText)

Command(
    backward = constraints.Boolean(default=lambda : False)
)(inner.search, capi_section)


@Command(
    searchText = constraints.Default(default=lambda : lastSearch),
    backward = constraints.Boolean(default=lambda :False)
)
def search(searchText, backward):
    """search for searchText in currentDocument
    """
    from devparrot.core import session
    searchChar = "?" if backward else "/"

    global lastSearch
    lastSearch = searchText

    session.commands['tag'].subCommands['clean']('search_tag')
    searches_results = list(session.commands['capi']['search'](searchText))
    if searches_results:
        session.commands['tag'].subCommands['set']('search_tag', searches_results)

        document = get_currentDocument()
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

        session.commands['goto']((document, next_to_go[0]))

@Alias()
def bsearch(searchText):
    return "search {0!r} backward=True".format(searchText)

bindings["<F3>"] = "search\n"
bindings["<Alt-F3>"] = "search backward=True\n"
bindings["<Control-f>"] = "search "
