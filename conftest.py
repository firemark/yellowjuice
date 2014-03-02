"""py.test common parts"""
import os
import sys

sys.path.append(os.path.dirname(__file__))
"""Fix for py.test's removal of current directory from sys.path"""


import pytest


@pytest.fixture
def rf(monkeypatch, rf):
    """Add .patch to Django RequestFactory"""
    def rf_patch(self, path, data='', content_type='application/octet-stream',
                 **extra):
        """Prepare PATCH request"""
        return self.generic('PATCH', path, data, content_type, **extra)

    from django.test.client import RequestFactory
    monkeypatch.setattr(RequestFactory, 'patch', rf_patch, raising=False)
    return rf


@pytest.fixture
def client(monkeypatch, rf, client):
    """Add .patch to Django test Client"""
    def client_patch(
            self, path, data='', content_type='application/octet-stream',
            follow=False, **extra):
        """Issue a PATCH request"""
        response = super(Client, self).patch(
            path, data=data, content_type=content_type, **extra)
        if follow:
            response = self._handle_redirects(response, **extra)
        return response

    from django.test.client import Client
    monkeypatch.setattr(Client, 'patch', client_patch, raising=False)
    return client


@pytest.fixture()
def conference(db):
    """A conference."""
    from main.tests.factories import ConferenceFactory
    return ConferenceFactory()


@pytest.fixture()
def user_client(db, client):
    """A Django client logged-in as a new user"""
    from main.tests.factories import UserFactory
    user = UserFactory()
    client.login(username=getattr(user, user.USERNAME_FIELD),
                 password=user.raw_password)
    client.user = user
    return client


# jshint plugin
import pytest
import subprocess


def pytest_addoption(parser):
    parser.addini("jshint_ignore", type="linelist",
                  help="each line specifies a glob pattern for ignored filed")


def pytest_collect_file(parent, path):
    if path.ext == '.js':
        ignored_globs = parent.config.getini('jshint_ignore')
        if any(path.fnmatch(glob) for glob in ignored_globs):
            return
        return JSHintItem(path, parent)


class JSHintItem(pytest.Item, pytest.File):
    """Item running JSHint on a given file"""
    def runtest(self):
        """Run JSHint on current file"""
        # JSHint sends all errors to stdout.
        # Return codes:
        #  0 - all good, no errors
        #  1 - file couldn't be checked
        #  2 - there are problems in code
        process = subprocess.Popen(['jshint', str(self.fspath)],
                                   stdout=subprocess.PIPE)
        output, _ = process.communicate()
        ret_code = process.returncode
        if ret_code:
            raise JSHintError(ret_code, output.decode('utf-8'))

    def repr_failure(self, excinfo):
        if excinfo.errisinstance(JSHintError):
            ret_code, output = excinfo.value.args
            if ret_code == 1:
                return 'Internal error in jshint:\n' + output
            else:
                return output
        return super(JSHintItem, self).repr_failure(excinfo)


class JSHintError(Exception):
    """Error from JSHint. args are return code and output"""
