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
    result = MySQLtransport(SQLdefaults['host'], SQLdefaults['port'], 
        SQLdefaults['login'], SQLdefaults['password'])
    assert isinstance(result, MySQLtransport)

def test_mysql_wrong_host():
    with pytest.raises(TransportConnectionError):
        result = MySQLtransport('_wrong_', SQLdefaults['port'], 
            SQLdefaults['login'], SQLdefaults['password'])

def test_mysql_wrong_port():
    with pytest.raises(TransportConnectionError):
        result = MySQLtransport(SQLdefaults['host'], -1, 
            SQLdefaults['login'], SQLdefaults['password'])

def test_mysql_wrong_user():
    with pytest.raises(TransportConnectionError):
        result = MySQLtransport(SQLdefaults['host'], SQLdefaults['port'], 
            '_wrong_', SQLdefaults['password'])

def test_mysql_wrong_password():
    with pytest.raises(TransportConnectionError):
        result = MySQLtransport(SQLdefaults['host'], SQLdefaults['port'], 
            SQLdefaults['login'], '_wrong_')

def test_get_transport():
    result = get_transport('SQL')
    assert isinstance(result, MySQLtransport)

def test_exec():
    prepare_base()
    result = get_transport('SQL').sql_exec("SELECT `id`, `password` FROM `users` WHERE `email`=%s", sql_data)
    assert isinstance(result, dict)

def test_empty_exec():
    result = get_transport('SQL').sql_exec("", "")
    assert result is None

def test_not_empty_table():
    result = get_transport('SQL').check_if_empty_table('users')
    assert not result

def test_empty_table():
    drop_n_create_table()
    result = get_transport('SQL').check_if_empty_table('users')
    assert result

def test_all_empty_tables():
    prepare_base()
    result = get_transport('SQL').all_empty_tables()
    assert isinstance(result, list)

def test_all_not_empty_tables():
    result = get_transport('SQL').all_not_empty_tables()
    assert isinstance(result, list)

def test_check_database_exist():
    result = get_transport('SQL').check_database_exist('def_database')
    assert result

def test_check_database_not_exist():
    result = get_transport('SQL').check_database_exist('_unknown_')
    assert not result