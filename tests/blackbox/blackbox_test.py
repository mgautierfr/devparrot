import pytest

import devparrot
import os
import collections
import imp, gc, logging
from subprocess import check_call, CalledProcessError

def all_valid_rc():
    for top, dirnames, filenames in os.walk(os.path.dirname(__file__)):
        for filename in filenames:
            if filename.endswith('.rc') and not filename.startswith('fail_'):
                yield filename

def all_fail_rc():
    for top, dirnames, filenames in os.walk(os.path.dirname(__file__)):
        for filename in filenames:
            if filename.endswith('.rc') and filename.startswith('fail_'):
                yield filename

@pytest.fixture(params=all_valid_rc())
def valid_script(request):
    currentDir = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(currentDir, request.param)

@pytest.fixture(params=all_fail_rc())
def fail_script(request):
    currentDir = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(currentDir, request.param)

def test_custom_valid_script(tmpdir, valid_script):
    os.chdir(str(tmpdir))
    piper, pipew = os.pipe2(os.O_NONBLOCK|os.O_CLOEXEC)
    env = dict(os.environ)
    env['POSTTEST_FD'] = str(pipew)
    commands_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'commands')
    command = "devparrot --option custom_commands_dir,[\\'"+commands_dir+"\\'] --option fail_on_command_error,True --configrc "+valid_script
    print(command)
    check_call(command, shell=True, cwd=str(tmpdir), pass_fds=(pipew,), env=env)

def test_custom_fail_script(tmpdir, fail_script):
    with pytest.raises(CalledProcessError):
        check_call("devparrot --configrc "+fail_script, shell=True, cwd=str(tmpdir))
