#!/usr/bin/env python3
from transports import get_transport, MySQLtransport
import pymysql.cursors

sql_data = 'webmaster@python.org'
trans = get_transport('SQL')

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

print(trans.sql_exec("SELECT `id`, `password` FROM `users` WHERE `email`=%s", sql_data))
print(trans.check_if_empty_table('users'))
print(trans.all_not_empty_tables())
print(trans.check_database_exist('def_database'))