import json
import os

BROWSER_JSON_PATH = os.sep.join(['..','proto','protocol.json'])

def get_browser_api_json(api_path=BROWSER_JSON_PATH):
    return json.loads(open(BROWSER_JSON_PATH,'r').read())


class ParameterAPI(object):
    def __init__(self, init_dict):
        self._name = init_dict['name']
        if 'type' in init_dict:
            self._type = init_dict['type']

class CommandAPI(object):
    def __init__(self, init_dict):
        self._name = init_dict['name']
        if 'description' in init_dict:
            self._description = init_dict['description']
        if 'parameters' in init_dict:
            self._parameters = [ParameterAPI(param) for param in init_dict['parameters']]
        if 'returns' in init_dict:
            self._returns = [ParameterAPI(retval) for retval in init_dict['returns']]

class DomainAPI(object):
    def __init__(self, init_dict):
        self._domain = init_dict['domain']
        if 'commands' in init_dict:
            self._cmds = [CommandAPI(cmd) for cmd in init_dict['commands']]


def build_api_objects():
    api_json = get_browser_api_json()
    domains = [DomainAPI(d) for d in api_json['domains']]
    return domains

api_objects = build_api_objects()

