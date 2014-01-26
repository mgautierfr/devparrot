

import pytest
from devparrot.models.sourceBuffer import LineInfo, ModelInfo
from devparrot.core.utils.posrange import Index, Start
import itertools


test_content = "\n".join(
" "*i for i in itertools.chain(xrange(5, 10), xrange(10, 5, -1))
)

def test_initial_insert_one_line():
    model = ModelInfo()
    model.insert(Start, " "*5)
    assert model.nbLine == 1
    assert [li.len for li in model.lineInfos[1:]] == [5]



def test_initial_insert():
    model = ModelInfo()
    model.insert(Start, test_content)
    assert model.nbLine == 10
    print [li.len for li in model.lineInfos[1:]]
    assert [li.len for li in model.lineInfos[1:]] == [5, 6, 7, 8, 9, 10, 9, 8, 7, 6]

@pytest.mark.parametrize(("index","content","nbLine","lineLens"), [
(Index(2,0), " "*5, 3, [5, 10, 5]),

(Index(2,0), "\n",  4, [5, 0, 5, 5]),
(Index(2,3), "\n",  4, [5, 3, 2, 5]),
(Index(2,5), "\n",  4, [5, 5, 0, 5]),

(Index(2,0), "\n".join([" "*5]*2),  4, [5, 5, 10, 5]),
(Index(2,3), "\n".join([" "*5]*2),  4, [5, 8, 7, 5]),
(Index(2,5), "\n".join([" "*5]*2),  4, [5, 10, 5, 5]),

(Index(2,0), " "*5+"\n"*2+" "*5,  5, [5, 5, 0, 10, 5]),
(Index(2,3), " "*5+"\n"*2+" "*5,  5, [5, 8, 0, 7, 5]),
(Index(2,5), " "*5+"\n"*2+" "*5,  5, [5, 10, 0, 5, 5]),
])
def test_insert_content(index, content, nbLine, lineLens):
    model = ModelInfo()
    model.nbLine = 3
    model.lineInfos = [None] + [LineInfo(5) for i in xrange(3)]

    model.insert(index, content)

    assert model.nbLine == nbLine
    assert [li.len for li in model.lineInfos[1:]] == lineLens




@pytest.mark.parametrize(("index1","index2","nbLine","lineLens"), [
(Index(1, 0), Index(1,1), 10, [4, 6, 7, 8, 9, 10, 9, 8, 7, 6]),
(Index(1, 0), Index(1,5), 10, [0, 6, 7, 8, 9, 10, 9, 8, 7, 6]),
(Index(1, 0), Index(2,0), 9,  [   6, 7, 8, 9, 10, 9, 8, 7, 6]),
(Index(2, 0), Index(2,0), 10, [5, 6, 7, 8, 9, 10, 9, 8, 7, 6]),
(Index(2, 0), Index(9,0), 3,  [5,                       7, 6]),
(Index(1, 0), Index(9,0), 2,  [                         7, 6]),
(Index(2, 6), Index(3,0), 9,  [5, 13,   8, 9, 10, 9, 8, 7, 6]),
(Index(2, 6), Index(4,0), 8,  [5, 14,      9, 10, 9, 8, 7, 6]),
(Start,       Index(10, 6), 1,[0])

])
def test_remove_content(index1, index2, nbLine, lineLens):
    model = ModelInfo()
    model.nbLine = 10
    model.lineInfos = [None] + [LineInfo(i) for i in itertools.chain(xrange(5, 10), xrange(10, 5, -1))]

    model.delete(index1, index2)

    assert model.nbLine == nbLine
    assert [li.len for li in model.lineInfos[1:]] == lineLens



@pytest.mark.parametrize(("index", "nbLine", "expected"), [
(Start, 0, Start),
(Index(1,0), 1, Index(2, 0)),
(Index(1,0), 2, Index(3, 0)),
(Index(1,5), 2, Index(3, 5)),
(Index(6,9), 3, Index(9, 7)),
(Index(6,9), 10, Index(11, 0)),
(Index(6,9), -4, Index(2, 6)),
])
def test_addline(index, nbLine, expected):
    model = ModelInfo()
    model.nbLine = 10
    model.lineInfos = [None] + [LineInfo(i) for i in itertools.chain(xrange(5, 10), xrange(10, 5, -1))]

    assert model.addline(index, nbLine) == expected

@pytest.mark.parametrize(("index", "nbLine", "expected"), [
(Start, 0, Start),
(Index(1,0), 1, Index(1, 0)),
(Index(4,0), 1, Index(3, 0)),
(Index(4,0), 2, Index(2, 0)),
(Index(4,3), 2, Index(2, 3)),
(Index(4,8), 2, Index(2, 6)),
(Index(6,9), 10, Index(1, 5)),
])
def test_delline(index, nbLine, expected):
    model = ModelInfo()
    model.nbLine = 10
    model.lineInfos = [None] + [LineInfo(i) for i in itertools.chain(xrange(5, 10), xrange(10, 5, -1))]

    assert model.delline(index, nbLine) == expected

@pytest.mark.parametrize(("index", "nbChar", "expected"), [
(Start, 0, Start),
(Start, 100, Index(11, 0)),
(Index(1,0), 1, Index(1, 1)),
(Index(1,0), 5, Index(1, 5)),
(Index(1,5), 1, Index(2, 0)),
(Index(1,0), 6, Index(2, 0)),
(Index(1,2), 5, Index(2, 1)),
(Index(10,0), 6, Index(10, 6)),
(Index(10,0), 10, Index(11, 0)),
(Index(10,6), 1, Index(11, 0)),
(Index(10,6), 0, Index(10, 6)),
])
def test_addchar(index, nbChar, expected):
    model = ModelInfo()
    model.nbLine = 10
    model.lineInfos = [None] + [LineInfo(i) for i in itertools.chain(xrange(5, 10), xrange(10, 5, -1))]

    assert model.addchar(index, nbChar) == expected


@pytest.mark.parametrize(("index", "nbChar", "expected"), [
(Index(5,0), 0, Index(5, 0)),
(Index(5,0), 1, Index(4, 8)),
(Index(5,1), 1, Index(5, 0)),
(Index(5,9), 9, Index(5, 0)),
(Index(5,9), 10, Index(4, 8)),
(Index(5,9), 11, Index(4, 7)),
(Index(1,0), 1, Index(1, 0)),
(Index(10,0), 100, Index(1, 0)),
(Index(10,6), 1, Index(10, 5)),
(Index(10,6), 0, Index(10, 6)),
])
def test_delchar(index, nbChar, expected):
    model = ModelInfo()
    model.nbLine = 10
    model.lineInfos = [None] + [LineInfo(i) for i in itertools.chain(xrange(5, 10), xrange(10, 5, -1))]

    assert model.delchar(index, nbChar) == expected

