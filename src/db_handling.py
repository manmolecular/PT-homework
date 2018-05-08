#!/usr/bin/env python3
# Create and manage database
from enum import Enum
import json
import sqlite3
from pathlib import Path
import os
import datetime

JSON_DB = None
DB_CONTEST = 'configs/controls.json'
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
    global JSON_DB
    if not JSON_DB:
        with Path('.').joinpath(DB_CONTEST).open() as f:
            JSON_DB = json.load(f)
    return JSON_DB


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
        except sqlite3.Error as e:
            raise DatabaseError(e.args[0])

    def create_db(self):
        try:
            with self.connection:
                self.connection.execute(
                    '''
                    CREATE TABLE IF NOT EXISTS 
                    control(
                        id INTEGER PRIMARY KEY,
                        descr TEXT,
                        filename TEXT,
                        requirement TEXT)
                    '''
                    )
                self.connection.execute(
                    '''
                    CREATE TABLE IF NOT EXISTS
                    scandata(
                        id INTEGER PRIMARY KEY,
                        header TEXT,
                        transport TEXT,
                        status TEXT)
                    '''
                    )
                self.connection.execute(
                    '''
                    CREATE TABLE IF NOT EXISTS
                    scansystem(
                        id INTEGER PRIMARY KEY,
                        scan_date TEXT,
                        longitude TEXT,
                        tests_count INTEGER,
                        status_not_null INTEGER)
                    ''')
        except sqlite3.Error as e:
            raise DatabaseError(e.args[0])

        controls = load_json()

        try:
            with self.connection:
                for cur_control in controls:
                    self.connection.execute(
                        "INSERT OR REPLACE INTO \
                        control(id, descr, filename, requirement) \
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
                    "INSERT OR REPLACE INTO scandata \
                    (id, header, transport, status) VALUES(?, ?, ?, ?)",
                    (control_id, control_name, transport_name,
                    Status(control_status).name))
        except sqlite3.Error as e:
            raise DatabaseError(e.args[0])

    def add_scan_info(self, longitude):
        scan_date = datetime.datetime.today().strftime('%Y-%m-%d')
        scan_longitude = longitude

        try:
            with self.connection:
                tests_count = self.connection.execute("SELECT Count(*) FROM \
                    scandata").fetchall()[0][0]
                tests_count_not_null = self.connection.execute("SELECT Count(*) \
                    FROM scandata WHERE status IS NOT NULL").fetchall()[0][0]
                self.connection.execute(
                    "INSERT OR REPLACE INTO scansystem \
                    (scan_date, longitude, tests_count, status_not_null)\
                    VALUES (?, ?, ?, ?)",
                    (scan_date, scan_longitude, 
                    tests_count, tests_count_not_null))
        except sqlite3.Error as e:
            raise DatabaseError(e.args[0])

    def __del__(self):
        self.connection.close()
