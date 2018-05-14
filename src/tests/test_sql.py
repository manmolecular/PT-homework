#!/usr/bin/env python3
# Tests for sql transport
import pymysql
import pytest

from transports import MySQLtransport, get_defaults, get_transport, \
TransportError, TransportConnectionError

SQLdefaults = get_defaults('SQL')
SQL_DATA = 'webmaster@python.org'


def setup_module():
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 port=43306,
                                 password='rootpass',
                                 db='def_database',
                                 charset='utf8',
                                 cursorclass=pymysql.cursors.DictCursor,
                                 unix_socket=False)

    with connection as cursor:
        cursor.execute('DROP TABLE IF EXISTS users')
        cursor.execute('DROP TABLE IF EXISTS empty')
        cursor.execute('''
                CREATE TABLE IF NOT EXISTS `users` (
                `id` int(11) NOT NULL AUTO_INCREMENT,
                `email` varchar(255) COLLATE utf8_bin NOT NULL,
                `password` varchar(255) COLLATE utf8_bin NOT NULL,
                PRIMARY KEY (`id`)) ENGINE=InnoDB 
                DEFAULT CHARSET=utf8 COLLATE=utf8_bin 
                AUTO_INCREMENT=1 ;''')

        cursor.execute('''
                CREATE TABLE IF NOT EXISTS `empty` (
                `id` int NOT NULL AUTO_INCREMENT, 
                PRIMARY KEY (`id`)) ENGINE=InnoDB 
                DEFAULT CHARSET=utf8 COLLATE=utf8_bin 
                AUTO_INCREMENT=1 ;''')

        sql = "INSERT IGNORE INTO `users` (`email`, `password`) \
            VALUES (%s, %s)"
        cursor.execute(sql, ('webmaster@python.org', \
                                          'very-secret'))

    connection.close()


def test_mysql_init():
    result = MySQLtransport(SQLdefaults['host'], SQLdefaults['port'],
                            SQLdefaults['login'], SQLdefaults['password'])
    default_names = ['id', 'email', 'password']
    columns = result.sql_exec(
        "SELECT * FROM information_schema.columns WHERE \
        table_schema = 'def_database' AND table_name = 'users'")
    for index, column in enumerate(columns):
        assert (column['COLUMN_NAME'] == default_names[index])


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
    right_dict = {'password': 'very-secret', 'id': 1}
    result = get_transport('SQL').sql_exec("SELECT `id`, `password`\
        FROM `users` WHERE `email`=%s", SQL_DATA)[0]
    assert isinstance(result, dict)
    assert (right_dict == result)


def test_empty_exec():
    with pytest.raises(TransportError):
        get_transport('SQL').sql_exec("", "")


def test_not_empty_table():
    result = get_transport('SQL').check_if_empty_table('users')
    assert not result


def test_empty_table():
    result = get_transport('SQL').check_if_empty_table('empty')
    assert result


def test_all_empty_tables():
    result = get_transport('SQL').all_empty_tables()
    assert isinstance(result, list)
    assert (len(result) == 17)


def test_all_not_empty_tables():
    result = get_transport('SQL').all_not_empty_tables()
    assert isinstance(result, list)
    assert (len(result) == 67)


def test_check_database_exist():
    result = get_transport('SQL').check_database_exist('def_database')
    assert result


def test_check_database_not_exist():
    result = get_transport('SQL').check_database_exist('_unknown_')
    assert not result
