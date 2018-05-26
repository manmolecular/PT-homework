from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML, CSS

from ssh_info import get_ssh_info

def get_rendered_html():
    render_data = {
        'ssh_audit': get_ssh_info()
        'sql_audit': get_sql_info()
    }

    env = Environment(
        loader=FileSystemLoader('hackathon_report'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('index.html')
    return template.render(scan_data=render_data)

def make_hackathon_report():
    whtml = HTML(string=get_rendered_html().encode('utf8'))
    wcss = CSS(filename='./templates/style.css')
    whtml.write_pdf('hackathon.pdf', stylesheets=[wcss])

make_hackathon_report()