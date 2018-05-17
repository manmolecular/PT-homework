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


class WMIScanInfo(NamedTuple):
    OSname: str
    OSArchitecture: str
    OSVersion: str
    NetBiosName: str
    Hostname: str
    Domain: str
    Workgroup: str


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

        audit_query = connection.execute(
            'SELECT * FROM audit WHERE id = ?',
            (str(scandata[6]))).fetchone()

        audit = WMIScanInfo(
            OSname=audit_query[1],
            OSArchitecture=audit_query[2],
            OSVersion=audit_query[3],
            NetBiosName=audit_query[4],
            Hostname=audit_query[5],
            Domain=audit_query[6],
            Workgroup=audit_query[7])

        render_data.append(BasicScanInfo(
            scanid=scan[0],
            scandate=scan[1],
            start_time=scan[2],
            end_time=scan[3],
            duration=scan[4],
            tests_count=scan[5],
            not_null_status=scan[6],
            controls=scan_controls,
            wmi_sys_info=audit))

    connection.close()

    env = Environment(
        loader=FileSystemLoader('templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('index.html')
    return template.render(scan_data=render_data)


def make_report():
    whtml = HTML(string=get_rendered_html().encode('utf8'))
    wcss = CSS(filename='./templates/style.css')
    whtml.write_pdf('sample_report.pdf', stylesheets=[wcss])
