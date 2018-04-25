"""Module for controlling EZProxy server instance"""
import time
import requests
from bs4 import BeautifulSoup
from . import stanzas
from .stanzas import StanzaUtil


class EzproxyServer:
    """This is a class to represent an Ezproxy server instance"""
    def __init__(self, hostname, base_dir):
        self.hostname = hostname
        self.base_dir = base_dir
        self.__set_stanzas()
        self.__set_server_options()
        self.auth_cookie = None
        self.pid = None

    def __set_stanzas(self):
        with open(self.base_dir + "/config/databases.conf", "r") as stanza_file:
            self.stanzas = StanzaUtil.parse_stanzas(stanza_file.read())

    def __set_server_options(self):
        with open(self.base_dir + "/config/server.conf", "r") as options_file:
            options_array = []
            options_text = options_file.read()
            for line in options_text.splitlines():
                # Skip empty lines and comments
                if line.strip() and line.startswith("#") is False:
                    param = line.strip().split(' ', 1)
                    # Force inital letter of key to be uppercase
                    key = param[0][:1].upper() + param[0][1:]
                    value = param[1].strip()
                    options_array.append({key: value})
            self.options = options_array

    def login(self, username, password=None):
        """Login to an instance of EZProxy"""
        # Get password from usertext file
        if password is None:
            with open(self.base_dir + "/user.txt", "r") as auth_file:
                for line in auth_file.readlines():
                    if line.strip().startswith(username):
                        password = line.split(":")[1]
                        break

        login_url = "https://login." + self.hostname + "/login"
        credentials = {
            "user": username,
            "pass": password
        }

        auth = requests.post(
            login_url,
            data=credentials,
            allow_redirects=False
        )
        auth_cookie = {}
        for key in auth.cookies.keys():
            if key.startswith("EZProxy"):
                auth_cookie = {key: auth.cookies.get(key)}
            else:
                Exception("No authorized session found")
        self.auth_cookie = auth_cookie
        self.get_pid()
        return True

    def logout(self):
        response = requests.get(
            "https://" + self.hostname + "/logout",
            self.auth_cookie,
            allow_redirects=False
        )
        return response.ok

    def get_pid(self):
        """Get the current PID of EZProxy"""
        restart_url = "https://login." + self.hostname + "/restart"
        restart_form = requests.get(
            restart_url,
            cookies=self.auth_cookie,
            allow_redirects=False
        )
        pid = BeautifulSoup(restart_form.text, "html.parser") \
            .find_all(attrs={"name": "pid"})[0] \
            .attrs["value"]
        self.pid = pid

    def restart_ezproxy(self, no_wait=False):
        """Restart this instance of EZProxy"""
        restart_url = "https://login." + self.hostname + "/restart"
        restart_payload = {
            "pid": self.pid,
            "confirm": "RESTART"
        }

        try:
            restart_request = requests.post(
                restart_url,
                data=restart_payload,
                cookies=self.auth_cookie
            )
            if (BeautifulSoup(restart_request.text, "html.parser")
                .h1.next_sibling.strip() ==
                    "EZproxy will restart in 5 seconds."):
                if no_wait is False:
                    time.sleep(5)
                self.get_pid()
            else:
                RuntimeError("Failed to restart server.")
        except RuntimeError:
            pass
        return self.pid

    def get_stanzas(self):
        return self.stanzas

    def search_proxy(self, url=None, name=None):
        """
        Search proxy instance for existing stanza with origin URL
        """
        url_matches = set()
        name_matches = set()
        try:
            for i in range(len(self.get_stanzas())):
                stanza = self.get_stanzas()[i]
                if url:
                    for origin in stanza.get_origins():
                        if StanzaUtil.match_origin_url(url, origin):
                            url_matches.add((i, stanza.name))
                            break
                elif name and stanza.name.startswith(name):
                    name_matches.add((i, stanza.name))

            if bool(url_matches) and bool(name_matches):
                return url_matches & name_matches
            elif bool(url_matches):
                return url_matches
            elif bool(name_matches):
                return name_matches

        except (AttributeError, TypeError):
            raise AssertionError(
                f"Expected a list of Stanzas. Got {type(stanzas)}")
