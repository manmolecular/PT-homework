#!/usr/bin/env python3
# Create and manage database
from enum import Enum
import json
import sqlite3
import os.path

_json_db = None
_db_contest = 'configs/controls.json'
_db_name = 'database.db'

class Status(Enum):
    STATUS_COMPLIANT = 1
    STATUS_NOT_COMPLIANT = 2
    STATUS_NOT_APPLICABLE = 3
    STATUS_ERROR = 4
    STATUS_EXCEPTION = 5

def get_db_obj():
    db = sqlite3.connect(_db_name)
    return db

def get_full_path():
    my_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(my_path, _db_contest)

def load_db():
    global _json_db
    if not _json_db:
        with open(get_full_path(),'r') as f:
            _json_db = json.load(f)
    return _json_db

def create_db():
    db = get_db_obj()
    curr = db.cursor()
    curr.execute('''
        CREATE TABLE IF NOT EXISTS control(id INTEGER PRIMARY KEY, header TEXT, descr TEXT, filename TEXT, requirement TEXT)
        ''')
    curr.execute('''
        CREATE TABLE IF NOT EXISTS scandata(id INTEGER PRIMARY KEY, descr TEXT, status TEXT)
        ''')
    controls = load_db()
    for cur_control in controls:
        curr.execute("INSERT OR REPLACE INTO control(id, header, descr, filename, requirement) VALUES(?, ?, ?, ?, ?)", 
            (cur_control[0], cur_control[1], cur_control[2], cur_control[3], cur_control[4]))
    db.commit()
    db.close()

def add_control(control_id, status):
    db = get_db_obj()
    curr = db.cursor()
    descr = (curr.execute("SELECT descr FROM control WHERE id = ?", str(control_id)).fetchone())[0]
    curr.execute("INSERT OR REPLACE INTO scandata(id, descr, status) VALUES(?, ?, ?)", 
            (control_id, descr, Status(status).name))
    db.commit()
    db.close()