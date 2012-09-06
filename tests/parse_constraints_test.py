#!/usr/bin/env python

import unittest
import sys

try:
    import _preambule
except ImportError:
    sys.exc_clear()

from devparrot.core.command import constraints

class Constraints_test(unittest.TestCase):
    def setUp(self):
        self.OneConstraint1 = constraints.Keyword(("constraint1", ))
        self.OneOrMoreConstraint1 = constraints.Keyword(("constraint1",), multiple=True)
        self.OptionalConstraint1 = constraints.Keyword(("constraint1",), optional=True)
        self.ZeroOrMoreConstraint1 = constraints.Keyword(("constraint1",), optional=True, multiple=True)
        self.OneConstraint2 = constraints.Keyword(("constraint2", ))
        
        self.tokensList = [
            [],
            [""],
            ["constraint1"],
            ["constraint2"],
            ["constraint1","constraint2"],
            ["constraint2","constraint1"],
            ["constraint1" for i in xrange(3)],
            ["constraint1" for i in xrange(3)]+["constraint2"],
            ["constraint2" for i in xrange(3)],
            ["constraint2"]+["constraint1" for i in xrange(3)],
            ["constraint2"]+["constraint1" for i in xrange(3)]+["constraint2"],
        ]
    
    def test_one_constraint(self):
        tokenParser = constraints.TokenParser([self.OneConstraint1])
        oracle = [
            "raise", #[]
            "raise", #[""]
            ["constraint1"],  #[c1]
            "raise", #[c2]
            "raise", #[c1, c2]
            "raise", #[c2, c1]
            "raise", #[c1, c1, c1]
            "raise", #[c1, c1, c1, c2]
            "raise", #[c2, c2, c2]
            "raise", #[c2, c1, c1, c1]
            "raise", #[c2, c1, c1, c1, c2]
        ]
        
        print "\none_constraint"
        for tokens, oracle in zip(self.tokensList, oracle):
            print "try", tokens, "=>", oracle
            if oracle == "raise":
                self.assertRaises(Exception,tokenParser.parse, (tokens,))
            else:
                self.assertEqual(tokenParser.parse(tokens), oracle)
    
    def test_optional_constraint(self):
        tokenParser = constraints.TokenParser([self.OptionalConstraint1])
        oracle = [
            [None], #[]
            [None], #[""]
            ["constraint1"],  #[c1]
            "raise", #[c2]
            "raise", #[c1, c2]
            "raise", #[c2, c1]
            "raise", #[c1, c1, c1]
            "raise", #[c1, c1, c1, c2]
            "raise", #[c2, c2, c2]
            "raise", #[c2, c1, c1, c1]
            "raise", #[c2, c1, c1, c1, c2]
        ]
        
        print "\noptional_constraint"
        for tokens, oracle in zip(self.tokensList, oracle):
            print "try", tokens, "=>", oracle
            if oracle == "raise":
                self.assertRaises(Exception,tokenParser.parse, (tokens,))
            else:
                self.assertEqual(tokenParser.parse(tokens), oracle)

    def test_oneOrMore_constraint(self):
        tokenParser = constraints.TokenParser([self.OneOrMoreConstraint1])
        oracle = [
            "raise", #[]
            "raise", #[""]
            [["constraint1"]],  #[c1]
            "raise", #[c2]
            "raise", #[c1, c2]
            "raise", #[c2, c1]
            [["constraint1", "constraint1", "constraint1"]], #[c1, c1, c1]
            "raise", #[c1, c1, c1, c2]
            "raise", #[c2, c2, c2]
            "raise", #[c2, c1, c1, c1]
            "raise", #[c2, c1, c1, c1, c2]
        ]
        
        print "\noneOrMore_constraint"
        for tokens, oracle in zip(self.tokensList, oracle):
            print "try", tokens, "=>", oracle
            if oracle == "raise":
                self.assertRaises(Exception,tokenParser.parse, (tokens,))
            else:
                self.assertEqual(tokenParser.parse(tokens), oracle)
        
    def test_zeroOrMore_constraint(self):
        tokenParser = constraints.TokenParser([self.ZeroOrMoreConstraint1])
        oracle = [
            [[]], #[]
            [[None]], #[""]
            [["constraint1"]],  #[c1]
            "raise", #[c2]
            "raise", #[c1, c2]
            "raise", #[c2, c1]
            [["constraint1", "constraint1", "constraint1"]], #[c1, c1, c1]
            "raise", #[c1, c1, c1, c2]
            "raise", #[c2, c2, c2]
            "raise", #[c2, c1, c1, c1]
            "raise", #[c2, c1, c1, c1, c2]
        ]
        
        print "\nzeroOrMore_constraint"
        for tokens, oracle in zip(self.tokensList, oracle):
            print "try", tokens, "=>", oracle
            if oracle == "raise":
                self.assertRaises(Exception,tokenParser.parse, (tokens,))
            else:
                self.assertEqual(tokenParser.parse(tokens), oracle)
    
    def test_two_constraint(self):
        tokenParser = constraints.TokenParser([self.OneConstraint1, self.OneConstraint2])
        oracle = [
            "raise", #[]
            "raise", #[""]
            "raise", #[c1]
            "raise", #[c2]
            ["constraint1", "constraint2"], #[c1, c2]
            "raise", #[c2, c1]
            "raise", #[c1, c1, c1]
            "raise", #[c1, c1, c1, c2]
            "raise", #[c2, c2, c2]
            "raise", #[c2, c1, c1, c1]
            "raise", #[c2, c1, c1, c1, c2]
        ]
        
        print "\ntwo_constraint"
        for tokens, oracle in zip(self.tokensList, oracle):
            print "try", tokens, "=>", oracle
            if oracle == "raise":
                self.assertRaises(Exception,tokenParser.parse, (tokens,))
            else:
                self.assertEqual(tokenParser.parse(tokens), oracle)
    
    def test_two_constraint_inverted(self):
        tokenParser = constraints.TokenParser([self.OneConstraint2, self.OneConstraint1])
        oracle = [
            "raise", #[]
            "raise", #[""]
            "raise", #[c1]
            "raise", #[c2]
            "raise", #[c1, c2]
            ["constraint2", "constraint1"], #[c2, c1]
            "raise", #[c1, c1, c1]
            "raise", #[c1, c1, c1, c2]
            "raise", #[c2, c2, c2]
            "raise", #[c2, c1, c1, c1]
            "raise", #[c2, c1, c1, c1, c2]
        ]
        
        print "\ntwo_constraint_inverted"
        #import pdb; pdb.set_trace()
        for tokens, oracle in zip(self.tokensList, oracle):
            print "try", tokens, "=>", oracle
            if oracle == "raise":
                self.assertRaises(Exception,tokenParser.parse, (tokens,))
            else:
                self.assertEqual(tokenParser.parse(tokens), oracle)
    
    def test_two_constraint_opt(self):
        tokenParser = constraints.TokenParser([self.OptionalConstraint1, self.OneConstraint2])
        oracle = [
            "raise", #[]
            "raise", #[""]
            "raise", #[c1]
            [None, "constraint2"], #[c2]
            ["constraint1","constraint2"], #[c1, c2]
            "raise", #[c2, c1]
            "raise", #[c1, c1, c1]
            "raise", #[c1, c1, c1, c2]
            "raise", #[c2, c2, c2]
            "raise", #[c2, c1, c1, c1]
            "raise", #[c2, c1, c1, c1, c2]
        ]
        
        print "\ntwo_constraint_opt"
        for tokens, oracle in zip(self.tokensList, oracle):
            print "try", tokens, "=>", oracle
            if oracle == "raise":
                self.assertRaises(Exception,tokenParser.parse, (tokens,))
            else:
                self.assertEqual(tokenParser.parse(tokens), oracle)
    
    def test_two_constraint_opt_inverted(self):
        tokenParser = constraints.TokenParser([self.OneConstraint2, self.OptionalConstraint1])
        oracle = [
            "raise", #[]
            "raise", #[""]
            "raise", #[c1]
            ["constraint2", None], #[c2]
            "raise", #[c1, c2]
            ["constraint2", "constraint1"], #[c2, c1]
            "raise", #[c1, c1, c1]
            "raise", #[c1, c1, c1, c2]
            "raise", #[c2, c2, c2]
            "raise", #[c2, c1, c1, c1]
            "raise", #[c2, c1, c1, c1, c2]
        ]
        
        print "\ntwo_constraint_opt_inverted"
        #import pdb; pdb.set_trace()
        for tokens, oracle in zip(self.tokensList, oracle):
            print "try", tokens, "=>", oracle
            if oracle == "raise":
                self.assertRaises(Exception,tokenParser.parse, (tokens,))
            else:
                self.assertEqual(tokenParser.parse(tokens), oracle)
    
    def test_two_constraintlist(self):
        tokenParser = constraints.TokenParser([self.OneConstraint2, self.OneOrMoreConstraint1])
        oracle = [
            "raise", #[]
            "raise", #[""]
            "raise", #[c1]
            "raise", #[c2]
            "raise", #[c1, c2]
            ["constraint2", ["constraint1"]], #[c2, c1]
            "raise", #[c1, c1, c1]
            "raise", #[c1, c1, c1, c2]
            "raise", #[c2, c2, c2]
            ["constraint2", ["constraint1", "constraint1", "constraint1"]], #[c2, c1, c1, c1]
            "raise", #[c2, c1, c1, c1, c2]
        ]
        
        print "\ntwo_constraintlist"
        for tokens, oracle in zip(self.tokensList, oracle):
            print "try", tokens, "=>", oracle
            if oracle == "raise":
                self.assertRaises(Exception,tokenParser.parse, (tokens,))
            else:
                self.assertEqual(tokenParser.parse(tokens), oracle)
    
    def test_two_constraintlist1(self):
        tokenParser = constraints.TokenParser([self.OneConstraint2, self.ZeroOrMoreConstraint1])
        oracle = [
            "raise", #[]
            "raise", #[""]
            "raise", #[c1]
            ["constraint2", []], #[c2]
            "raise", #[c1, c2]
            ["constraint2", ["constraint1"]], #[c2, c1]
            "raise", #[c1, c1, c1]
            "raise", #[c1, c1, c1, c2]
            "raise", #[c2, c2, c2]
            ["constraint2", ["constraint1","constraint1","constraint1"]], #[c2, c1, c1, c1]
            "raise", #[c2, c1, c1, c1, c2]
        ]
        
        print "\ntwo_constraintlist1"
        for tokens, oracle in zip(self.tokensList, oracle):
            print "try", tokens, "=>", oracle
            if oracle == "raise":
                self.assertRaises(Exception,tokenParser.parse, (tokens,))
            else:
                self.assertEqual(tokenParser.parse(tokens), oracle)
    
    def test_two_optional(self):
        tokenParser = constraints.TokenParser([self.OptionalConstraint1,constraints.Keyword(("constraint1",), optional=True)])
        tokensList = [
            [],
            [""],
            ["", ""],
            ["constraint1", "constraint1"],
            ["constraint1", ""],
            ["", "constraint1"],
            ["constraint2"],
            ["constraint2", "constraint1"],
            ["constraint1", "constraint2"],
            ["constraint2", ""],
            ["", "constraint2"]
        ]
        oracle = [
            [None, None], #[]
            [None, None], #[""]
            [None, None], #[c1]
            ["constraint1", "constraint1"], #[c2]
            ["constraint1", None],
            [None, "constraint1"],
            "raise", #[c1, c2]
            "raise",
            "raise", #[c1, c1, c1]
            "raise", #[c1, c1, c1, c2]
            "raise"
        ]
        
        print "\ntwo_constraintlist1"
        for tokens, oracle in zip(tokensList, oracle):
            print "try", tokens, "=>", oracle
            if oracle == "raise":
                self.assertRaises(Exception,tokenParser.parse, (tokens,))
            else:
                self.assertEqual(tokenParser.parse(tokens), oracle)
    
    def test_splitted_list(self):
        tokenParser = constraints.TokenParser([self.OneOrMoreConstraint1,self.OneConstraint2, self.OneOrMoreConstraint1])
        tokensList = [
            [],
            [""],
            ["", ""],
            ["constraint1", "constraint1"],
            ["constraint1", "constraint2"],
            ["constraint1", "constraint1", "constraint2"],
            ["constraint1", "constraint1", "constraint2", "constraint1"],
            ["constraint2", "constraint1"]
        ]
        oracle = [
            "raise", #[]
            "raise", #[""]
            "raise", #[c1]
            "raise",
            [["constraint1"], "constraint2", ["constraint1"]],
            [["constraint1", "constraint1"], "constraint2", ["constraint1", "constraint1"]],
            "raise",
            "raise"
        ]
        
        print "\ntwo_constraintlist1"
        for tokens, oracle in zip(tokensList, oracle):
            print "try", tokens, "=>", oracle
            if oracle == "raise":
                self.assertRaises(Exception,tokenParser.parse, (tokens,))
            else:
                self.assertEqual(tokenParser.parse(tokens), oracle)

if __name__ == "__main__":
    unittest.main()
