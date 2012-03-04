# -*- coding: utf-8 -*-
"""
    textHighlight.styles
    ~~~~~~~~~~~~~~~

    Contains built-in styles.

    :copyright: Copyright 2006-2011 by the Pygments team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

from ..util import ClassNotFound


#: Maps style names to 'submodule::classname'.
STYLE_MAP = {
    'default':  'default::DefaultStyle',
    'emacs':    'emacs::EmacsStyle',
    'friendly': 'friendly::FriendlyStyle',
    'colorful': 'colorful::ColorfulStyle',
    'autumn':   'autumn::AutumnStyle',
    'murphy':   'murphy::MurphyStyle',
    'manni':    'manni::ManniStyle',
    'monokai':  'monokai::MonokaiStyle',
    'perldoc':  'perldoc::PerldocStyle',
    'pastie':   'pastie::PastieStyle',
    'borland':  'borland::BorlandStyle',
    'trac':     'trac::TracStyle',
    'native':   'native::NativeStyle',
    'fruity':   'fruity::FruityStyle',
    'bw':       'bw::BlackWhiteStyle',
    'vim':      'vim::VimStyle',
    'vs':       'vs::VisualStudioStyle',
    'tango':    'tango::TangoStyle',
}


def get_style_by_name(name):
	import imp, os
	if name in STYLE_MAP:
		mod, cls = STYLE_MAP[name].split('::')
		builtin = "yes"
	print mod
	
	fp, pathname, desc = imp.find_module( mod, [os.path.dirname(__file__)])
	
	try:
		mod = imp.load_module(mod, fp, pathname, desc)
	finally:
		if fp:
			fp.close()
    	try:
		return getattr(mod, cls)
	except AttributeError:
		raise ClassNotFound("Could not find style class %r in style module." % cls)


def get_all_styles():
    """Return an generator for all styles by name,
    both builtin and plugin."""
    for name in STYLE_MAP:
        yield name


