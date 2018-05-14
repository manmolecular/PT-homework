#!/usr/bin/env python3
# Main module for scripts calling
import importlib
from datetime import datetime
from pathlib import Path

from db_handling import SQLiteHandling
from report import make_report

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
    import_scripts()

    end_time = datetime.now()
    duration = end_time - start_time

    local_db.add_time(
        start_time.time().isoformat(timespec='milliseconds'),
        end_time.time().isoformat(timespec='milliseconds'),
        duration.total_seconds())
    make_report()
    local_db.close()


if __name__ == "__main__":
    main()
