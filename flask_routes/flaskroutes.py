import flask

import note_functions
import noteitem_functions
from flask_routes import routes_functions

from main import app
import user_functions
from utility import get_provided_user, isNoteOfUser, isNitemOfUser, getSessionUser, isAdmin


def respond(status: str = "Success", response=None):
    return flask.make_response(flask.jsonify(dict(
        status=status,
        response=response
    )))


@app.route("/")
def index():
    return flask.make_response("Tf you wanted to see here bro? Want me to drop database?")


"""
===============USER routes===============
"""


@app.route('/user/', methods=["get", "put"])
def user_info():
    if sessionkey := flask.session.get("sessionkey"):
        sessionuser = getSessionUser(sessionkey)
    else:
        return respond("No sessionkey was found.")

    match flask.request.method:
        case "PUT":
            return respond("Not implemented.")
        case "GET":
            return respond("Not implemented.")


@app.route('/user/notes/', methods=["post", "get"])
def user_notes():
    if sessionkey := flask.session.get("sessionkey"):
        sessionuser = getSessionUser(sessionkey)
    else:
        return respond("No sessionkey was found.")

    match flask.request.method:
        case "POST": return respond(response=user_functions.create_note(
            userid=sessionuser.ID,
            name=flask.request.args.get("name"),
            content=flask.request.args.get("content"),
        ))
        case "GET":  return respond(response=user_functions.get_notes(sessionuser.ID))


"""
===============NOTE routes===============
"""


@app.route('/note/<noteid>', methods=["delete"])
def note_info(noteid: int):
    if sessionkey := flask.session.get("sessionkey"):
        sessionuser = getSessionUser(sessionkey)
    else:
        return respond("No sessionkey was found.")

    if not (isNoteOfUser(noteid, sessionuser) or isAdmin(sessionuser)):
        return respond(f"No note with id#{noteid} was found for this specific user.")

    if note_functions.delete(noteid):
        return respond()
    else:
        return respond("Failed to delete note.")


@app.route('/note/<noteid>/items/', methods=["post", "get"])
def note_items(noteid: int):
    if sessionkey := flask.session.get("sessionkey"):
        sessionuser = getSessionUser(sessionkey)
    else:
        return respond("No sessionkey was found.")

    if not (isNoteOfUser(noteid, sessionuser) or isAdmin(sessionuser)):
        return respond(f"No note with id#{noteid} was found for this specific user.")

    match flask.request.method:
        case "POST": return respond(response=note_functions.create_item(noteid))
        case "GET":  return respond(response=dict(notes=note_functions.get_items(noteid)))


"""
===============NOTEITEM routes===============
"""


@app.route('/noteitem/<nitemid>', methods=["delete", "put", "get"])
def noteitem(nitemid: int):
    if sessionkey := flask.session.get("sessionkey"):
        sessionuser = getSessionUser(sessionkey)
    else:
        return respond("No sessionkey was found.")

    if not (isNitemOfUser(nitemid, sessionuser) or isAdmin(sessionuser)):
        return respond(f"No noteitem with id#{nitemid} was found for this specific user.")

    match flask.request.method:
        case "GET": return respond(response=noteitem_functions.get(nitemid))
        case "PUT": return respond(response=noteitem_functions.edit(
            nitemid,
            content=flask.request.args.get("content")   or None,
            itemtype=flask.request.args.get("itemtype") or None
        ))
        case "DELETE":
            if noteitem_functions.delete(nitemid):  return respond()
            else:                                   return respond("Failed to delete note.")


"""
====================AUTH====================
"""


@app.route('/register/', methods=["post"])
def register_route():
    username, password = flask.request.form["username"], flask.request.form["password"]

    return flask.make_response(
        routes_functions.register(username, password))


@app.route('/login/', methods=["post"])
def login_route():
    if flask.session.get("sessionkey"):
        return flask.make_response("Already logged in.")

    username =  str(flask.request.form["username"])
    password =  str(flask.request.form["password"])
    # remember = bool(flask.request.form["remember"])

    resp, sessionkey = routes_functions.login(username, password, remember=False)
    if sessionkey:
        flask.session["sessionkey"] = sessionkey
    return flask.make_response(resp)


@app.route('/logout/', methods=["post"])
def logout_route():
    if not (sessionkey := flask.session.get("sessionkey")):
        return flask.make_response("No sessionkey was found.")

    routes_functions.logout(sessionkey)
    flask.session.pop("sessionkey")
    return flask.make_response("You have been logged out.")
