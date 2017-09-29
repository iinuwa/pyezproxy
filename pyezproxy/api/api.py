import sys
import json
from flask import Flask, Response, request
from pyezproxy.server import EzproxyServer
from pyezproxy.stanzas import StanzaUtil

args = sys.argv
server = None


app = Flask(__name__)


def start(hostname, base_dir, username, password):
    global server
    global app
    server = EzproxyServer(hostname, base_dir)
    server.login(username, password)
    app.run()


@app.route("/")
def status():
    return Response(json.dumps(server.options), mimetype="application/json")


@app.route("/stanzas")
def get_stanzas():
    return_json = []

    for i in range(len(server.stanzas)):
        stanza = server.stanzas[i]
        stanza_info = {
            "position": i + 1,
            "name": stanza.name,
            "origins": list(stanza.get_origins())
        }
        if request.args.get("name") is not None:
            if stanza_info["name"].lower() \
                    .startswith(request.args.get("name").lower()):
                return_json.append(stanza_info)
        elif request.args.get("url") is not None:
            url = StanzaUtil.translate_url_origin(
                request.args.get("url"))
            for origin in stanza.get_origins():
                if StanzaUtil.match_origin_url(url, origin):
                    return_json.append(stanza_info)
                    break
        else:
            return_json.append(stanza_info)
    return Response(json.dumps(return_json), mimetype='application/json')


@app.route("/stanzas/<int:position>")
def get_stanza_detail(position):
    stanza = server.stanzas[position - 1]
    return_json = {
            "position": position,
            "name": stanza.name,
            "directives": stanza.directives
    }
    return Response(json.dumps(return_json), mimetype='application/json')


if __name__ == "__main__":
    start(args[1], args[2], args[3], args[4])
