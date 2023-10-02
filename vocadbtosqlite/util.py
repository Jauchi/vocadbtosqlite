import json


def parse_json(location):
    c = None
    with open(location, 'r') as fd:
        content = fd.read()
        c = json.loads(content)
    return c
