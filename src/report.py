#!/usr/bin/env python3
# Module for report creating
from jinja2 import Environment, PackageLoader, FileSystemLoader, select_autoescape
from collections import namedtuple
from weasyprint import HTML, CSS
from db_handling import *

report_data = []
record = namedtuple('record','filename, header, script_id, descr, requirement, status')

env = Environment(
    loader = FileSystemLoader('templates'),
    autoescape = select_autoescape(['html', 'xml'])
)

def get_rendered_html():
    db = get_db_obj()
    curr = db.cursor()
    scandata_ids = curr.execute("SELECT id FROM scandata").fetchall()
    for scan in scandata_ids:
        scan_id = scan[0]
        scan_header = curr.execute("SELECT header FROM control WHERE id = ?", str(scan[0])).fetchone()[0]
        scan_descr = curr.execute("SELECT descr FROM scandata WHERE id = ?", str(scan[0])).fetchone()[0]
        scan_status = curr.execute("SELECT status FROM scandata WHERE id = ?", str(scan[0])).fetchone()[0]
        scan_filename = curr.execute("SELECT filename FROM control WHERE id = ?", str(scan[0])).fetchone()[0]
        scan_requirements = curr.execute("SELECT requirement FROM control WHERE id = ?", str(scan[0])).fetchone()[0]

        report_data.append(record(filename = scan_filename, header = scan_header, script_id = scan_id, 
            descr = scan_descr, requirement = scan_requirements, status = scan_status))

    template = env.get_template('index.html')
    return template.render(report_data = report_data)

def make_report():
    whtml = HTML(string=get_rendered_html().encode('utf8'))
    wcss = CSS(filename='./templates/style.css')
    whtml.write_pdf('sample_report.pdf',stylesheets=[wcss])