

import pytest
from devparrot.core.constraints.index import *
import itertools

markSet = {"markName", "markName2"}
tagSet  = {"tagName" , "tagName2" }

@pytest.mark.parametrize(("input", "output"), [	
# mark
(""                           , Mark("insert")                                                 ),
("i"                          , Mark("insert")                                                 ),
("insert"                     , Mark("insert")                                                 ),
("c"                          , Mark("current")                                                ),
("current"                    , Mark("current")                                                ),
("start"                      , Mark("start")                                                  ),
("end"                        , Mark("end")                                                    ),
("markName"                   , Mark("markName")                                               ),

#Index modifier
("i+1c"                       , CharDelta(Mark("insert"), 1)                                   ),
("insert-1c"                 , CharDelta(Mark("insert"), -1)                                  ),
("current+1l"                , LineDelta(Mark("current"), 1)                                  ),
("end-10l"                 , LineDelta(Mark("end"), -10)                                    ),
("start~we"                   , WordEnd(Mark("start"))                                         ),
("markName~ws"                , WordStart(Mark("markName"))                                    ),
("markName~le"                , LineEnd(Mark("markName"))                                      ),
("markName~ls"                , LineStart(Mark("markName"))                                    ),

#range to index
("tagName.0"                  , RangePos(Tag("tagName"), 0)                                    ),
("tagName.first"              , RangePos(Tag("tagName"), "first")                              ),
("tagName.last"                , RangePos(Tag("tagName"), "last")                                ),
("tagName.-1"                 , RangePos(Tag("tagName"), -1)                                   ),
("1.0"                        , RangePos(Line(1), 0)                                           ),
("10.10"                      , RangePos(Line(10), 10)                                         ),
("10.-5"                      , RangePos(Line(10), -5)                                         ),
("10.last"                     , RangePos(Line(10), "last")                                      ),

# "index modifier" apply by default to insert
("+1c"                        , CharDelta(Mark("insert"), 1)                                   ),
("-10l"                       , LineDelta(Mark("insert") , -10)                                ),
("~we"                        , WordEnd(Mark("insert"))                                        ),

#this can be composed

])
def test_parse_index(input, output):
    parsed = parse_something(input, markSet, tagSet)
    print(parsed)
    print(output)
    assert parsed == output


@pytest.mark.parametrize(("input", "output"), [	
# range
("s"                          , Tag("sel")                                               ),
("sel"                        , Tag("sel")                                               ),
("selection"                  , Tag("sel")                                               ),
("all"                        , Tag("all")                                                     ),
("tagName"                    , Tag("tagName")                                                 ),
("1"                          , Line(1)                                                        ),
("10"                         , Line(10)                                                       ),

#index to range
("markName?'regex'"            , RegexRange(Mark("markName"), False, "regex")                    ),
("markName/'regex'"            , RegexRange(Mark("markName"), True, "regex")                   ),
("markName:markName2"         , StartEndRange(Mark("markName"), Mark("markName2"))                     ),
("markName:line"              , Line(Mark("markName"))                                         ),
("markName:word"              , Word(Mark("markName"))                                         ),

## "index to range" apply by default to insert
("?'regex'"                    , RegexRange(Mark("insert"), False, "regex")     ),
(":markName"                  , StartEndRange(Mark("insert"), Mark("markName"))         ),
(":word"                      , Word(Mark("insert"))                            ),
("i:i"                        , StartEndRange(Mark("insert"), Mark("insert"))           ),
("i:"                        , StartEndRange(Mark("insert"), Mark("insert"))           ),
(":i"                        , StartEndRange(Mark("insert"), Mark("insert"))           ),
(":"                        , StartEndRange(Mark("insert"), Mark("insert"))           ),

## Range to range
("10+4l"                     , LineDelta(Line(10), 4)                 ),
("1+4c"                      , CharDelta(Line(1), 4)                  ),
("tagName-3l"                , LineDelta(Tag("tagName"), -3)          ),


##this can be composed
("insert:insert+1c"           , StartEndRange(Mark("insert"), CharDelta(Mark("insert"), 1))            ),
("start:sel.first"            , StartEndRange(Mark("start"), RangePos(Tag("sel"), "first"))            ),
("sel.last:i:word.last"         , StartEndRange(RangePos(Tag("sel"), "last"), RangePos(Word(Mark("insert")), "last")) ),
("~ws~ws~ws:~we"                , StartEndRange(WordStart(WordStart(WordStart(Mark("insert")))), WordEnd(WordStart(WordStart(WordStart(Mark("insert")))))) ),
])
def test_parse_range(input, output):
	parsed = parse_something(input, markSet, tagSet)
	print(parsed)
	print(output)
	assert parsed == output

