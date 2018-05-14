#!/usr/bin/env python3
# Tests for SSH transport class based on PT-security lectures
import pytest

from transports import TransportError, TransportUnknown, \
    TransportConnectionError, SSHtransport, \
    get_defaults, get_transport


def setup_module():
    global SSHdefaults
    SSHdefaults = get_defaults('SSH')


# Check for different get_transport function calls
def test_get_transport_with_args():
    transport_instance = get_transport('SSH', SSHdefaults['host'],
                                       SSHdefaults['port'], SSHdefaults['login'], 
                                       SSHdefaults['password'])
    assert isinstance(transport_instance, SSHtransport)


def test_get_transport_without_args():
    transport_instance = get_transport('SSH')
    assert isinstance(transport_instance, SSHtransport)


def test_get_transport_empty_host():
    with pytest.raises(TransportUnknown):
        get_transport('', SSHdefaults['host'], SSHdefaults['port'],
                      SSHdefaults['login'], SSHdefaults['password'])


# Check for different SSHtransport __init__ call
def test_init_exceptions():
    transport_instance = SSHtransport(SSHdefaults['host'],
                                      SSHdefaults['port'], SSHdefaults['login'], 
                                      SSHdefaults['password'])
    assert isinstance(transport_instance, SSHtransport)


def test_wrong_host():
    with pytest.raises(TransportConnectionError):
        SSHtransport('_unknownhost_', SSHdefaults['port'],
                     SSHdefaults['login'], SSHdefaults['password'])


def test_wrong_port():
    with pytest.raises(TransportConnectionError):
        SSHtransport(SSHdefaults['host'], '_unknownport_',
                     SSHdefaults['login'], SSHdefaults['password'])


def test_wrong_login():
    with pytest.raises(TransportConnectionError):
        SSHtransport(SSHdefaults['host'], SSHdefaults['port'],
                     '_unknownlogin_', SSHdefaults['password'])


def test_wrong_pass():
    with pytest.raises(TransportConnectionError):
        SSHtransport(SSHdefaults['host'], '_unknownport_',
                     SSHdefaults['login'], '_unknownpass_')


# Check for different exec commands from SSHtransport
def test_exec():
    transport_instance = SSHtransport(SSHdefaults['host'],
                                      SSHdefaults['port'], SSHdefaults['login'],
                                      SSHdefaults['password']).exec('ls')
    assert (str(transport_instance) == "b'testfile\\n'")


def test_exec_exception():
    with pytest.raises(TransportError):
        SSHtransport(SSHdefaults['host'], SSHdefaults['port'],
                     SSHdefaults['login'], SSHdefaults['password']).exec(None)


# Check for getting existing file or getting file without name
def test_getfile_exists():
    transport_instance = SSHtransport(SSHdefaults['host'],
                                      SSHdefaults['port'], SSHdefaults['login'],
                                      SSHdefaults['password']).get_file('testfile')
    assert isinstance(transport_instance, bytes)


def test_empty_file():
    transport_instance = SSHtransport(SSHdefaults['host'],
                                      SSHdefaults['port'], SSHdefaults['login'],
                                      SSHdefaults['password']).get_file('')
    assert isinstance(transport_instance, bytes)


# Check for getting not existing file
def test_getfile_wrong_name_exception():
    with pytest.raises(TransportError):
        SSHtransport(SSHdefaults['host'], SSHdefaults['port'],
                     SSHdefaults['login'],
                     SSHdefaults['password']).get_file('_unknownfile_')
