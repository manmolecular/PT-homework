#!/usr/bin/env python3
# Create and manage database
import datetime
import json
import sqlite3
from enum import Enum
from pathlib import PurePosixPath

json_db = None
DB_CONTEST = 'controls.json'
DB_DIR = 'configs'
DB_NAME = 'database.db'


class DatabaseError(sqlite3.Error):
    def __init__(self, error_args):
        super().__init__(self)
        self.error_args = error_args

    def __str__(self):
        return (self.error_args)


class Status(Enum):
    STATUS_COMPLIANT = 1
    STATUS_NOT_COMPLIANT = 2
    STATUS_NOT_APPLICABLE = 3
    STATUS_ERROR = 4
    STATUS_EXCEPTION = 5


def load_json():
    global json_db
    if not json_db:
        with open(str(PurePosixPath(DB_DIR, DB_CONTEST))) as f:
            json_db = json.load(f)
    return json_db


def connect_database():
    try:
        connection = sqlite3.connect(DB_NAME)
    except sqlite3.Error as e:
        raise DatabaseError(e.args[0])
    return connection


class SQLiteHandling():
    def __init__(self):
        self.connection = connect_database()
        self.connection.execute('PRAGMA foreign_keys = ON')

    def create_db(self):
        try:
            with self.connection:
                self.connection.execute(
                    '''
                    CREATE TABLE IF NOT EXISTS 
                    control(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        description TEXT,
                        filename TEXT,
                        requirement TEXT,
                        transport TEXT)
                    '''
                )
                self.connection.execute(
                    '''
                    CREATE TABLE IF NOT EXISTS
                    scandata(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        transport TEXT,
                        status TEXT,
                        scansystem_id INTEGER,
                        control_id INTEGER,

                        FOREIGN KEY (scansystem_id) REFERENCES scansystem(id),
                        FOREIGN KEY (control_id) REFERENCES control(id))
                    '''
                )
                self.connection.execute(
                    '''
                    CREATE TABLE IF NOT EXISTS
                    scansystem(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        scandate TEXT,
                        start_time TEXT,
                        end_time TEXT,
                        duration TEXT,
                        tests_count INTEGER,
                        not_null_status INTEGER)
                    ''')
        except sqlite3.Error as e:
            raise DatabaseError(e.args[0])

        controls = load_json()

        try:
            with self.connection:
                for cur_control in controls:
                    self.connection.execute(
                        '''
                        INSERT OR REPLACE INTO
                        control(id, description, filename, requirement, 
                        transport) VALUES(?, ?, ?, ?, ?)''',
                        (
                            cur_control[0],
                            cur_control[1],
                            cur_control[2],
                            cur_control[3],
                            cur_control[4]
                        ))
        except sqlite3.Error as e:
            raise DatabaseError(e.args[0])

    def add_control(self, control_id, control_name, control_status):
        try:
            with self.connection:
                self.connection.execute(
                    '''
                    INSERT OR REPLACE INTO
                    scandata(name, transport, status, scansystem_id, 
                    control_id) VALUES (?, ?, ?, ?, ?)''',
                    (
                        control_name,
                        self.connection.execute(
                            'SELECT transport FROM control WHERE id = ?',
                            str(control_id)).fetchone()[0],
                        Status(control_status).name,
                        self.connection.execute(
                            'SELECT max(id) FROM scansystem').fetchone()[0],
                        control_id
                    ))
        except sqlite3.Error as e:
            raise DatabaseError(e.args[0])

    def initial_scan(self):
        scan_date = datetime.datetime.today().strftime('%Y-%m-%d')
        try:
            with self.connection:
                self.connection.execute(
                    'INSERT OR REPLACE INTO scansystem'
                    '(id, scandate) VALUES (?, ?)',
                    (None, scan_date))
        except sqlite3.Error as e:
            raise DatabaseError(e.args[0])

    def add_time(self, start_time, end_time, duration):
        max_id = self.connection.execute(
            'SELECT max(id) FROM scansystem').fetchone()[0]
        try:
            with self.connection:
                test_count = self.connection.execute(
                    'SELECT COUNT(*) FROM scandata WHERE scansystem_id = ?',
                    str(max_id)).fetchone()[0]
                test_count_not_null = self.connection.execute(
                    'SELECT COUNT(*) FROM scandata WHERE scansystem_id = ? \
                    AND status IS NOT NULL', str(max_id)).fetchone()[0]

                sql = (
                    '''
                    UPDATE scansystem
                          SET start_time = ? ,
                              end_time = ? ,
                              duration = ? ,
                              tests_count = ? ,
                              not_null_status = ?
                          WHERE id = ?
                    ''')
                self.connection.execute(sql, (str(start_time), str(end_time),
                                              duration, str(test_count), str(test_count_not_null),
                                              max_id))

        except sqlite3.Error as e:
            raise DatabaseError(e.args[0])

    def close(self):
        self.connection.close()

    def __del__(self):
        self.close()
