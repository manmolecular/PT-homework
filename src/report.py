#!/usr/bin/env python3
# Module for report creating
from jinja2 import Environment, PackageLoader, FileSystemLoader, select_autoescape
from collections import namedtuple
from weasyprint import HTML, CSS
from db_handling import DatabaseError, connect_database
import datetime

global_scan = {
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

def scan_info(longitude):
    connection = connect_database()
    curr = connection.cursor()

    global_scan['date'] = datetime.datetime.today().strftime('%Y-%m-%d')
    global_scan['longitude'] = longitude
    global_scan['counter'] = curr.execute("SELECT Count(*) FROM scandata").fetchall()[0][0]
    global_scan['counter_not_null'] = curr.execute("SELECT Count(*) FROM scandata WHERE status IS NOT NULL").fetchall()[0][0]

def get_rendered_html():
    connection = connect_database()
    curr = connection.cursor()

    control_script_info = namedtuple('control_script_info', 'filename, header, script_id, descr, requirement, status, transport')
    basic_scan_info = namedtuple('basic_scan_info', 'date, longitude, counter, counter_not_null')

    report_data = []
    scandata_ids = curr.execute("SELECT id FROM scandata").fetchall()

    for scan in scandata_ids:
        global_scan['id'] = scan[0]
        global_scan['header'] = curr.execute("SELECT header FROM control WHERE id = ?", str(scan[0])).fetchone()[0]
        global_scan['descrt'] = curr.execute("SELECT descr FROM control WHERE id = ?", str(scan[0])).fetchone()[0]
        global_scan['status'] = curr.execute("SELECT status FROM scandata WHERE id = ?", str(scan[0])).fetchone()[0]
        global_scan['filename'] = curr.execute("SELECT filename FROM control WHERE id = ?", str(scan[0])).fetchone()[0]
        global_scan['requirements'] = curr.execute("SELECT requirement FROM control WHERE id = ?", str(scan[0])).fetchone()[0]
        global_scan['transport'] = curr.execute("SELECT transport FROM control WHERE id = ?", str(scan[0])).fetchone()[0]
        report_data.append(control_script_info(
            filename = global_scan['filename'], 
            header = global_scan['header'], 
            script_id = global_scan['id'], 
            descr = global_scan['descr'], 
            requirement = global_scan['requirements'], 
            status = global_scan['status'],
            transport = global_scan['transport']))

    scan_data = basic_scan_info(
        date = global_scan['date'], 
        longitude = global_scan['longitude'], 
        counter = global_scan['counter'], 
        counter_not_null = global_scan['counter_not_null'])

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