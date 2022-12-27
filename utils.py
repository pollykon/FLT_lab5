import yaml

class Types:
    term = 0
    nterm = 1

def read_config(filepath):
    with open(filepath, 'rt') as f:
        config = yaml.full_load(f.read())
    return config

