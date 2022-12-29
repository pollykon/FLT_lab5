import yaml

class Types:
    term = 0
    nterm = 1

def input_config():
    lines = []
    while True:
        try:
            lines.append(input())
        except EOFError:
            break

    lines = [i for i in lines if len(i)>0]
    return yaml.full_load('\n'.join(lines))

def read_config(filepath):
    with open(filepath, 'rt') as f:
        config = yaml.full_load(f.read())
    return config

