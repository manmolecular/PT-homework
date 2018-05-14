#!/usr/bin/env python3
# Get configuration from json file
import json
from pathlib import Path

json_config = None
CONFIG_CONTEST = 'config.json'
CONFIG_DIR = 'configs'


def get_config():
    global json_config
    if not json_config:
        with Path('.').joinpath(CONFIG_DIR).joinpath(CONFIG_CONTEST).open() as f:
            json_config = json.load(f)
    return json_config
