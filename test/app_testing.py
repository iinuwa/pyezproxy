import os
import unittest
from collections import OrderedDict
from app import stanzas
from app.stanzas import Stanza

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

def mocked_login_request:
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data
class EZProxyServerTestCase:
    def
if __name__ == '__main__':
    unittest.main()
