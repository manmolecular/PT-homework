#!/usr/bin/env python3
# Module for report creating
from jinja2 import Environment, FileSystemLoader, select_autoescape
from collections import namedtuple
from weasyprint import HTML, CSS
from db_handling import DatabaseError, connect_database
from typing import NamedTuple
import ast


class control_info(NamedTuple):
    contrid: int
    description: str
    filename: str
    requirement: str
    name: str
    transport: str
    status: str


class basic_scan_info(NamedTuple):
    scanid: int
    scandate: str
    start_time: str
    end_time: str
    duration: str
    tests_count: int
    not_null_status: int
    controls: list

def get_rendered_html():
    connection = connect_database()
    curr = connection.cursor()

    scans = connection.execute('SELECT * FROM scansystem').fetchall()

    render_data = []
    for scan in scans:
        scan_controls = []
        scandatas = connection.execute('SELECT * FROM scandata WHERE scansystem_id = ?', (str(scan[0]))).fetchall()
        for scandata in scandatas:
            control = connection.execute('SELECT * FROM control WHERE id = ?', (str(scandata[5]))).fetchone()
            scan_controls.append(control_info(
                contrid=control[0],
                description=control[1],
                filename=control[2],
                requirement=control[3],
                name=scandata[1],
                transport=scandata[2],
                status=scandata[3]))
        
        render_data.append(basic_scan_info(
            scanid=scan[0],
            scandate=scan[1],
            start_time=scan[2],
            end_time=scan[3],
            duration=scan[4],
            tests_count=scan[5],
            not_null_status=scan[6],
            controls=scan_controls))

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
