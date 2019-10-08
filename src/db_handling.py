#!/usr/bin/env python3
# Create and manage database
import datetime
import json
import sqlite3
from enum import Enum
from pathlib import Path

from transports import get_transport, TransportConnectionError

json_db = None
DB_CONTEST = 'controls.json'
DB_DIR = 'configs'
DB_NAME = 'database.db'


class DatabaseError(sqlite3.Error):
    def __init__(self, error_args):
        super().__init__(self)
        self.error_args = error_args

    def __str__(self):
        return self.error_args


class Status(Enum):
    STATUS_COMPLIANT = 1
    STATUS_NOT_COMPLIANT = 2
    STATUS_NOT_APPLICABLE = 3
    STATUS_ERROR = 4
    STATUS_EXCEPTION = 5


def load_json():
    global json_db
    if not json_db:
        with Path(DB_DIR, DB_CONTEST).open() as f:
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
                    '''
                )
                self.connection.execute(
                    '''
                    CREATE TABLE IF NOT EXISTS
                    audit(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        attribute TEXT,
                        value TEXT,
                        scansystem_id INTEGER,

                        FOREIGN KEY (scansystem_id) REFERENCES scansystem(id))
                    '''
                )
                self.connection.execute(
                    '''
                    CREATE TABLE IF NOT EXISTS
                    snmp_sysDescr(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        value TEXT,
                        scansystem_id INTEGER,

                        FOREIGN KEY (scansystem_id) REFERENCES scansystem(id))
                    '''
                )
                self.connection.execute(
                    '''
                    CREATE TABLE IF NOT EXISTS
                    snmp_interfaces(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        interface TEXT,
                        status TEXT,
                        scansystem_id INTEGER,

                        FOREIGN KEY (scansystem_id) REFERENCES scansystem(id))
                    '''
                )
                self.connection.execute(
                    '''
                    CREATE TABLE IF NOT EXISTS
                    ssh_audit(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        attribute TEXT,
                        value TEXT,
                        scansystem_id INTEGER,

                        FOREIGN KEY (scansystem_id) REFERENCES scansystem(id))
                    '''
                )
        except sqlite3.Error as e:
            raise DatabaseError(e.args[0])

        controls = load_json()

        try:
            with self.connection:
                for cur_control in controls:
                    self.connection.execute(
                        '''
                        INSERT OR REPLACE INTO
                        control(id, description, requirement, 
                        transport) VALUES(?, ?, ?, ?)''',
                        (tuple(cur_control)
                         ))
        except sqlite3.Error as e:
            raise DatabaseError(e.args[0])

    def add_control(self, control_id, control_name, control_status):
        try:
            with self.connection:
                current_scan = self.connection.execute(
                    'SELECT max(id) FROM scansystem').fetchone()[0]
                print('Current: ' + control_name)
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
                        current_scan,
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
                                              duration, str(test_count),
                                              str(test_count_not_null),
                                              max_id))
        except sqlite3.Error as e:
            raise DatabaseError(e.args[0])

    def add_audit(self):
        try:
            wmi_connection = get_transport('WMI')
        except TransportConnectionError as e:
            print('Warning: WMI service is unavailable')
            return 0
        query_result_sys = wmi_connection.wmi_query("Select Caption, \
            OSArchitecture, Version from Win32_OperatingSystem")[0]
        query_result_group = wmi_connection.wmi_query("Select Name, \
            DNSHostName, Domain, Workgroup, PartOfDomain \
            from Win32_ComputerSystem")[0]
        Domain = query_result_group.Domain
        Workgroup = query_result_group.Workgroup

        if query_result_group.PartOfDomain == False:
            Domain = None
        else:
            Workgroup = None

        audit_info = {
            'OSName': query_result_sys.Caption,
            'OSArchitecture': query_result_sys.OSArchitecture,
            'OSVersion': query_result_sys.Version,
            'NetBiosName': query_result_group.Name,
            'Hostname': query_result_group.DNSHostName,
            'Domain': Domain,
            'Workgroup': Workgroup,
            'PartOfDomain': bool(query_result_group.PartOfDomain)
        }

        try:
            with self.connection:
                current_scan = self.connection.execute(
                    'SELECT max(id) FROM scansystem').fetchone()[0]
                for key in audit_info:
                    self.connection.execute(
                        'INSERT OR REPLACE INTO audit'
                        '(attribute, value, scansystem_id) VALUES (?, ?, ?)',
                        (
                            key,
                            audit_info[key],
                            current_scan
                        ))
        except sqlite3.Error as e:
            raise DatabaseError(e.args[0])

    def add_SNMP_SSH_info(self, SNMP_audit_info, SSH_audit_info):
        try:
            with self.connection:
                current_scan = self.connection.execute(
                    'SELECT max(id) FROM scansystem').fetchone()[0]
                self.connection.execute(
                    'INSERT OR REPLACE INTO snmp_sysDescr'
                    '(value, scansystem_id) VALUES (?, ?)',
                    (
                        str(SNMP_audit_info['sysDescr']),
                        current_scan
                    ))
                for interface in SNMP_audit_info['listOfInterfaces']:
                    self.connection.execute(
                        'INSERT OR REPLACE INTO snmp_interfaces'
                        '(interface, status, scansystem_id)'
                        'VALUES (?, ?, ?)',
                        (
                            interface[0],
                            interface[1],
                            current_scan
                        ))
                for key in SSH_audit_info:
                    self.connection.execute(
                        'INSERT OR REPLACE INTO ssh_audit'
                        '(attribute, value, scansystem_id)'
                        'VALUES (?, ?, ?)',
                        (
                            key,
                            SSH_audit_info[key],
                            current_scan
                        ))
        except sqlite3.Error as e:
            raise DatabaseError(e.args[0])

    def close(self):
        self.connection.close()

    def __del__(self):
        self.close()
