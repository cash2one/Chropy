import pydoc
import json
import os
import sys
import subprocess
import urllib2
import time
import random

from ws4py.client import WebSocketBaseClient

BROWSER_JSON_PATH = os.sep.join(['..','proto','protocol.json'])

CHROME_LINUX_PATH = "/opt/google/chrome-unstable/chrome"
DEVTOOLS_JSON_HOME = 'http://127.0.0.1:{PORT}/json'


def get_browser_api_json(api_path=BROWSER_JSON_PATH):
    return json.loads(open(BROWSER_JSON_PATH,'r').read())

class ParameterAPI(object):
    UNKNOWN_TYPE = "UNKNOWN"
    def __init__(self, init_dict):
        self._raw = init_dict
        self.name = init_dict['name']
        if 'type' in init_dict:
            self.vtype = pydoc.locate(init_dict['type'])
        elif '$ref' in init_dict:
            self.vtype = "RefType-" + init_dict['$ref']
        else:
            self.vtype = ParameterAPI.UNKNOWN_TYPE
    def __repr__(self):
        return "<Parameter {name} {typ}>".format(name=self.name, typ=str(self.vtype))

class CommandAPI(object):
    def __init__(self, init_dict,domain=None):
        self._raw = init_dict
        self.domain = domain
        if self.domain:
            self._domain_name = self.domain.name
        else:
            self._domain_name = "NoDomain?"
        self.name = init_dict['name']
        if 'description' in init_dict:
            self.description = init_dict['description']
        else:
            self.description = ""
        if 'parameters' in init_dict:
            self.parameters = [ParameterAPI(param) for param in init_dict['parameters']]
        if 'returns' in init_dict:
            self.returns = [ParameterAPI(retval) for retval in init_dict['returns']]

    def __repr__(self):
        return "<Command {domain}::{api}{desc}>".format(api=self.name, domain=self._domain_name, desc=(" (" + self.description + ")") if self.description  else "")

# TODO: Impl. type discovery, register the types globally or maintain a dict of them or something in Chropy?
class TypeAPI(object):
    def __init__(self, init_dict, domain):
        self.domain = domain

class DomainAPI(object):
    def __init__(self, init_dict):
        self._raw = init_dict
        self.name = init_dict['domain']

#       if 'types' in init_dict:
#            self._types = [TypeAPI()]
        if 'commands' in init_dict:
            self._commands = [CommandAPI(cmd, domain=self) for cmd in init_dict['commands']]

        for _cmd in self._commands:
            if _cmd not in self.__dict__:
                self.__dict__[_cmd.name] = _cmd
            else:
                    raise Exception("Overwriting something in classdict")

    def __repr__(self):
        return "<API Domain {api}>".format(api=self.name)

    @property
    def cmdlist(self):
        return self._commands

    @property
    def commands(self):
        return dict([(d.name, d) for d in self._commands])

def build_api_objects():
    api_json = get_browser_api_json()
    domains = [DomainAPI(d) for d in api_json['domains']]
    return dict([(d.name, d) for d in domains])


class Chropy(object):
    def __init__(self):
        self._api_objects = build_api_objects()
        self._proc = None

    @property
    def domains(self):
        return self._api_objects

    def _is_running(self):
        if not self._proc or self._proc.poll():
            return False
        return True

    def launch_browser(self,port=None,path=None):
        if port is None:
            port = random.randint(10000,20000)
        if self._is_running():
            raise Exception("self._proc already up, create a new Chropy instance")

        if 'linux' in sys.platform:
            if path:
                return self._launch_chrome_headless_linux(port,path=path)
            return self._launch_chrome_headless_linux(port)
        raise Exception("Failed to launch chrome")

    def _launch_chrome_headless_linux(self, port,path=CHROME_LINUX_PATH, skip_check=False):
        self._port = port
        self._proc = subprocess.Popen([path,'--headless', '--remote-debugging-port=' + str(port)], stderr=subprocess.PIPE, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        if not skip_check:
            time.sleep(2.5)
            if not self._is_running():
                self._proc = None
                raise Exception("Chrome headless launch seems to have failed")



    def get_tabs(self):
        if not self._is_running():
            raise Exception("Can't talk to a dead browser...")
        return json.loads(urllib2.urlopen(DEVTOOLS_JSON_HOME.format(PORT=self._port)).read())


