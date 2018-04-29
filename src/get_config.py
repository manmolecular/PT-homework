#!/usr/bin/env python3
# Get configuration from json file
import json
import os.path

_json_config = None
_config_name = 'configs/config.json'

def get_full_path():
    my_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(my_path, _config_name)

def get_config():
    global _json_config
    if not _json_config:
        with open(get_full_path(),'r') as f:
            _json_config = json.load(f)
    return _json_config