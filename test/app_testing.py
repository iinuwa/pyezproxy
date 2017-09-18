"""Module for test cases"""

import unittest
from unittest import mock
from collections import OrderedDict
from app import stanzas
from app.stanzas import Stanza
from app.server import EzproxyServer

class ParseStanzaTestCase(unittest.TestCase):
    """Test cases for stanza methods"""
    def setUp(self):
        self.test_text = """
        # This file contains database stanzas for resources only available
        # MAIN and DL students

        ####################################################################
        ###############   EBOOK TYPE RESOURCES    ##########################
        ####################################################################

        #### Sage Knowledge START #####
        Title Sage Knowledge
        URL http://knowledge.sagepub.com
        #### Sage Knowledge  END ####

        ####################################################################
        ###############    DATABASES PROVIDERS    ##########################
        ####################################################################

        #### IPA Source START ####
        Title IPA Source
        URL https://www.ipasource.com
        #### IPA Source END ####

        #### Mango for Libraries START ####
        Title Mango for Libraries - Chicago
        URL https://connect.mangolanguages.com/mbicl/start
        DJ mangolanguages.com
        DJ libraries.mangolanguages.com
        HJ http://libraries.mangolanguages.com/mbicl/start
        #### Mango for Libraries END ####
        """
        self.test_raw_stanza_array = [
            OrderedDict({
                "name": "Sage Knowledge",
                "config": OrderedDict({
                    "Title": "Sage Knowledge",
                    "URL": "http://knowledge.sagepub.com"
                })
            }),
            OrderedDict({
                "name": "IPA Source",
                "config": OrderedDict({
                    "Title": "IPA Source",
                    "URL": "https://www.ipasource.com"
                })
            }),
            OrderedDict({
                "name": "Mango for Libraries - Chicago",
                "config": OrderedDict({
                    "Title": "Mango for Libraries - Chicago",
                    "URL": "https://connect.mangolanguages.com/mbicl/start",
                    "DJ": [
                        "mangolanguages.com",
                        "libraries.mangolanguages.com"
                    ],
                    "HJ": "http://libraries.mangolanguages.com/mbicl/start"
                })
            })
        ]
        self.stanzas = []
        for stanza in self.test_raw_stanza_array:
            self.stanzas.append(Stanza(stanza))

    def test_parse(self):
        """Test for stanzas.parse_stanzas()"""
        self.assertEqual(
            stanzas.parse_stanzas(self.test_text),
            self.test_raw_stanza_array,
            "Parsing does not match"
        )

    def test_get_matching_origin(self):
        """Test for stanzas.search_proxy()"""
        self.assertEqual(
            stanzas.search_proxy(
                "http://libraries.mangolanguages.com",
                self.stanzas
            ),
            ["Mango for Libraries - Chicago"]
        )


class TranslateUrlTestCase(unittest.TestCase):
    """TestCases for origin-related methods"""
    def test_translate(self):
        """Simple test for HTTP URL"""
        self.assertEqual(
            stanzas.translate_url_origin("http://www.example.com"),
            "http://www.example.com",
            "Origins do not match"
        )

    def test_translate_https(self):
        """Simple test for HTTPS URL"""
        self.assertEqual(
            stanzas.translate_url_origin("https://www.example.com"),
            "https://www.example.com",
            "Origins do not match"
        )

    def test_translate_with_port(self):
        """Test that that port is added to the origin URL when port is specified
        in stanza directive"""
        self.assertEqual(
            stanzas.translate_url_origin("http://www.example.com:80"),
            "http://www.example.com:80",
            "Origins do not match"
        )

class StanzaTestCase(unittest.TestCase):
    """Test cases for Stanza class"""
    def setUp(self):
        stanza_array = OrderedDict({
            "name": "Mango for Libraries - Chicago",
            "config": OrderedDict({
                "Title": "Mango for Libraries - Chicago",
                "URL": "https://connect.mangolanguages.com/mbicl/start",
                "DJ": [
                    "mangolanguages.com",
                    "libraries.mangolanguages.com"
                ],
                "HJ": "http://libraries.mangolanguages.com/mbicl/start"
            })
        })
        self.stanza = stanzas.Stanza(stanza_array)

    def test_get_directives(self):
        """Test for Stanza.get_directives()"""
        self.assertEqual(
            self.stanza.get_directives(),
            OrderedDict({
                "Title": "Mango for Libraries - Chicago",
                "URL": "https://connect.mangolanguages.com/mbicl/start",
                "DJ": [
                    "mangolanguages.com",
                    "libraries.mangolanguages.com"
                ],
                "HJ": "http://libraries.mangolanguages.com/mbicl/start"
            }),
            "Directives do not match."
        )
    def test_get_origins(self):
        """Test for Stanza.get_origin()"""
        self.assertEqual(
            self.stanza.get_origins(),
            set([
                "https://connect.mangolanguages.com",
                "http://libraries.mangolanguages.com"
            ]),
            "Origins do not match."
        )

class EZProxyServerTestCase(unittest.TestCase):
    """Test cases for EzproxyServer class"""
    def mocked_login_request(self, **kwargs):
        """
        Override post request to send a mocked response
        for an EZProxy logon
        """
        class MockCookie:
            """Mock class emulating Requests CookieJar object"""
            def __init__(self, cookie_name, cookie_value):
                self.cookie_name = cookie_name
                self.cookie_value = cookie_value
            def keys(self):
                """Required to mock CookieJar object"""
                return [self.cookie_name]
            def get(self, *args):
                """Required to mock CookieJar object"""
                return self.cookie_value

        class MockLoginResponse:
            """Mock class for EZProxy login response"""
            def __init__(self, cookie_name, cookie_value):
                self.cookie_name = cookie_name
                self.cookie_value = cookie_value
                self.cookies = MockCookie(cookie_name, cookie_value)
        return MockLoginResponse("EZProxyTest", "AbcDef123")

    @mock.patch('requests.post', side_effect=mocked_login_request)
    def test_login(self, mock_get):
        """Test for EzproxyServer.login()"""
        server = EzproxyServer("example.com")
        self.assertTrue(server.login("admin", "password"))
        self.assertEqual(
            server.auth_cookie,
            {"EZProxyTest": "AbcDef123"}
        )

    def mocked_request_form(self, cookies, allow_redirects):
        """Override request.get for GET /restart on EZproxy server"""
        class MockRestartFormResponse:
            """Emulation of GET /restart on EZProxy server"""
            def __init__(self):
                self.text = '''<html>
                <body>
                <a href="/admin">Administration</a><hr>
                <h1>Restart EZproxy</h1>
                <p>You have requested that EZproxy be restarted.</p>
                <p>This release of EZproxy does not verify that the EZproxy configuration
                is valid.  If there are errors in
                config.txt or any file included by config.txt, EZproxy may shutdown.</p>
                <p></p><form action="/restart" method="post">
                <input type="hidden" name="pid" value="7977">
                If you still want EZproxy to restart, type RESTART in this box
                <input type="text" name="confirm" size="8" maxlength="8"> then click
                <input type="submit" value="here"></form>
                <p><a class="small" href="http://www.oclc.org/ezproxy/">Copyright
                (c) 1993-2016 OCLC (ALL RIGHTS RESERVED).</a></p>
                </body>
                </html>
                '''
        return MockRestartFormResponse()

    @mock.patch("requests.get", side_effect=mocked_request_form)
    def test_get_pid(self, mock_get):
        """Test for EzproxyServer.get_pid()"""
        server = EzproxyServer("example.com")
        server.auth_cookie = {"cookie":"value"}
        server.get_pid()
        self.assertEqual(
            server.pid,
            "7977"
        )

    def mocked_restart_request(self, url, *args, **kwargs):
        """Override POST request to EZproxy server for testing"""
        class MockRestartResponse:
            """Emulates POST /restart response from EZProxy"""
            def __init__(self):
                self.text = """<html><body><h1>EZProxy</h1>
                EZproxy will restart in 5 seconds.
                </body></html>"""
        return MockRestartResponse()

    @mock.patch("requests.post", side_effect=mocked_restart_request)
    def test_restart_ezproxy(self, mock_get):
        """Test for EzproxyServer.restart_ezproxy()"""
        server = EzproxyServer("example.com")
        server.auth_cookie = {"cookie":"value"}
        server.pid = 11111
        self.assertTrue(server.restart_ezproxy())


if __name__ == '__main__':
    unittest.main()
