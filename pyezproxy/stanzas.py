"""This is a utility module for working with EZproxy stanzas"""

from os import path
from urllib.parse import urlparse
from collections import OrderedDict


class Stanza:
    """Class for EZProxy stanza type"""

    def __init__(self, stanza_array):
        self.name = stanza_array["name"]
        self.group = stanza_array["config"].get("Group", "Default")
        self.directives = None
        self.__set_directives(stanza_array["config"])

    def __set_directives(self, stanza_config):
        # Remove group key if already set
        directives = stanza_config
        if "Group" in stanza_config:
            del directives["Group"]
        self.directives = directives

    def get_directives(self):
        """Returns the directives of this stanza"""
        return self.directives

    def get_origins(self):
        """Returns set of origins for that this stanza matches"""

        directives = self.get_directives()
        origin_array = []
        for directive in directives:
            if directive in [
                "URL", "U", "Host", "H", "HostJavascript", "HJ"
            ]:
                if isinstance(directives[directive], str):
                    origin_array.append(StanzaUtil.translate_url_origin(
                        directives[directive]))
                elif isinstance(directives[directive], list):
                    for directive_str in directives[directive]:
                        origin_array.append(StanzaUtil.translate_url_origin(
                            directive_str))
        return set(origin_array)

    def get_group(self):
        """Returns group if specified in stanza directives"""
        return self.group

    def __sort_directives(self, key_tuple):
        # group goes first, then title, then everything else
        sorted_keys = {
            "Group": -2,
            "Title": -1
        }
        return sorted_keys.get(key_tuple[0], 0)


class StanzaUtil:
    shortcuts = {
        "T": "Title",
        "U": "URL",
        "H": "Host",
        "HJ": "HostJavascript",
        "D": "Domain",
        "DJ": "DomainJavascript"
    }

    def parse_stanzas(stanza_text):
        """Function to parse database stanza files"""
        stanza_array = []
        for stanza_text in (StanzaUtil.__extract_stanzas(stanza_text)):
            stanza_array.append(StanzaUtil.parse_stanza(stanza_text))
        return stanza_array

    def __extract_stanzas(stanzas_text):
        start = "START"
        end = "END"
        buffer = []
        started = False
        for line in stanzas_text.splitlines():
            if line.strip():  # Omits blank lines
                if start in line:
                    started = True
                    directives_text = []
                elif end in line:
                    started = False
                    buffer.append("\n".join(directives_text))
                elif started:
                    directives_text.append(line.strip())
        return buffer

    def parse_stanza(stanza_text):
        return_dict = {}
        db_config = OrderedDict()

        for line in stanza_text.splitlines():
            # Ignore comments in file.
            if line.strip() and line.startswith("#") is False:
                param = line.strip().split(' ', 1)
                # Force initial letter of key to be uppercase
                key = param[0][:1].upper() + param[0][1:]
                if key.upper() in StanzaUtil.shortcuts:
                    key = StanzaUtil.shortcuts.get(key)
                value = param[1].strip()
                if key in db_config:
                    if isinstance(db_config[key], list) is False:
                        db_config[key] = [db_config[key]]
                    db_config[key].append(value)
                else:
                    db_config[key] = value

        if db_config.get("IncludeFile") and not db_config.get("Title"):
            return_dict["name"] = path.split(db_config.get("IncludeFile"))[1]
        else:
            return_dict["name"] = db_config.get("Title")

        return_dict["config"] = db_config
        return Stanza(return_dict)

    def print_stanzas(stanzas):
        lines = []
        for stanza in stanzas:
            lines.append("#### " + stanza.name + " START ####")
            lines.append("Group " + stanza.group)
            directives = stanza.get_directives()
            for directive in directives:
                if isinstance(directives[directive], list):
                    for value in directives[directive]:
                        lines.append(directive + " " + value)
                else:
                    lines.append(directive + " " + directives[directive])
            lines.append("#### " + stanza.name + " END   ####")
            lines.append("")  # Append blank line between stanzas.
        return "\n".join(lines)

    def translate_url_origin(url):
        """Returns the origin URL of a given URL"""
        if "//" not in url:
            url = "//" + url
        parsed_url = urlparse(url)
        if parsed_url.scheme:
            origin = parsed_url.scheme + "://" + parsed_url.netloc
        else:
            origin = "//" + parsed_url.netloc
        return origin

    def match_origin_url(url, origin):
        if "//" not in url:
            parsed_url = urlparse("//" + url)
        else:
            parsed_url = urlparse(url)

        if "//" not in origin:
            parsed_origin = urlparse("//" + origin)
        else:
            parsed_origin = urlparse(origin)

        host_matches = (parsed_url.hostname == parsed_origin.hostname)

        if parsed_origin.scheme:
            scheme_matches = (parsed_url.scheme == parsed_origin.scheme)
        else:
            scheme_matches = True

        if parsed_origin.port:
            port_matches = (parsed_url.port == parsed_origin.port)
        else:
            port_matches = True

        return (host_matches and scheme_matches and port_matches)
