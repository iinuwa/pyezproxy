"""Module for controlling EZProxy server instance"""
import time
import requests
from bs4 import BeautifulSoup

class EzproxyServer:
    """This is a class to represent an Ezproxy server instance"""
    def __init__(self, hostname):
        self.hostname = hostname
        self.auth_cookie = None
        self.pid = None

    def login(self, username, password):
        """Login to an instance of EZProxy"""
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
        return True

    def get_pid(self):
        """Get the current PID of EZProxy"""
        restart_url = "https://login." + self.hostname + "/restart"
        restart_form = requests.get(
            restart_url,
            cookies=self.auth_cookie,
            allow_redirects=False
        )
        pid = BeautifulSoup(restart_form.text, "html.parser") \
            .find_all(attrs={"name":"pid"})[0] \
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
            if BeautifulSoup(restart_request.text, "html.parser").h1.next_sibling.strip() == \
                    "EZproxy will restart in 5 seconds.":
                if no_wait is False:
                    time.sleep(5)
                self.get_pid()
            else:
                RuntimeError("Failed to restart server.")
        except RuntimeError:
            pass
        return self.pid
