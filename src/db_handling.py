#!/usr/bin/env python3
# Create and manage database
from enum import Enum
from pathlib import Path
import json
import sqlite3
import datetime

json_db = None
DB_CONTEST = 'controls.json'
DB_DIR = 'configs'
DB_NAME = 'database.db'

class DatabaseError(sqlite3.Error):
    def __init__(self, error_args):
        Exception.__init__(self, 'DatabaseError {}'.format(error_args))
        self.error_args = error_args


class Status(Enum):
    STATUS_COMPLIANT = 1
    STATUS_NOT_COMPLIANT = 2
    STATUS_NOT_APPLICABLE = 3
    STATUS_ERROR = 4
    STATUS_EXCEPTION = 5


def load_json():
    global json_db
    if not json_db:
        with Path('.').joinpath(DB_DIR).joinpath(DB_CONTEST).open() as f:
            json_db = json.load(f)
    return json_db


def connect_database():
    try:
        connection = sqlite3.connect(DB_NAME)
    except sqlite3.Error as e:
        raise DatabaseError(e.args[0])
    return connection


class sqlite_handle():
    def __init__(self):
        try:
            self.connection = sqlite3.connect(DB_NAME)
            self.connection.execute("PRAGMA foreign_keys = ON")
        except sqlite3.Error as e:
            raise DatabaseError(e.args[0])

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
                        requirement TEXT)
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
                        "INSERT OR REPLACE INTO \
                        control(id, description, filename, requirement) \
                        VALUES(?, ?, ?, ?)",
                        (
                            cur_control[0],
                            cur_control[1],
                            cur_control[2],
                            cur_control[3]
                        ))
        except sqlite3.Error as e:
            raise DatabaseError(e.args[0])

    def add_control(self, control_id, control_name, 
                    transport_name, control_status):
        try:
            with self.connection:
                self.connection.execute(
                    "INSERT OR REPLACE INTO \
                    scandata(name, transport, status, scansystem_id, control_id) \
                    VALUES (?, ?, ?, ?, ?)",
                    (
                        control_name,
                        transport_name,
                        Status(control_status).name,
                        self.connection.execute("SELECT max(id) FROM scansystem").fetchone()[0],
                        control_id
                    ))
        except sqlite3.Error as e:
            raise DatabaseError(e.args[0])


    def initial_scan(self):
        scan_date = datetime.datetime.today().strftime('%Y-%m-%d')
        try:
            with self.connection:
                self.connection.execute(
                    "INSERT OR REPLACE INTO scansystem \
                    (id, scandate) VALUES (?, ?)",
                    (None, scan_date))
        except sqlite3.Error as e:
            raise DatabaseError(e.args[0])


    def add_time(self, start_time, end_time, duration):
        max_id = self.connection.execute("SELECT max(id) FROM scansystem").fetchone()[0]
        try:
            with self.connection:
                test_count_query = (
                    '''
                    SELECT COUNT(*) FROM scandata WHERE scansystem_id = ?
                    ''')
                test_count_not_null_query = (
                    '''
                    SELECT COUNT(*) FROM scandata WHERE scansystem_id = ? AND status IS NOT NULL
                    ''')
                test_count = self.connection.execute(test_count_query, str(max_id)).fetchone()[0]
                test_count_not_null = self.connection.execute(test_count_not_null_query, str(max_id)).fetchone()[0]

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
                self.connection.execute(sql, (str(start_time), str(end_time), duration, str(test_count), str(test_count_not_null), max_id))

        except sqlite3.Error as e:
            raise DatabaseError(e.args[0])

    def __del__(self):
        self.connection.close()
