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
                'control_id', 'audit_id']
    scansystem = ['id', 'scandate', 'start_time', 'end_time', 'duration',
                  'tests_count', 'not_null_status']
    audit = ['id', 'OSName', 'OSArchitecture', 'OSVersion',
             'NetBiosName', 'Hostname', 'Domain', 'Workgroup']

    control_columns = connection.execute(
        'PRAGMA table_info(control);').fetchall()
    scandata_columns = connection.execute(
        'PRAGMA table_info(scandata);').fetchall()
    scansystem_columns = connection.execute(
        'PRAGMA table_info(scansystem);').fetchall()
    audit_columns = connection.execute(
        'PRAGMA table_info(audit);').fetchall()
    for index, controldb in enumerate(control_columns):
        assert (controldb[1] == control[index])
    for index, scandatadb in enumerate(scandata_columns):
        assert (scandatadb[1] == scandata[index])
    for index, scansystemdb in enumerate(scansystem_columns):
        assert (scansystemdb[1] == scansystem[index])
    for index, auditdb in enumerate(audit_columns):
        assert (auditdb[1] == audit[index])
    connection.close()


def test_add_control_good(connection):
    with connection:
        control_func = local_db.add_control(0, 'name', 5)
        value_from_db = connection.execute("SELECT status FROM scandata \
            WHERE id = (SELECT MAX(id) from scandata)").fetchone()[0]
        value_from_enum = Status(5).name
        assert (value_from_db == value_from_enum)
    connection.close()
