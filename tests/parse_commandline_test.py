
import pytest

from devparrot.core.command.parserGrammar import parse_input_text as parser

from devparrot.core.command.tokens import *

to_test = {
            "token"                                            : Pipe(index=0,
                                                                      len=5,
                                                                      values=[CommandCall(index=0,
                                                                                          len=5,
                                                                                          name="token",
                                                                                          closed=False,
                                                                                          values=[])]
                                                                     ),
            "token "                                           : Pipe(index=0,
                                                                      len=6,
                                                                      values=[CommandCall(index=0,
                                                                                          len=6,
                                                                                          name="token",
                                                                                          closed=False,
                                                                                          values=[New(index=6)])]
                                                                     ),
             "function arg1"                                   : Pipe(index=0,
                                                                      len=13,
                                                                      values=[CommandCall(index=0,
                                                                                          len=13,
                                                                                          name="function",
                                                                                          closed=False,
                                                                                          values=[UnquotedString(index=9,
                                                                                                                 len=4,
                                                                                                                 values="arg1",
                                                                                                                 closed=False)
                                                                                                 ])]
                                                                     ),
              "function 'arg1'"                                : Pipe(index=0,
                                                                      len=15,
                                                                      values=[CommandCall(index=0,
                                                                                          len=15,
                                                                                          name="function",
                                                                                          closed=False,
                                                                                          values=[SimpleString(index=9,
                                                                                                               len=6,
                                                                                                               values="arg1",
                                                                                                               closed=True)
                                                                                                 ])]
                                                                     ),
               'function "arg1"'                               : Pipe(index=0,
                                                                      len=15,
                                                                      values=[CommandCall(index=0,
                                                                                          len=15,
                                                                                          name="function",
                                                                                          closed=False,
                                                                                          values=[DoubleString(index=9, len=6, values="arg1", closed=True)],
                                                                                         )]
                                                                     ),
                "function 'arg1":                                Pipe(index=0,
                                                                      len=14,
                                                                      values=[CommandCall(index=0,
                                                                                          len=14,
                                                                                          name="function",
                                                                                          values=[SimpleString(index=9, len=5, values="arg1", closed=False)],
                                                                                          closed=False)]
                                                                     ),
                "function arg1 "                               : Pipe(index=0,
                                                                      len=14,
                                                                      values=[CommandCall(index=0,
                                                                                          len=14,
                                                                                          name="function",
                                                                                          values=[UnquotedString(index=9, len=4, values="arg1", closed=True),
                                                                                                  New(index=14)],
                                                                                          closed=False)]
                                                                     ),
                "function arg1 'arg2'"                         : Pipe(index=0,
                                                                      len=20,
                                                                      values=[CommandCall(index=0,
                                                                                          len=20,
                                                                                          name="function",
                                                                                          closed=False,
                                                                                          values=[UnquotedString(index=9, len=4, values="arg1", closed=True),
                                                                                                  SimpleString(index=14, len=6, values="arg2", closed=True)
                                                                                                 ]
                                                                                          )
                                                                             ]
                                                                     ),
                 "function [arg1 'arg2']"                      : Pipe(index=0,
                                                                      len=22,
                                                                      values=[CommandCall(index=0,
                                                                                          len=22,
                                                                                          name="function",
                                                                                          closed=False,
                                                                                          values=[List(index=9, len=13, closed=True,
                                                                                                       values=[UnquotedString(index=10, len=4, values="arg1", closed=True),
                                                                                                               SimpleString(index=15, len=6, values="arg2", closed=True)
                                                                                                              ]
                                                                                                      )
                                                                                                 ]
                                                                                          )
                                                                             ]
                                                                     ),
                "function [arg1 'arg2'"                        : Pipe(index=0,
                                                                      len=21,
                                                                      values=[CommandCall(index=0,
                                                                                          len=21,
                                                                                          name="function",
                                                                                          closed=False,
                                                                                          values=[List(index=9, len=12, closed=False,
                                                                                                       values=[UnquotedString(index=10, len=4, values="arg1", closed=True),
                                                                                                               SimpleString(index=15, len=6, values="arg2", closed=True)
                                                                                                              ]
                                                                                                      )
                                                                                                 ]
                                                                                          )
                                                                             ]
                                                                     ),
                    "function []"                              : Pipe(index=0,
                                                                      len=11,
                                                                      values=[CommandCall(index=0,
                                                                                          len=11,
                                                                                          name="function",
                                                                                          closed=False,
                                                                                          values=[List(index=9, len=2, closed=True, values=[]) ]
                                                                                          )
                                                                             ]
                                                                     ),
                    "function ["                               : Pipe(index=0,
                                                                      len=10,
                                                                      values=[CommandCall(index=0,
                                                                                          len=10,
                                                                                          name="function",
                                                                                          closed=False,
                                                                                          values=[List(index=9, len=1, closed=False, values=[]) ]
                                                                                          )
                                                                             ]
                                                                     ),
                    "function key=value"                       : Pipe(index=0,
                                                                      len=18,
                                                                      values=[CommandCall(index=0,
                                                                                          len=18,
                                                                                          name="function",
                                                                                          closed=False,
                                                                                          values=[KeywordArg(index=9, len=9,
                                                                                                             name=Identifier(index=9, len=3, name="key"),
                                                                                                             value=UnquotedString(index=13, len=5, values="value", closed=False)
                                                                                                            )
                                                                                                 ]
                                                                                          )
                                                                             ]
                                                                     ),
                    "function key='value'"                     : Pipe(index=0,
                                                                      len=20,
                                                                      values=[CommandCall(index=0,
                                                                                          len=20,
                                                                                          name="function",
                                                                                          closed=False,
                                                                                          values=[KeywordArg(index=9, len=11,
                                                                                                             name=Identifier(index=9, len=3, name="key"),
                                                                                                             value=SimpleString(index=13, len=7, values="value", closed=True)
                                                                                                            )
                                                                                                 ]
                                                                                          )
                                                                             ]
                                                                     ),
                    "function key1=value1 key2=value2"         : Pipe(index=0,
                                                                      len=32,
                                                                      values=[CommandCall(index=0,
                                                                                          len=32,
                                                                                          name="function",
                                                                                          closed=False,
                                                                                          values=[KeywordArg(index=9, len=11,
                                                                                                             name=Identifier(index=9, len=4, name="key1"),
                                                                                                             value=UnquotedString(index=14, len=6, values="value1", closed=True)
                                                                                                            ),
                                                                                                  KeywordArg(index=21, len=11,
                                                                                                             name=Identifier(index=21, len=4, name="key2"),
                                                                                                             value=UnquotedString(index=26, len=6, values="value2", closed=False)
                                                                                                            )
                                                                                                 ]
                                                                                          )
                                                                             ]
                                                                     ),
                    "function arg key=value"                   : Pipe(index=0,
                                                                      len=22,
                                                                      values=[CommandCall(index=0,
                                                                                          len=22,
                                                                                          name="function",
                                                                                          closed=False,
                                                                                          values=[UnquotedString(index=9, len=3, values="arg", closed=True),
                                                                                                  KeywordArg(index=13, len=9,
                                                                                                             name=Identifier(index=13, len=3, name="key"),
                                                                                                             value=UnquotedString(index=17, len=5, values="value", closed=False)
                                                                                                            )
                                                                                                 ]
                                                                                          )
                                                                             ]
                                                                     ),
                     "function arg1 arg2 key=value"            : Pipe(index=0,
                                                                      len=28,
                                                                      values=[CommandCall(index=0,
                                                                                          len=28,
                                                                                          name="function",
                                                                                          closed=False,
                                                                                          values=[UnquotedString(index=9, len=4, values="arg1", closed=True),
                                                                                                  UnquotedString(index=14, len=4, values="arg2", closed=True),
                                                                                                  KeywordArg(index=19, len=9,
                                                                                                             name=Identifier(index=19, len=3, name="key"),
                                                                                                             value=UnquotedString(index=23, len=5, values="value", closed=False)
                                                                                                            )
                                                                                                 ]
                                                                                          )
                                                                             ]
                                                                     ),
                     "function arg1 arg2 key1=value1 key2=value2" : Pipe(index=0,
                                                                      len=42,
                                                                      values=[CommandCall(index=0,
                                                                                          len=42,
                                                                                          name="function",
                                                                                          closed=False,
                                                                                          values=[UnquotedString(index=9, len=4, values="arg1", closed=True),
                                                                                                  UnquotedString(index=14, len=4, values="arg2", closed=True),
                                                                                                  KeywordArg(index=19, len=11,
                                                                                                             name=Identifier(index=19, len=4, name="key1"),
                                                                                                             value=UnquotedString(index=24, len=6, values="value1", closed=True)
                                                                                                            ),
                                                                                                  KeywordArg(index=31, len=11,
                                                                                                             name=Identifier(index=31, len=4, name="key2"),
                                                                                                             value=UnquotedString(index=36, len=6, values="value2", closed=False)
                                                                                                            )
                                                                                                 ]
                                                                                          )
                                                                             ]
                                                                     ),
                      "function1 | function2"                  : Pipe(index=0,
                                                                      len=21,
                                                                      values=[CommandCall(index=0,
                                                                                          len=10,
                                                                                          name="function1",
                                                                                          closed=True,
                                                                                          values=[]
                                                                                          ),
                                                                              CommandCall(index=12, len=9, name="function2", closed=False, values=[])
                                                                             ]
                                                                     ),
                      "function1 arg| function2"               : Pipe(index=0,
                                                                      len=24,
                                                                      values=[CommandCall(index=0,
                                                                                          len=13,
                                                                                          name="function1",
                                                                                          closed=True,
                                                                                          values=[UnquotedString(index=10, len=3, closed=True, values="arg")]
                                                                                          ),
                                                                              CommandCall(index=15, len=9, name="function2", closed=False, values=[])
                                                                             ]
                                                                     ),
                      "function1 arg \n function2"             : Pipe(index=0,
                                                                      len=25,
                                                                      values=[CommandCall(index=0,
                                                                                          len=14,
                                                                                          name="function1",
                                                                                          closed=True,
                                                                                          values=[UnquotedString(index=10, len=3, closed=True, values="arg")]
                                                                                          ),
                                                                              "\n",
                                                                              CommandCall(index=16, len=9, name="function2", closed=False, values=[])
                                                                             ]
                                                                     )
          }

@pytest.fixture(params=to_test.keys())
def string_to_test(request):
    return request.param

def test_parse_tokens(string_to_test):
    parsed = parser(string_to_test, forCompletion=False)
    parsed.pprint("")
    assert parsed == to_test[string_to_test]
