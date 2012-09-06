#!/usr/bin/env python

import unittest
import sys

try:
    import _preambule
except ImportError:
    sys.exc_clear()


class GrammarTest(unittest.TestCase):
    def setUp(self):
        """launch an instance of devparrot"""
        pass
        
        
    def test_string(self):
        from devparrot.core.command import grammar
        print grammar.string.parseString('hello word')
        print grammar.string.parseString(r'"hello\" word'+"'"+'"'+"'"+'"')
        print grammar.string.parseString(r'hello\ word')
    
    def test_path(self):
        from devparrot.core.command import grammar
        print grammar.path.parseString('/absolute/path')
        print grammar.path.parseString('/absolute/path/dir/')
        print grammar.path.parseString('/absolute/path/file.ext')
        print grammar.path.parseString('relative/path')
        print grammar.path.parseString('relative/path/dir/')
        print grammar.path.parseString('relative/path/file.ext')
        print grammar.path.parseString('./relative/path')
        print grammar.path.parseString('../relative/./path')

if __name__ == "__main__":
    unittest.main()
