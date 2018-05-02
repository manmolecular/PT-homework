#!/usr/bin/env python3
# Module for report creating
from jinja2 import Environment, PackageLoader, FileSystemLoader, select_autoescape
from collections import namedtuple

env = Environment(
    loader = FileSystemLoader('templates'),
    autoescape = select_autoescape(['html', 'xml'])
)

user_list = ['user {}'.format(n) for n in range(0, 10)]
print(user_list)
record = namedtuple('record','filename, script_id, descr, transports, status')
report_data = [record(filename=name,script_id='test',descr='test',transports='test',status='test') for name in user_list]

test_tpl = env.get_template('index.html')
rendered_html = test_tpl.render(report_data = report_data)

print(rendered_html)