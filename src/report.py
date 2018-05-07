#!/usr/bin/env python3
# Module for report creating
from jinja2 import Environment, PackageLoader, FileSystemLoader, select_autoescape
from collections import namedtuple
from weasyprint import HTML, CSS
from db_handling import DatabaseError, connect_database
import datetime


SCAN_STRUCTURE = {
    'date': None,
    'longitude': None,
    'counter': None,
    'counter_not_null': None,
    'id': None,
    'header': None,
    'descr': None,
    'status': None,
    'filename': None,
    'requirements': None,
    'transport': None
}

def scan_info(longitude = None):
    connection = connect_database()
    curr = connection.cursor()

    SCAN_STRUCTURE['date'] = datetime.datetime.today().strftime('%Y-%m-%d')
    SCAN_STRUCTURE['longitude'] = longitude
    SCAN_STRUCTURE['counter'] = curr.execute("SELECT Count(*) FROM scandata").fetchall()[0][0]
    SCAN_STRUCTURE['counter_not_null'] = curr.execute("SELECT Count(*) FROM scandata WHERE status IS NOT NULL").fetchall()[0][0]

def get_rendered_html():
    connection = connect_database()
    curr = connection.cursor()

    control_script_info = namedtuple('control_script_info', 'filename, header, script_id, descr, requirement, status, transport')
    basic_scan_info = namedtuple('basic_scan_info', 'date, longitude, counter, counter_not_null')

    report_data = []
    scandata_ids = curr.execute("SELECT id FROM scandata").fetchall()

    for scan in scandata_ids:
        SCAN_STRUCTURE['id'] = scan[0]
        SCAN_STRUCTURE['header'] = curr.execute("SELECT header FROM control WHERE id = ?", str(scan[0])).fetchone()[0]
        SCAN_STRUCTURE['descr'] = curr.execute("SELECT descr FROM control WHERE id = ?", str(scan[0])).fetchone()[0]
        SCAN_STRUCTURE['status'] = curr.execute("SELECT status FROM scandata WHERE id = ?", str(scan[0])).fetchone()[0]
        SCAN_STRUCTURE['filename'] = curr.execute("SELECT filename FROM control WHERE id = ?", str(scan[0])).fetchone()[0]
        SCAN_STRUCTURE['requirements'] = curr.execute("SELECT requirement FROM control WHERE id = ?", str(scan[0])).fetchone()[0]
        SCAN_STRUCTURE['transport'] = curr.execute("SELECT transport FROM control WHERE id = ?", str(scan[0])).fetchone()[0]
        report_data.append(control_script_info(
            filename = SCAN_STRUCTURE['filename'], 
            header = SCAN_STRUCTURE['header'], 
            script_id = SCAN_STRUCTURE['id'], 
            descr = SCAN_STRUCTURE['descr'], 
            requirement = SCAN_STRUCTURE['requirements'], 
            status = SCAN_STRUCTURE['status'],
            transport = SCAN_STRUCTURE['transport']))

    scan_data = basic_scan_info(
        date = SCAN_STRUCTURE['date'], 
        longitude = SCAN_STRUCTURE['longitude'], 
        counter = SCAN_STRUCTURE['counter'], 
        counter_not_null = SCAN_STRUCTURE['counter_not_null'])

    env = Environment(
        loader = FileSystemLoader('templates'),
        autoescape = select_autoescape(['html', 'xml'])
    )

    template = env.get_template('index.html')
    return template.render(report_data = report_data, scan_data = scan_data)

def make_report():
    whtml = HTML(string=get_rendered_html().encode('utf8'))
    wcss = CSS(filename='./templates/style.css')
    whtml.write_pdf('sample_report.pdf',stylesheets=[wcss])