#!/usr/bin/env python3
# Main module for scripts calling
from pathlib import Path
from db_handling import SQLiteHandling
from report import make_report
from time import gmtime, strftime
import importlib
import time

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
    start_time = strftime("%H:%M:%S", gmtime())
    start_time_diff = time.time()
    local_db.create_db()
    local_db.initial_scan()
    import_scripts()
    end_time = strftime("%H:%M:%S", gmtime())
    end_time_diff = time.time()
    duration = end_time_diff - start_time_diff
    local_db.add_time(start_time, end_time, duration)
    make_report()
    local_db.close()


if __name__ == "__main__":
    main()
