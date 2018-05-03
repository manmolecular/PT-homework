#!/usr/bin/env python3
# Tests for SSH transport class based on PT-security lectures
from transports import *
from db_handling import *
import pytest

SSHdefaults = get_defaults('SSH')
_database = 'database.db'

# Transport class test block
def test_SSH_get_transport_exc():
    get_transport('SSH', SSHdefaults['host'], SSHdefaults['port'], 
        SSHdefaults['login'], SSHdefaults['password'])
    get_transport('SSH')
    with pytest.raises(TransportUnknown):
        get_transport('', SSHdefaults['host'], SSHdefaults['port'], 
            SSHdefaults['login'], SSHdefaults['password'])

def test_SSH_init_exc():
    SSHtransport(SSHdefaults['host'], SSHdefaults['port'], 
        SSHdefaults['login'], SSHdefaults['password'])
    with pytest.raises(TransportConnectionError):
        SSHtransport('_unknownhost_', SSHdefaults['port'], 
            SSHdefaults['login'], SSHdefaults['password'])
        SSHtransport(SSHdefaults['host'], '_unknownport_', 
            SSHdefaults['login'], SSHdefaults['password'])
        SSHtransport(SSHdefaults['host'], SSHdefaults['port'], 
            '_unknownlogin_', SSHdefaults['password'])
        SSHtransport(SSHdefaults['host'], '_unknownport_', 
            SSHdefaults['login'], '_unknownpass_')

def test_SSH_exec_exc():
    SSHtransport(SSHdefaults['host'], SSHdefaults['port'], 
        SSHdefaults['login'], SSHdefaults['password']).exec('ls')
    with pytest.raises(TransportError):
        SSHtransport(SSHdefaults['host'], SSHdefaults['port'], 
            SSHdefaults['login'], SSHdefaults['password']).exec()

def test_SSH_get_file_name_exc():
    SSHtransport(SSHdefaults['host'], SSHdefaults['port'], 
        SSHdefaults['login'], SSHdefaults['password']).get_file('testfile')
    SSHtransport(SSHdefaults['host'], SSHdefaults['port'], 
        SSHdefaults['login'], SSHdefaults['password']).get_file('')

def test_SSH_get_file_remote_exc():
    with pytest.raises(TransportError):
       SSHtransport(SSHdefaults['host'], SSHdefaults['port'], 
            SSHdefaults['login'], SSHdefaults['password']).get_file('_unknownfile_')

def test_SSH_is_exist_name_exc():
    SSHtransport(SSHdefaults['host'], SSHdefaults['port'], 
        SSHdefaults['login'], SSHdefaults['password']).is_exist('testfile')
    SSHtransport(SSHdefaults['host'], SSHdefaults['port'], 
        SSHdefaults['login'], SSHdefaults['password']).is_exist('')

# Database class test block

def test_create_db():
    if not os.path.isfile('./' + _database):
        create_db()

def test_connect_database():
    connect_database()

def test_load_json():
    load_json()

def test_add_control():
    add_control(0, 1)
    with pytest.raises(Exception):
        add_control('invalid id','invalid status')