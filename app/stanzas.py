"""This is a utility module for working with EZproxy stanzas"""

from urllib.parse import urlparse
from collections import OrderedDict
import requests
from bs4 import BeautifulSoup

class Stanza:
    """Class for EZProxy stanza type"""

    def __init__(self, stanza_array):
        self.name = stanza_array["name"]
        self.directives = stanza_array["config"]

    def get_directives(self):
        """Returns the directives of this stanza"""
        return self.directives

    def get_origins(self):
        """Returns set of origins for that this stanza matches"""

        directives = self.get_directives()
        origin_array = []
        for directive in directives:
            if directive in [
                    "URL", "Host", "H", "HostJavascript", "HJ"
                ]:
                if isinstance(directive, str):
                    origin_array.append(translate_url_origin(directives[directive]))
                elif isinstance(directive, list):
                    for i in directives[directive]:
                        origin_array.append(translate_url_origin(directives[directive][i]))
        return set(origin_array)

def parse_stanzas(stanza_text):
    """Function to parse database stanza files"""
    start = "START"
    end = "END"
    stanza_array = []
    started = False
    for line in stanza_text.splitlines():
        if line.strip():
            if start in line:
                started = True
                db_config = OrderedDict()
            elif end in line:
                started = False
                db_dict = OrderedDict()
                if 'Title' in db_config:
                    db_dict['name'] = db_config['Title']
                else:
                    db_dict['name'] = ""
                db_dict['config'] = db_config
                stanza_array.append(db_dict)
            elif started and line.startswith("#") is False:
                param = line.strip().split(' ', 1)
                key = param[0][:1] + param[0][1:]
                value = param[1]
                if key in db_config:
                    if isinstance(db_config[key], list) is False:
                        db_config[key] = [db_config[key]]
                    db_config[key].append(value)
                else:
                    db_config[key] = value
    return stanza_array

def search_proxy(origin_url, stanzas):
    """
    Search proxy instance for existing stanza with origin URL
    """
    matching_stanzas = []
    try:
        for stanza in stanzas:
            if origin_url in stanza.get_origins():
                matching_stanzas.append(stanza.name)
    except (AttributeError, TypeError):
        raise AssertionError(f"Expected a list of Stanzas. Got {type(stanzas)}")
    return matching_stanzas

def translate_url_origin(url):
    """Returns the origin URL of a given URL"""
    parsed_url = urlparse(url)
    origin = parsed_url.scheme + "://" + parsed_url.netloc
    return origin

def login(hostname,username,password):
    """Login to an instance of EZProxy"""
    login_url = "https://login." + hostname + "/login"
    restart_url = "https://login." + hostname + "/restart"
    credentials = {
            "user": username,
            "pass": password
        }

    auth = requests.post(
            login_url,
            data=credentials,
            allow_redirects=False
        )

    for key in auth.cookies.keys:
        if key.startswith("EZProxy"):
            authCookie = {key: auth.cookies.get(key)},
        else:
            assert(Exception("No authorized session found"))
    return authCookie

def get_pid(hostname,authCookie):
    """Get the current PID of EZProxy"""
    restart_form = requests.get(
            restart_url,
            data=credentials,
            cookies=authCookie,
            allow_redirects=False
        )
    pid = BeautifulSoup(restart_form.text).find_all(attrs={"name":"pid"})[0].attrs["value"]
    return pid

def restart_ezproxy(
    """Restart this instance of EZProxy"""
    restart_payload = {
            "pid": pid,
            "confirm": "RESTART"
        }

    restart_request = requests.post(restart_url, data=restart_payload,
        cookies=authCookie)
    
    return BeautifulSoup(restart_request.text).h1.next_sibling.strip() ==
        "EZproxy will restart in 5 seconds."
