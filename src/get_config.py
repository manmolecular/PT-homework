#!/usr/bin/env python3
# Get configuration from json file
import json
from pathlib import Path

JSON_CONFIG = None
CONFIG_CONTEST = 'config.json'
CONFIG_DIR = 'configs'


def get_config():
    global JSON_CONFIG
    if not JSON_CONFIG:
        with Path('.').joinpath(CONFIG_DIR).joinpath(CONFIG_CONTEST).open() as f:
            JSON_CONFIG = json.load(f)
    return JSON_CONFIG
