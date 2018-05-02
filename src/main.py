#!/usr/bin/env python3
# Main module for scripts calling
from transports import *
from db_handling import *
from report import *
import os
import importlib
import time

_database = 'database.db'
_scriptdir = 'scripts'

# Import all scripts from folder
def import_scripts():
    for file in os.listdir('./' + _scriptdir):
            if file.endswith('.py') and file != '__init__.py':
                status = importlib.import_module(_scriptdir + '.' + file[:-3]).main()
                script_id = int(file[0:3])
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