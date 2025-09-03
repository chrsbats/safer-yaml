"""
Safer YAML operations using yamlcore.
Provides safe loading/dumping with Norway fix and improved file handling.
"""

import yaml
from yamlcore import CCoreLoader, CCoreDumper
import pathlib 

isa = isinstance

def load(f):
    if isa(f, pathlib.PosixPath):
        f = str(f)
    if isa(f, str):
        with open(f, 'rb') as f:
            data = yaml.load(f, Loader=CCoreLoader)
        return data
    return yaml.load(f, Loader=CCoreLoader)

def loads(x):
    return yaml.load(x, Loader=CCoreLoader)

def dumps(data, width=1000000):
    return yaml.dump(data, sort_keys=False, width=width, Dumper=CCoreDumper, indent=4)

def dump(data, f, width=1000000):
    if isa(f, pathlib.PosixPath):
        f = str(f)
    if isa(f, str):
        with open(f, 'w') as f:
            yaml.dump(data, f, sort_keys=False, width=width, Dumper=CCoreDumper, indent=4)
        return
    yaml.dump(data, f, Dumper=CCoreDumper)
