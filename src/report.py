#!/usr/bin/env python3
# Module for report creating
from typing import NamedTuple

from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML, CSS

from db_handling import connect_database


class ControlInfo(NamedTuple):
    contrid: int
    description: str
    requirement: str
    name: str
    transport: str
    status: str


class BasicScanInfo(NamedTuple):
    scanid: int
    scandate: str
    start_time: str
    end_time: str
    duration: str
    tests_count: int
    not_null_status: int
    controls: list
    wmi_sys_info: list
    snmp_ssh: list


class WMIScanInfo(NamedTuple):
    OSname: str
    OSArchitecture: str
    OSVersion: str
    NetBiosName: str
    Hostname: str
    Domain: str
    Workgroup: str
    PartOfDomain: str

class SNMPSSHScanInfo(NamedTuple):
    sysDescr: str
    interfaces: list
    ssh_sys_info: str
    ssh_cpu_info: list
    ssh_kernel: str
    ssh_sys_users: list
    ssh_ip_macs: list
    ssh_packages: list


def get_rendered_html():
    connection = connect_database()
    scans = connection.execute('SELECT * FROM scansystem').fetchall()

    render_data = []
    for scan in scans:
        scan_controls = []
        scandatas = connection.execute(
            'SELECT * FROM scandata WHERE scansystem_id = ?',
            (str(scan[0]))).fetchall()
        for scandata in scandatas:
            control = connection.execute(
                'SELECT * FROM control WHERE id = ?',
                (str(scandata[5]))).fetchone()
            scan_controls.append(ControlInfo(
                contrid=control[0],
                description=control[1],
                requirement=control[2],
                name=scandata[1],
                transport=scandata[2],
                status=scandata[3]))

        audit_query = dict(connection.execute(
            'SELECT attribute, value FROM audit WHERE scansystem_id = ?',
            (str(scan[0]))).fetchall())

        if audit_query:
            audit = WMIScanInfo(
                OSname=audit_query['OSName'],
                OSArchitecture=audit_query['OSArchitecture'],
                OSVersion=audit_query['OSVersion'],
                NetBiosName=audit_query['NetBiosName'],
                Hostname=audit_query['Hostname'],
                Domain=audit_query['Domain'],
                Workgroup=audit_query['Workgroup'],
                PartOfDomain=audit_query['PartOfDomain'])
        else:
            audit = None

        """SNMP/SSH part"""
        try:
            SNMP_sysDescr_query = str(connection.execute('SELECT value FROM snmp_sysDescr \
                WHERE scansystem_id = ?', (str(scan[0]))).fetchall()[0][0])
        except IndexError:
            SNMP_sysDescr_query = None
        try:
            SNMP_interfaces_query = connection.execute('SELECT \
                interface, status FROM snmp_interfaces WHERE \
                scansystem_id = ?', (str(scan[0]))).fetchall()
        except Exception:
            SNMP_interfaces_query = None

        SSH_base_query = connection.execute('SELECT \
            value FROM ssh_audit WHERE \
            scansystem_id = ?', (str(scan[0]))).fetchall()
        if SSH_base_query:
            SNMP_audit_data = SNMPSSHScanInfo(
                sysDescr=SNMP_sysDescr_query,
                interfaces=SNMP_interfaces_query,
                ssh_sys_info=SSH_base_query[0][0],
                ssh_cpu_info=SSH_base_query[1][0].split('\n'),
                ssh_kernel=SSH_base_query[2][0],
                ssh_sys_users=SSH_base_query[3][0].split('\n'),
                ssh_ip_macs=SSH_base_query[4][0].split('\n'),
                ssh_packages=SSH_base_query[5][0].split('\n'))
        else:
            SNMP_audit_data = None

        render_data.append(BasicScanInfo(
            scanid=scan[0],
            scandate=scan[1],
            start_time=scan[2],
            end_time=scan[3],
            duration=scan[4],
            tests_count=scan[5],
            not_null_status=scan[6],
            controls=scan_controls,
            wmi_sys_info=audit,
            snmp_ssh=SNMP_audit_data))

    connection.close()

    env = Environment(
        loader=FileSystemLoader('templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('index.html')
    return template.render(scan_data=render_data)


def make_report():
    print('Create report...')
    whtml = HTML(string=get_rendered_html().encode('utf8'))
    wcss = CSS(filename='./templates/style.css')
    whtml.write_pdf('system_report.pdf', stylesheets=[wcss])
