#!/usr/bin/env python3
# Module for report creating
from jinja2 import Environment, PackageLoader, \
    FileSystemLoader, select_autoescape
from collections import namedtuple
from weasyprint import HTML, CSS
from db_handling import DatabaseError, connect_database
from typing import NamedTuple

SCAN_STRUCTURE = {
    'id': None,
    'header': None,
    'descr': None,
    'status': None,
    'filename': None,
    'requirements': None,
    'transport': None,
}


class control_script_info(NamedTuple):
    filename: str
    header: str
    script_id: int
    descr: str
    requirement: str
    status: str
    transport: str


class basic_scan_info(NamedTuple):
    scan_id: int
    date: str
    longitude: str
    counter: int
    counter_not_null: int


def get_rendered_html():
    connection = connect_database()
    curr = connection.cursor()

    report_data = []
    scandata_ids = curr.execute("SELECT id FROM scandata").fetchall()

    for scan in scandata_ids:
        from_control = curr.execute("SELECT * FROM control \
            WHERE id = ?", str(scan[0])).fetchone()
        from_scandata = curr.execute("SELECT * FROM \
            scandata WHERE id = ?", str(scan[0])).fetchone()

        SCAN_STRUCTURE['id'] = from_scandata[0]
        SCAN_STRUCTURE['header'] = from_scandata[1]
        SCAN_STRUCTURE['descr'] = from_control[1]
        SCAN_STRUCTURE['status'] = from_scandata[3]
        SCAN_STRUCTURE['filename'] = from_control[2]
        SCAN_STRUCTURE['requirements'] = from_control[3]
        SCAN_STRUCTURE['transport'] = from_scandata[2]
        report_data.append(control_script_info(
            filename=SCAN_STRUCTURE['filename'],
            header=SCAN_STRUCTURE['header'],
            script_id=SCAN_STRUCTURE['id'],
            descr=SCAN_STRUCTURE['descr'],
            requirement=SCAN_STRUCTURE['requirements'],
            status=SCAN_STRUCTURE['status'],
            transport=SCAN_STRUCTURE['transport']))

    system_data = []
    system_ids = curr.execute("SELECT id FROM scansystem").fetchall()
    for sys in system_ids:
        from_scansystem = curr.execute("SELECT * FROM scansystem \
            WHERE id = ?", str(sys[0])).fetchone()
        system_data.append(basic_scan_info(
            scan_id=from_scansystem[0],
            date=from_scansystem[1],
            longitude=from_scansystem[2],
            counter=from_scansystem[3],
            counter_not_null=from_scansystem[4]))

    env = Environment(
        loader=FileSystemLoader('templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('index.html')
    return template.render(
        report_data=report_data,
        scan_data=system_data)


def make_report():
    whtml = HTML(string=get_rendered_html().encode('utf8'))
    wcss = CSS(filename='./templates/style.css')
    whtml.write_pdf('sample_report.pdf', stylesheets=[wcss])
