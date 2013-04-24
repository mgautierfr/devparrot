from devparrot.capi import Command, create_section


def empty():
    yield ""


def null():
    raise StopIteration


Command()(empty, create_section("stream"))
Command()(null, create_section("stream"))
