from devparrot.core.command import Command, Macro, Alias
from devparrot.core import session, constraints

@Command()
def assert_file_equal(file1, file2):
    assert open(file1, 'rb').read() == open(file2, 'rb').read()

@Command(
number = constraints.Integer())
def assert_nb_document(number):
    assert number == session.get_documentManager().get_nbDocuments()

@Command(
number = constraints.Default(multiple=True))
def assert_document_names(*names):
    assert len(names) == session.get_documentManager().get_nbDocuments()
    for name in names:
        session.get_documentManager().get_file_from_title(name)

@Command()
def assert_equal(v1, v2):
    assert v1 == v2

@Command(
s=constraints.Stream(),
v=constraints.Default(multiple=True)
)
def assert_stream_equal(s, v):
    s = list(s)
    v = list(v)
    print('s = ', s)
    print('v = ', v)
    assert s == v

@Macro()
def ast_eval(value):
    import ast
    try:
        return ast.literal_eval(value)
    except ValueError:
        return value

@Macro()
def range_(text):
    from devparrot.core.constraints import Range
    ok, result = Range().check(text)

    if ok:
        return result
    raise InvalidArgument()
