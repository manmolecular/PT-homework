#!/usr/bin/env python3
# Main module for scripts calling
from pathlib import Path
from transports import *
from db_handling import *
from report import *
import importlib
import time
import os

_database = 'database.db'
_scriptdir = 'scripts'

# Import all scripts from folder
def import_scripts():
    script_dir = Path('./' + _scriptdir)
    for file in script_dir.glob('**/*.py'):
        if file.name != '__init__.py':
            status = importlib.import_module('.' + file.name[:-3], package = _scriptdir).main()
            script_id = int(file.name[0:3])
            add_control(script_id, status)

def is_db_exist():
    return os.path.isfile('./' + _database)

def main():
    start_time = time.time()
    if not is_db_exist():
        create_db()
    import_scripts()
    end_time = time.time() - start_time
    scan_info(end_time)
    make_report()

if __name__ == "__main__":
    main()