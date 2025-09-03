"""
Safer YAML operations using yamlcore.
Provides safe loading/dumping with Norway fix and improved file handling.
"""

import yaml
from yamlcore import CCoreLoader, CCoreDumper
import os
from os import PathLike

DEFAULT_WIDTH = 1_000_000
DEFAULT_INDENT = 4

isa = isinstance

def load(f):
    if isa(f, (str, PathLike)):
        with open(os.fspath(f), 'rb') as fh:
            data = yaml.load(fh, Loader=CCoreLoader)
        return data
    return yaml.load(f, Loader=CCoreLoader)

def loads(x):
    return yaml.load(x, Loader=CCoreLoader)

def dumps(data, width=None, indent=None):
    if width is None:
        width = DEFAULT_WIDTH
    if indent is None:
        indent = DEFAULT_INDENT
    return yaml.dump(data, sort_keys=False, width=width, Dumper=CCoreDumper, indent=indent)

def dump(data, f, width=None, indent=None):
    if width is None:
        width = DEFAULT_WIDTH
    if indent is None:
        indent = DEFAULT_INDENT
    if isa(f, (str, PathLike)):
        with open(os.fspath(f), 'w', encoding='utf-8') as fh:
            yaml.dump(data, fh, sort_keys=False, width=width, Dumper=CCoreDumper, indent=indent)
        return
    yaml.dump(data, f, sort_keys=False, width=width, Dumper=CCoreDumper, indent=indent)
