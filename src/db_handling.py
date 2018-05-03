#!/usr/bin/env python3
# Create and manage database
from enum import Enum
import json
import sqlite3
import os.path

_json_db = None
_db_contest = 'configs/controls.json'
_db_name = 'database.db'

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

def connect_database():
    connection = sqlite3.connect(_db_name)
    return connection

def get_full_path():
    my_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(my_path, _db_contest)

def load_json():
    global _json_db
    if not _json_db:
        with open(get_full_path(),'r') as f:
            _json_db = json.load(f)
    return _json_db
     
def create_db():
    connection = connect_database()
    curr = connection.cursor()

    try:
        with connection:
            curr.execute('''
                CREATE TABLE IF NOT EXISTS control(id INTEGER PRIMARY KEY, header TEXT, descr TEXT, filename TEXT, requirement TEXT, transport TEXT)
                ''')
            curr.execute('''
                CREATE TABLE IF NOT EXISTS scandata(id INTEGER PRIMARY KEY, status TEXT)
                ''')
    except sqlite3.Error as e:
        raise DatabaseError(e.args[0])

    controls = load_json()
    for cur_control in controls:
        try:
            with connection:
                curr.execute("INSERT OR REPLACE INTO control(id, header, descr, filename, requirement, transport) VALUES(?, ?, ?, ?, ?, ?)", 
                    (cur_control[0], cur_control[1], cur_control[2], cur_control[3], cur_control[4], cur_control[5]))
        except sqlite3.Error as e:
            raise DatabaseError(e.args[0])

    connection.close()

def add_control(control_id, status):
    connection = connect_database()
    curr = connection.cursor()
    try:
        with connection:
            curr.execute("INSERT OR REPLACE INTO scandata(id, status) VALUES(?, ?)", 
                    (control_id, Status(status).name))
    except sqlite3.Error as e:
        raise DatabaseError(e.args[0])

    connection.close()