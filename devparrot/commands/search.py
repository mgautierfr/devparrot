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


@Alias(
    searchText = constraints.Default(default=lambda : lastSearch),
    backward = constraints.Boolean(default=lambda :False)
)
def search(searchText, backward):
    """search for searchText in currentDocument
    """
    searchChar = "?" if backward else "/"

    global lastSearch
    lastSearch = searchText

    commands = [
        "tag clean search_tag",
        "capi.search {0!r} | tag set search_tag".format(searchText),
        "goto {0}'{1}'".format(searchChar,searchText.replace("'", "\\'"))
    ]

    return "\n".join(commands)

@Alias()
def bsearch(searchText):
    return "search {0!r} backward=True".format(searchText)

bindings["<F3>"] = "search\n"
bindings["<Alt-F3>"] = "search backward=True\n"
bindings["<Control-f>"] = "search "
