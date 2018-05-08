#!/usr/bin/env python3
# Module for report creating
from jinja2 import Environment, PackageLoader, \
    FileSystemLoader, select_autoescape
from collections import namedtuple
from weasyprint import HTML, CSS
from db_handling import DatabaseError, connect_database
from typing import NamedTuple
import ast

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
    curr_test: list

# Get rendered html
# Basic idea: we make scan of system and this scan is marked with id
# (for example, 1). For this scan we put all of passed controls
# in scandata table with _same_ id (for our example, 1). 

# Scandata (id, list(info about every control))

# After this, when we render report, we take _system scan_
# and search results of _controls testing_ on it.
# On fingers: system scan id = 1, than scandata results = 1
# That's how we do it - all information about every scan
# will be saved.

def get_rendered_html():
    connection = connect_database()
    curr = connection.cursor()

    render_data = []
    scan_count = curr.execute("SELECT id FROM scansystem").fetchall()

    # Look at all scans of our system from db 
    for full_scan_id in scan_count:
        
        # Find all controls that we test on current full scan of system
        this_scan_controls = ast.literal_eval(
            curr.execute("SELECT * FROM scandata \
            WHERE id = ?", str(full_scan_id[0])).fetchone()[1])

        # List of info about every control from this sysscan
        list_of_controls_info = []
        
        # For all controls from scan we retrieve all information
        for curr_control in this_scan_controls:
            from_db_info = curr.execute("SELECT * FROM control \
                WHERE id = ?", [str(curr_control[0])]).fetchone()
            SCAN_STRUCTURE['id'] = curr_control[0]
            SCAN_STRUCTURE['header'] = curr_control[1]
            SCAN_STRUCTURE['descr'] = from_db_info[1]
            SCAN_STRUCTURE['status'] = curr_control[3]
            SCAN_STRUCTURE['filename'] = from_db_info[2]
            SCAN_STRUCTURE['requirements'] = from_db_info[3]
            SCAN_STRUCTURE['transport'] = curr_control[2]
            list_of_controls_info.append(control_script_info(
                filename=SCAN_STRUCTURE['filename'],
                header=SCAN_STRUCTURE['header'],
                script_id=SCAN_STRUCTURE['id'],
                descr=SCAN_STRUCTURE['descr'],
                requirement=SCAN_STRUCTURE['requirements'],
                status=SCAN_STRUCTURE['status'],
                transport=SCAN_STRUCTURE['transport']))

        # Get major debug info from scanning of system (date, time, etc.)
        from_db_fullscan_info = curr.execute("SELECT * FROM scansystem \
            WHERE id = ?", str(full_scan_id[0])).fetchone()

        # Get list of all data that we must render to pdf (controls info
        # + sys info of scan)
        render_data.append(basic_scan_info(
            scan_id=from_db_fullscan_info[0],
            date=from_db_fullscan_info[1],
            longitude=from_db_fullscan_info[2],
            counter=from_db_fullscan_info[3],
            counter_not_null=from_db_fullscan_info[4],
            curr_test = list_of_controls_info))

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
