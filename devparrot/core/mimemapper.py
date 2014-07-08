from pygments.lexers import get_all_lexers

mimeMap = { mime:name for name, alias, regexes, mimes in get_all_lexers() for mime in mimes}

