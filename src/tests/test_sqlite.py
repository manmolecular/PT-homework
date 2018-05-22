#!/usr/bin/env python3
# Tests for database handling
import sqlite3

import pytest

from db_handling import load_json, SQLiteHandling, Status


@pytest.fixture
def connection():
    from db_handling import connect_database
    return connect_database()


def setup_module():
    global local_db
    local_db = SQLiteHandling()
    local_db.create_db()


# Check if function return object of sqlite3
def test_sqlite_object():
    assert isinstance(local_db, SQLiteHandling)


def test_connect_database(connection):
    assert isinstance(connection, sqlite3.Connection)


# Check if we return list of parameters from json config
def test_json_loader(connection):
    assert isinstance(load_json(), list)

    controls = connection.execute(
        'SELECT * from control').fetchall()

    for json, control in zip(load_json(), controls):
        assert int(json[0]) == int(control[0])
        for i in range(1, 4):
            assert (str(json[i]) == str(control[i]))

    connection.close()


def test_create_database(connection):
    control = ['id', 'description', 'requirement', 'transport']
    scandata = ['id', 'name', 'transport', 'status', 'scansystem_id',
                'control_id']
    scansystem = ['id', 'scandate', 'start_time', 'end_time', 'duration',
                  'tests_count', 'not_null_status']
    audit = ['id', 'attribute', 'value', 'scansystem_id']

    control_columns = connection.execute(
        'PRAGMA table_info(control);').fetchall()
    scandata_columns = connection.execute(
        'PRAGMA table_info(scandata);').fetchall()
    scansystem_columns = connection.execute(
        'PRAGMA table_info(scansystem);').fetchall()
    audit_columns = connection.execute(
        'PRAGMA table_info(audit);').fetchall()

    test_list = [control, scandata, scansystem, audit]
    db_list = [control_columns, scandata_columns, 
        scansystem_columns, audit_columns]

    for test_value, db_value in zip (test_list, db_list):
        assert len(test_value) == len(db_value)
        for a, b in zip (test_value, db_value):
            assert a == b[1]
            
    connection.close()


def test_add_control_good(connection):
    with connection:
        control_func = local_db.add_control(0, 'pytest_temp_value', 5)
        value_from_db = connection.execute("SELECT status FROM scandata \
            WHERE id = (SELECT MAX(id) from scandata)").fetchone()[0]
        value_from_enum = Status(5).name
        assert (value_from_db == value_from_enum)
    connection.close()
