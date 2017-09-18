import os
import unittest
from unittest import mock
from collections import OrderedDict
from app import stanzas
from app.stanzas import Stanza
from app.server import EzproxyServer

class ParseStanzaTestCase(unittest.TestCase):
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
        self.assertEqual(stanzas.parse_stanzas(self.test_text),
                self.test_raw_stanza_array, "Parsing does not match")

    def test_get_matching_origin(self):
        self.assertEqual(
                stanzas.search_proxy(
                    "http://libraries.mangolanguages.com",
                    self.stanzas
                ),
                ["Mango for Libraries - Chicago"]
            )


class TranslateUrlTestCase(unittest.TestCase):
    def test_translate(self):
        self.assertEqual(
            stanzas.translate_url_origin("http://www.example.com"),
            "http://www.example.com",
            "Origins do not match"
        )

    def test_translate_https(self):
        self.assertEqual(
            stanzas.translate_url_origin("https://www.example.com"),
            "https://www.example.com",
            "Origins do not match"
        )

    def test_translate_with_port(self):
        self.assertEqual(
            stanzas.translate_url_origin("http://www.example.com:80"),
            "http://www.example.com:80",
            "Origins do not match"
        )

class StanzaTestCase(unittest.TestCase):
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
        self.assertEqual(
                self.stanza.get_origins(),
                set([
                    "https://connect.mangolanguages.com",
                    "http://libraries.mangolanguages.com"
                ]),
                "Origins do not match."
            )


class EZProxyServerTestCase(unittest.TestCase):
    def mocked_login_request(self, **kwargs):
        class MockCookie:
            def __init__(self,cookie_name,cookie_value):
                self.cookie_name = cookie_name
                self.cookie_value = cookie_value
            def keys(self):
                return [self.cookie_name]
            def get(self,cookie_name):
                return self.cookie_value
        class MockResponse:
            def __init__(self,cookie_name,cookie_value):
                self.cookie_name = cookie_name
                self.cookie_value = cookie_value
                self.cookies = MockCookie(cookie_name, cookie_value)
        return MockResponse("EZProxyTest", "AbcDef123")
    
    @mock.patch('requests.post', side_effect=mocked_login_request)
    def test_login(self,mock_get):
        self.assertEqual(
            EzproxyServer.login("chilib-test.moody.edu","admin","password"),
            {"EZProxyTest": "AbcDef123"}
        )

    def mocked_request_form(self,cookies,allow_redirects):
        class MockResponse:
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
        if (cookies["EZProxyCHI"] != "AbcDef123"):
            return Exception("Authentication failed")
        return MockResponse()

    @mock.patch("requests.get", side_effect=mocked_request_form)
    def test_get_pid(self, mock_get):
        self.assertEqual(
            EzproxyServer.get_pid("example.com", {"EZProxyCHI":"AbcDef123"}),
            "7977"
        )

    def mocked_restart_request(self, **kwargs):
        class MockResponse:
            def __init__(self):
                self.text = """<html><body><h1>EZProxy</h1>
                EZproxy will restart in 5 seconds.
                </body></html>"""
        return MockResponse()
        
    def mocked_pid_response(self, *args):
        return 11111

    @mock.patch("requests.post", side_effect=mocked_restart_request)
    @mock.patch("app.server.EzproxyServer.get_pid", side_effect=mocked_pid_response)
    def test_restart_ezproxy(self,mock_get, mock_get2):
        server = EzproxyServer()
        self.assertTrue(server.restart_ezproxy("example.com", {"cookie":"value"}))

        
if __name__ == '__main__':
    unittest.main()
