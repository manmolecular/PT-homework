#!/usr/bin/env python3
# SSH transport class based on PT-security lectures
import socket

import paramiko
import pymysql.cursors
import wmi
import re

from get_config import get_config

FILE_DEFAULT = 'testfile'
WMI_OUTPUT_DIR = 'C:\\Windows\\temp\\'
WMI_CMD = 'cmd.exe /c'
HKLM = 0x80000002

class TransportError(Exception):
    """Base class for error handling"""

    def __init__(self, error_args):
        super().__init__(self)
        self.error_args = error_args

    def __str__(self):
        return str(self.error_args)


class TransportUnknown(Exception):
    def __init__(self, error_args):
        def __init__(self, error_args):
            super().__init__(self)
            self.error_args = error_args

        def __str__(self):
            return str(self.error_args)


class TransportConnectionError(TransportError):
    def __init__(self, error_args):
        super().__init__(error_args)


class TransportIOError(TransportError):
    def __init__(self, error_args):
        super().__init__(error_args)


class WMItransport():
    def __init__(self, computer, user, password):
        try:
            self.connect = wmi.WMI(computer=computer,
                                   user=user,
                                   password=password)
        except (wmi.x_access_denied, wmi.x_wmi) as e:
            raise TransportConnectionError(e) from e

    def wmi_exec(self, command):
        if not command:
            raise TransportError({'empty command'})

        """get filename from command without special characters"""
        filename = re.sub('[!@#$., ]', '', command)

        process_startup = self.connect.Win32_ProcessStartup.new()
        process_startup.ShowWindow = 1
        process_id, result = self.connect.Win32_Process.Create(
            CommandLine=WMI_CMD + ' ' + command + ' ' + 
            '> ' + WMI_OUTPUT_DIR + filename + '.txt',
            ProcessStartupInformation=process_startup
        )

        return {
            'process_id': process_id, 
            'result': result
        }  

    def wmi_query(self, query):
        if not query:
            raise TransportError({'empty query'})
        return self.connect.query(query)


class WMIregistryTransport(WMItransport):
    def __init__(self, computer, user, password):
        WMItransport.__init__(self, computer, user, password)

    def get_value(self, subkey, valuename):
        return self.connect.StdRegProv.GetDWORDValue(
            hDefKey=HKLM,
            sSubKeyName=subkey,
            sValueName=valuename
            )[1]


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

    def sql_exec(self, sql_query, sql_data=None):
        if not sql_query:
            raise TransportError({'empty query'})
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(sql_query, sql_data)
                return cursor.fetchall()
            except pymysql.MySQLError as e:
                raise TransportError(e) from e

    def check_database_exist(self, database_name):
        if not database_name:
            raise TransportError({'database_name': database_name})
        with self.connection.cursor() as cursor:
            sql_query = 'SELECT SCHEMA_NAME FROM \
            INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = %s'
            cursor.execute(sql_query, database_name)
            result = cursor.fetchone()
            return bool(result)

    def check_if_empty_table(self, table_name):
        if not table_name:
            raise TransportError({'table_name': table_name})
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

    def close(self):
        self.connection.close()


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

    def exec(self, command):
        if not command:
            raise TransportError({'command': command})
        stdin, stdout, stderr = self.client.exec_command(command)
        return stdout.read()

    def get_file(self, file_name=None):
        file_name = file_name or FILE_DEFAULT
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


global_transport_names = {
    'SSH': SSHtransport,
    'SQL': MySQLtransport,
    'WMI': WMItransport,
    'WMIreg': WMIregistryTransport
}


def get_defaults(transport_name):
    """Get defaults from config file"""
    json_cfg = get_config()
    
    if transport_name == 'WMI' or transport_name == 'WMIreg':
        return {
            'host': json_cfg['transports']['WMI']['computer'],
            'port': None,
            'login': json_cfg['transports']['WMI']['user'],
            'password': json_cfg['transports']['WMI']['password']
        } 
    return {
        'host': json_cfg['host'],
        'port': json_cfg['transports'][transport_name]['port'],
        'login': json_cfg['transports'][transport_name]['login'],
        'password': json_cfg['transports'][transport_name]['password']
    }


def get_transport(transport_name, host=None,
                  port=None, login=None, password=None):
    """Get unique transport of some class"""
    if transport_name not in global_transport_names:
        raise TransportUnknown({'transport_name': transport_name})

    default = get_defaults(transport_name)
    host = host or default['host']
    port = port or default['port']
    login = login or default['login']
    password = password or default['password']

    if transport_name == 'WMI' or transport_name == 'WMIreg':
        return global_transport_names[transport_name](host, login, password)
    return global_transport_names[transport_name](host, port, login, password)
