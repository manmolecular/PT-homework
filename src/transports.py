#!/usr/bin/env python3
# SSH transport class based on PT-security lectures
from get_config import get_full_path, get_config

import paramiko
import pymysql.cursors
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

# MySQL transport
class MySQLtransport():
    def __init__(self, host, port, login, password):
        self.connection = pymysql.connect(host = host, 
            user = login, 
            port = port, 
            password = password, 
            db = 'def_database', 
            charset='utf8', 
            cursorclass=pymysql.cursors.DictCursor, 
            unix_socket=False)

    def sql_exec(self, sql_query, sql_data):
        with self.connection.cursor() as cursor:
            if sql_query:
                cursor.execute(sql_query, sql_data)
                return cursor.fetchone()
            else:
                return None

    def check_if_empty_table(self, table_name):
        with self.connection.cursor() as cursor:
            cursor.execute('''
                SELECT table_name
                FROM information_schema.tables
                WHERE table_rows >= 1;
                ''')
            result_list = cursor.fetchall()
            for result in result_list:
                if result['table_name'] == table_name:
                    return True
            return False

    def all_not_empty_tables(self):
        with self.connection.cursor() as cursor:
            cursor.execute('''
                SELECT table_name
                FROM information_schema.tables
                WHERE table_rows >= 1;
                ''')
            return cursor.fetchall()

    def __del__(self):
        self.connection.close()

# SSH transport class
class SSHtransport():
    def __init__(self, host, port, login, password):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.client.connect(hostname = host, username = login, password = password, port = port)
        except (paramiko.BadHostKeyException, paramiko.AuthenticationException, 
        paramiko.SSHException, socket.error) as e:
            raise TransportConnectionError(e) from e
            
    def __del__(self):
        self.client.close()

    def exec(self, command = None):
        if not command:
            raise TransportError({'command':command})
        stdin, stdout, stderr = self.client.exec_command(command)
        return stdout.read()

    def get_file(self, file_name = None, remote_path = None, local_path = None):
        file_name = file_name or _get_file_defaults['file_name']
        remote_path = remote_path or _get_file_defaults['remote_path']
        local_path = local_path or _get_file_defaults['local_path']

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

    def is_exist(self, file_name = None, remote_path = None, local_path = None):
        file_name = file_name or _get_file_defaults['file_name']
        remote_path = remote_path or _get_file_defaults['remote_path']
        local_path = local_path or _get_file_defaults['local_path']

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
            sftp.close()
            return False
        sftp.close()
        return True

# Set default area of transport names
global_transport_names = {
        'SSH':SSHtransport,
        'SQL':MySQLtransport
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