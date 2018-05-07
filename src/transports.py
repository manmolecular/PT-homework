#!/usr/bin/env python3
# SSH transport class based on PT-security lectures
from get_config import get_config
import paramiko
import pymysql.cursors
import socket
import json

FILE_DEFAULT = 'testfile'


# Classes for error handling
class TransportError(Exception):
    def __init__(self, error_args):
        super().__init__(self)
        self.error_args=error_args

    def __str__(self):
        return (self.error_args)


class TransportUnknown(Exception):
    def __init__(self, error_args):
        def __init__(self, error_args):
            super().__init__(self)
            self.error_args=error_args

        def __str__(self):
            return (self.error_args)


class TransportConnectionError(TransportError):
    def __init__(self, error_args):
        TransportError.__init__(self, error_args)


class TransportIOError(TransportError):
    def __init__(self, error_args):
        TransportError.__init__(self, error_args)


# MySQL transport
class MySQLtransport():
    def __init__(self, host, port, login, password):
        try:
            self.connection = pymysql.connect(
                host=host,
                user=login,
                port=port,
                password=password,
                db='def_database',
                charset='utf8',
                cursorclass=pymysql.cursors.DictCursor,
                unix_socket=False)
        except pymysql.MySQLError as e:
            raise TransportConnectionError(e) from e

    def sql_exec(self, sql_query, sql_data):
        if not sql_query:
            return None
        else:
            with self.connection.cursor() as cursor:
                try:
                    cursor.execute(sql_query, sql_data)
                    return cursor.fetchone()
                except pymysql.MySQLError as e:
                    raise TransportError(e) from e

    def check_database_exist(self, database_name):
        with self.connection.cursor() as cursor:
            sql_query = 'SELECT SCHEMA_NAME FROM \
            INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = %s'
            cursor.execute(sql_query, database_name)
            result = cursor.fetchone()
            if result:
                return True
            else:
                return False

    def check_if_empty_table(self, table_name):
        with self.connection.cursor() as cursor:
            cursor.execute('''
                SELECT table_name
                FROM information_schema.tables
                WHERE table_rows = 0;
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

    def all_empty_tables(self):
        with self.connection.cursor() as cursor:
            cursor.execute('''
                SELECT table_name
                FROM information_schema.tables
                WHERE table_rows = 0;
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
            self.client.connect(
                hostname=host,
                username=login,
                password=password,
                port=port)
        except (paramiko.BadHostKeyException, paramiko.AuthenticationException,
                paramiko.SSHException, socket.error) as e:
            raise TransportConnectionError(e) from e

    def exec(self, command=None):
        if not command:
            raise TransportError({'command': command})
        stdin, stdout, stderr = self.client.exec_command(command)
        return stdout.read()

    def get_file(self, file_name=None):
        file_name = file_name or FILE_DEFAULT

        if not file_name:
            raise TransportError({'file_name': file_name})
        sftp = self.client.open_sftp()

        try:
            sftp.stat(file_name)
        except paramiko.SSHException:
            raise TransportConnectionError('paramiko: SSHException')
        except IOError:
            raise TransportIOError('file doesnt exist')

        file = sftp.open(file_name, mode='r', bufsize=-1).read()
        sftp.close()
        return file

    def __del__(self):
        self.client.close()


# Set default area of transport names
global_transport_names = {
        'SSH': SSHtransport,
        'SQL': MySQLtransport
    }


# Get defaults from config file
def get_defaults(transport_name):
    json_cfg = get_config()
    return {
        'host': json_cfg['host'],
        'port': json_cfg['transports'][transport_name]['port'],
        'login': json_cfg['transports'][transport_name]['login'],
        'password': json_cfg['transports'][transport_name]['password']
    }


# Get unique transport of some class
def get_transport(transport_name, host=None,
                  port=None, login=None, password=None):
    if transport_name not in global_transport_names:
        raise TransportUnknown({'transport_name': transport_name})

    default = get_defaults(transport_name)
    host = host or default['host']
    port = port or default['port']
    login = login or default['login']
    password = password or default['password']

    return global_transport_names[transport_name](host, port, login, password)
