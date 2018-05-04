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

# Mysql transport class test block

def test_sql_exec_empty():
    connection = pymysql.connect(host = 'localhost', 
            user = 'root', 
            port = 43306, 
            password = 'password', 
            db = 'def_database', 
            charset='utf8', 
            cursorclass=pymysql.cursors.DictCursor, 
            unix_socket=False)

    with connection.cursor() as cursor:
        cursor.execute('''
            DROP TABLE IF EXISTS users;
            ''')

        connection.commit()
        connection.close()

    with pytest.raises(TransportError):
        get_transport('SQL').sql_exec("SELECT `id`, `password` FROM `users` WHERE `email`=%s", 'webmaster@python.org')

def test_insert_db():
    connection = pymysql.connect(host = 'localhost', 
            user = 'root', 
            port = 43306, 
            password = 'password', 
            db = 'def_database', 
            charset='utf8', 
            cursorclass=pymysql.cursors.DictCursor, 
            unix_socket=False)

    with connection.cursor() as cursor:
        cursor.execute('''
            DROP TABLE IF EXISTS users;
            ''')

    with connection.cursor() as cursor:
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS `users` (
        `id` int(11) NOT NULL AUTO_INCREMENT,
        `email` varchar(255) COLLATE utf8_bin NOT NULL,
        `password` varchar(255) COLLATE utf8_bin NOT NULL,
        PRIMARY KEY (`id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin
            AUTO_INCREMENT=1 ;''')

    with connection.cursor() as cursor:
        sql = "INSERT IGNORE INTO `users` (`email`, `password`) VALUES (%s, %s)"
        cursor.execute(sql, ('webmaster@python.org', 'very-secret'))

    connection.commit()
    connection.close()

def test_get_sql_transport():
    get_transport('SQL')

def test_sql_exec():
    get_transport('SQL').sql_exec("SELECT `id`, `password` FROM `users` WHERE `email`=%s", 'webmaster@python.org')

def test_sql_exec_empty():
    get_transport('SQL').sql_exec("", '')

def test_check_empty_table():
    get_transport('SQL').check_if_empty_table('users')

def test_check_unknown_empty_table():
    get_transport('SQL').check_if_empty_table('_unknown_')

def test_all_not_empty_tables():
    get_transport('SQL').all_not_empty_tables()

def test_database_exist():
    get_transport('SQL').check_database_exist('def_database')

def test_unknown_database_exist():
    get_transport('SQL').check_database_exist('_unknown_')