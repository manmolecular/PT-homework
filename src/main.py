#!/usr/bin/env python3
# Main module for scripts calling
import importlib
from datetime import datetime
from pathlib import Path

from db_handling import SQLiteHandling
from report import make_report

from audit import retrieve_audit_info

SCRIPT_DIR = 'scripts'
local_db = SQLiteHandling()


# Import all scripts from folder
def import_scripts():
    script_dir = Path('.').joinpath(SCRIPT_DIR)
    for file in script_dir.glob('**/*.py'):
        if file.name == '__init__.py':
            continue
        script_id = int(''.join(filter(str.isdigit, file.name)))
        script_name = file.name[:-3]
        status = importlib.import_module('.' + script_name,
                                         package=SCRIPT_DIR).main()
        local_db.add_control(script_id, script_name, status)


def main():
    start_time = datetime.now()

    local_db.create_db()
    local_db.initial_scan()
    local_db.add_audit()
    import_scripts()

    network_analysis = retrieve_audit_info()
    if network_analysis != None:
        local_db.add_SNMP_SSH_info(network_analysis[0], network_analysis[1])
    else:
        print('Warning: SNMP and SSH services is unavailable')

    end_time = datetime.now()
    duration = end_time - start_time

    local_db.add_time(
        start_time.time().isoformat(timespec='seconds'),
        end_time.time().isoformat(timespec='seconds'),
        round(duration.total_seconds(), 2))
    make_report()
    local_db.close()


if __name__ == "__main__":
    main()
