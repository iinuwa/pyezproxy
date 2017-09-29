"""This is a utility module for working with EZproxy stanzas"""

from urllib.parse import urlparse
from collections import OrderedDict


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


class StanzaUtil:
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
                    value = param[1].strip()
                    if key in db_config:
                        if isinstance(db_config[key], list) is False:
                            db_config[key] = [db_config[key]]
                        db_config[key].append(value)
                    else:
                        db_config[key] = value
        return stanza_array

    def print_stanzas(stanzas):
        lines = []
        for stanza in stanzas:
            lines.append("#### " + stanza.name + " START ####")
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
