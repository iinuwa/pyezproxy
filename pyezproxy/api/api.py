import sys
import json
from flask import Flask, Response, request
from pyezproxy.server import EzproxyServer
from pyezproxy.stanzas import StanzaUtil

args = sys.argv
server = None


app = Flask(__name__)


def start(hostname, base_dir, username):
    global server
    global app
    server = EzproxyServer(hostname, base_dir)
    server.login(username)
    app.run()


@app.route("/")
def status():
    return Response(json.dumps(server.options), mimetype="application/json")


@app.route("/stanzas", methods=["GET", "POST"])
def stanzas_router():
    """
    Retrieves stanzas or create a stanza
    POST request takes the following JSON schema:
    {
        "text": "Title Example Database\nURL http://www.example.com"
    }
    """

    if request.method == "GET":
        return get_stanzas()
    elif request.method == "POST":
        return create_stanza(request.get_json().get("text"))


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


def create_stanza(stanza_text):
    stanza = StanzaUtil.parse_stanza(stanza_text)
    server.stanzas.append(stanza)
    return "Stanza created.", 201


@app.route("/stanzas/<int:position>", methods=["GET", "PUT", "PATCH"])
def stanza_detail_router(position):
    if request.method == "GET":
        return get_stanza_detail(position)
    elif request.method == "PUT":
        return update_stanza(position, request.get_json().get("text"))
    elif request.method == "PATCH":
        new_position = request.get_json().get("position")
        return move_stanza(position, new_position)


def get_stanza_detail(position):
    try:
        stanza = server.stanzas[position - 1]
    except IndexError:
        return "Stanza not found", 404

    return_json = {
            "position": position,
            "name": stanza.name,
            "group": stanza.get_group(),
            "directives": stanza.get_directives(),
            "origins": list(stanza.get_origins())
    }
    return Response(json.dumps(return_json), mimetype='application/json')


def update_stanza(position, stanza_text):
    server.stanzas[position - 1] = StanzaUtil.parse_stanza(stanza_text)
    return "Stanza updated.", 200


def move_stanza(current_position, new_position):
    if current_position == new_position:
        pass
    else:
        stanza = server.stanzas.pop(current_position - 1)
        server.stanzas.insert(new_position - 1, stanza)
        return "Stanza moved.", 200


if __name__ == "__main__":
    start(args[1], args[2], args[3])
