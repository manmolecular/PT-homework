#!/usr/bin/env python3
# Tests for sql transport
from transports import MySQLtransport, get_defaults, get_transport
from transports import TransportError, TransportUnknown, TransportConnectionError, TransportIOError
import pymysql
import pytest

SQLdefaults = get_defaults('SQL')
sql_data = 'webmaster@python.org'

def prepare_base():
    connection = pymysql.connect(host = 'localhost', 
            user = 'root', 
            port = 43306, 
            password = 'password', 
            db = 'def_database', 
            charset='utf8', 
            cursorclass=pymysql.cursors.DictCursor, 
            unix_socket=False)

    with connection:
        connection.cursor().execute('''
                DROP TABLE IF EXISTS users;
                ''')

        connection.cursor().execute('''
                CREATE TABLE IF NOT EXISTS `users` (
                `id` int(11) NOT NULL AUTO_INCREMENT,
                `email` varchar(255) COLLATE utf8_bin NOT NULL,
                `password` varchar(255) COLLATE utf8_bin NOT NULL,
                PRIMARY KEY (`id`)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin
                    AUTO_INCREMENT=1 ;''')

        sql = "INSERT IGNORE INTO `users` (`email`, `password`) VALUES (%s, %s)"
        connection.cursor().execute(sql, ('webmaster@python.org', 'very-secret'))

    connection.close()

def drop_n_create_table():
    connection = pymysql.connect(host = 'localhost', 
        user = 'root', 
        port = 43306, 
        password = 'password', 
        db = 'def_database', 
        charset='utf8', 
        cursorclass=pymysql.cursors.DictCursor, 
        unix_socket=False)

    with connection:
        connection.cursor().execute('''
            DROP TABLE IF EXISTS users;
            ''')

        connection.cursor().execute('''
        CREATE TABLE IF NOT EXISTS `users` (
        `id` int(11) NOT NULL AUTO_INCREMENT,
        `email` varchar(255) COLLATE utf8_bin NOT NULL,
        `password` varchar(255) COLLATE utf8_bin NOT NULL,
        PRIMARY KEY (`id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin
            AUTO_INCREMENT=1 ;''')

    connection.close()

def test_mysql_init():
    prepare_base()
    sql_transport = MySQLtransport(SQLdefaults['host'], SQLdefaults['port'], 
        SQLdefaults['login'], SQLdefaults['password'])
    assert isinstance(sql_transport, MySQLtransport)

def test_mysql_wrong_host():
    with pytest.raises(TransportConnectionError):
        sql_transport = MySQLtransport('_wrong_', SQLdefaults['port'], 
            SQLdefaults['login'], SQLdefaults['password'])

def test_mysql_wrong_port():
    with pytest.raises(TransportConnectionError):
        sql_transport = MySQLtransport(SQLdefaults['host'], -1, 
            SQLdefaults['login'], SQLdefaults['password'])

def test_mysql_wrong_user():
    with pytest.raises(TransportConnectionError):
        sql_transport = MySQLtransport(SQLdefaults['host'], SQLdefaults['port'], 
            '_wrong_', SQLdefaults['password'])

def test_mysql_wrong_password():
    with pytest.raises(TransportConnectionError):
        sql_transport = MySQLtransport(SQLdefaults['host'], SQLdefaults['port'], 
            SQLdefaults['login'], '_wrong_')

def test_get_transport():
    sql_transport = get_transport('SQL')
    assert isinstance(sql_transport, MySQLtransport)

def test_exec():
    prepare_base()
    sql_transport = get_transport('SQL').sql_exec("SELECT `id`, `password` FROM `users` WHERE `email`=%s", sql_data)
    assert isinstance(sql_transport, dict)

def test_empty_exec():
    sql_transport = get_transport('SQL').sql_exec("", "")
    assert sql_transport is None

def test_not_empty_table():
    sql_transport = get_transport('SQL').check_if_empty_table('users')
    assert not sql_transport

def test_empty_table():
    drop_n_create_table()
    sql_transport = get_transport('SQL').check_if_empty_table('users')
    assert sql_transport

def test_all_empty_tables():
    prepare_base()
    sql_transport = get_transport('SQL').all_empty_tables()
    assert isinstance(sql_transport, list)

def test_all_not_empty_tables():
    sql_transport = get_transport('SQL').all_not_empty_tables()
    assert isinstance(sql_transport, list)

def test_check_database_exist():
    sql_transport = get_transport('SQL').check_database_exist('def_database')
    assert sql_transport

def test_check_database_not_exist():
    sql_transport = get_transport('SQL').check_database_exist('_unknown_')
    assert not sql_transport