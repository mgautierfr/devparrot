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


import collections

toDisplay = {
'askUser'  : 'will ask to user if not provided',
'default'  : 'optional',
'multiple' : 'must be list',
'isVararg' : 'may be repeated'
}

class ConstraintInstance:
    def __init__(self, constraint, name):
        self.constraint = constraint
        self.name = name

    def __getattr__(self, name):
        attr = getattr(self.constraint, name)
        if isinstance(attr, collections.Callable):
            def f(*args, **kwords):
                return attr(*args, **kwords)
            return f
        return attr

    def __str__(self):
        return '"%s" (of type %s)' % (self.name, self.constraint.__class__.__name__)

    def get_help(self):
        attr_text = ", ".join( (toDisplay[attribute] for attribute in ("default", "askUser", "multiple", "isVararg") if getattr(self.constraint, attribute) ) )
        return [(None, " - %(name)s: ["%{'name':self.name}),
                ("autocmd.help '%s'"%self.constraint.get_helpName(), self.constraint.__class__.__name__),
                (None, "] (%(attr)s)\n     %(userHelp)s"%{'attr':attr_text, 'userHelp':self.constraint.get_userHelp()})
               ]
                
