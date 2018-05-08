#!/usr/bin/env python3
# Create and manage database
from enum import Enum
from pathlib import Path
import json
import sqlite3
import datetime

JSON_DB = None
DB_CONTEST = 'controls.json'
DB_DIR = 'configs'
DB_NAME = 'database.db'
CURRENT_SCAN = []

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
        with Path('.').joinpath(DB_DIR).joinpath(DB_CONTEST).open() as f:
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
                        scan_info TEXT)
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
        current_control = (control_id, control_name, transport_name, str(Status(control_status).name))
        CURRENT_SCAN.append(current_control)

    def add_scan_info(self, longitude):
        scan_date = datetime.datetime.today().strftime('%Y-%m-%d')
        scan_longitude = longitude

        try:
            with self.connection:
                self.connection.execute(
                    "INSERT OR REPLACE INTO scandata \
                    (id, scan_info) VALUES (?, ?)",
                    (None, str(CURRENT_SCAN)))

                tests_count = len(CURRENT_SCAN)
                tests_count_not_null = 0
                for status in CURRENT_SCAN:
                    if status[3]:
                        tests_count_not_null+=1

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
