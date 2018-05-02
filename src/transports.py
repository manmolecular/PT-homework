#!/usr/bin/env python3
# SSH transport class based on PT-security lectures
from get_config import *

import paramiko
import socket
import json

# Some helpful dicts for using
_get_file_defaults = {
        'file_name': 'testfile',
        'remote_path': './',
        'local_path': './'
    }

# Classes for error handling
class TransportError(Exception):
    def __init__(self, error_args):
        Exception.__init__(self, 'TransportError {}'.format(error_args))
        self.error_args = error_args

class TransportUnknown(Exception):
    def __init__(self, error_args):
        TransportError.__init__(self, error_args)
        self.error_args = error_args

class TransportConnectionError(TransportError):
    def __init__(self, error_args):
        TransportError.__init__(self, error_args)

class TransportIOError(TransportError):
    def __init__(self, error_args):
        TransportError.__init__(self, error_args)


# SSH transport class
class SSHtransport():
    def __init__(self, host, port, login, password):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.client.connect(hostname = host, username = login, password = password, port = port)
        except  paramiko.BadHostKeyException:
            raise TransportConnectionError('paramiko: BadHostKeyException')
        except  paramiko.AuthenticationException:
            raise TransportConnectionError('paramiko: AuthenticationException')
        except paramiko.SSHException:
            raise TransportConnectionError('paramiko: SSHException')
        except socket.error:
            raise TransportConnectionError('paramiko: socket.error')
        except:
            raise TransportConnectionError('connection refused by unknown reason')
            
    def __del__(self):
        self.client.close()

    def exec(self, command = ''):
        if not command:
            raise TransportError({'command':command})
        stdin, stdout, stderr = self.client.exec_command(command)
        return stdout.read()

    def get_file(self, file_name = _get_file_defaults['file_name'], 
        remote_path = _get_file_defaults['remote_path'], local_path = _get_file_defaults['local_path']):
        if not file_name:
            raise TransportError({'file_name':file_name})
        file_remote = remote_path + file_name
        file_local = local_path + file_name
        sftp = self.client.open_sftp()
        try:
            sftp.stat(file_remote)
        except paramiko.SSHException:
            raise TransportConnectionError('paramiko: SSHException')
        except IOError:
            raise TransportIOError('file doesnt exist')
        sftp.get(file_remote, file_local)
        sftp.close()

    def is_exist(self, file_name = _get_file_defaults['file_name'], 
        remote_path = _get_file_defaults['remote_path'], local_path = _get_file_defaults['local_path']):
        if not file_name:
            raise TransportError({'file_name':file_name})
        file_remote = remote_path + file_name
        file_local = local_path + file_name
        sftp = self.client.open_sftp()
        try:
            sftp.stat(file_remote)
        except paramiko.SSHException:
            raise TransportConnectionError('paramiko: SSHException')
        except IOError:
            raise TransportIOError('file doesnt exist')
        sftp.close()

# Set default area of transport names
global_transport_names = {
        'SSH':SSHtransport
    }

# Get defaults from config file
def get_defaults(transport_name):
    _json_config = get_config()
    return {
        'host': _json_config['host'], 
        'port':_json_config['transports'][transport_name]['port'], 
        'login':_json_config['transports'][transport_name]['login'], 
        'password':_json_config['transports'][transport_name]['password']
    }

# Get unique transport of some class
def get_transport(transport_name, host = None, port = None, login = None, password = None):
    if transport_name not in global_transport_names:
        raise TransportUnknown({'transport_name':transport_name})
    
    default = get_defaults(transport_name)
    host = host or default['host']
    port = port or default['port']
    login = login or default['login']
    password = password or default['password']

    return global_transport_names[transport_name](host, port, login, password)