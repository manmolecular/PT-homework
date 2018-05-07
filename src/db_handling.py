#!/usr/bin/env python3
# Create and manage database
from enum import Enum
import json
import sqlite3
from pathlib import Path
import os


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
                    CREATE TABLE IF NOT EXISTS control(id INTEGER
                    PRIMARY KEY, header TEXT, descr TEXT, 
                    filename TEXT, requirement TEXT, transport TEXT)
                    '''
                    )
                self.connection.execute(
                    '''
                    CREATE TABLE IF NOT EXISTS 
                    scandata(id INTEGER PRIMARY KEY, status TEXT)
                    '''
                    )
        except sqlite3.Error as e:
            raise DatabaseError(e.args[0])

        controls = load_json()

        try:
            with self.connection:
                for cur_control in controls:
                    self.connection.execute(
                        "INSERT OR REPLACE INTO \
                        control(id, header, descr, filename, requirement, \
                        transport) VALUES(?, ?, ?, ?, ?, ?)", 
                        (
                            cur_control[0], 
                            cur_control[1], 
                            cur_control[2], 
                            cur_control[3], 
                            cur_control[4], 
                            cur_control[5])
                        )
        except sqlite3.Error as e:
            raise DatabaseError(e.args[0])

    def add_control(self, control_id, status):
        try:
            with self.connection:
                self.connection.execute(
                    "INSERT OR REPLACE INTO scandata \
                    (id, status) VALUES(?, ?)", 
                        (control_id, Status(status).name))
        except sqlite3.Error as e:
            raise DatabaseError(e.args[0])

    def __del__(self):
        self.connection.close()