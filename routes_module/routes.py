import flask

from objects_functions import note_functions, noteitem_functions, user_functions
from routes_module import auth_functions

from main import app
from utility import isNoteOfUser, isNitemOfUser, getSessionUser, isAdmin, respond


@app.route("/")
def index():
    return flask.make_response("Tf you wanted to see here bro? Want me to drop database?")


"""
===============USER routes_module===============
"""


@app.route('/user/', methods=["get", "put"])
def user_info():
    sessionkey = flask.session.get("sessionkey")
    if not sessionkey:
        return respond("No sessionkey was found.")

    sessionuser = getSessionUser(sessionkey)

    # ===== Executing corresponding HTTP-method backend =====

    match flask.request.method:
        case "PUT":
            return respond("Not implemented.")
        case "GET":
            return respond("Not implemented.")


@app.route('/user/notes/', methods=["post", "get"])
def user_notes():
    sessionkey = flask.session.get("sessionkey")
    if not sessionkey:
        return respond("No sessionkey was found.")

    sessionuser = getSessionUser(sessionkey)

    # ===== Executing corresponding HTTP-method backend =====

    match flask.request.method:
        case "POST": return respond(response=user_functions.create_note(
            userid=sessionuser.ID,
            name=flask.request.args.get("name"),
            content=flask.request.args.get("content"),
        ))
        case "GET":  return respond(response=user_functions.get_notes(sessionuser.ID))


"""
===============NOTE routes_module===============
"""


@app.route('/note/<noteid>', methods=["delete"])
def note_info(noteid: int):
    sessionkey = flask.session.get("sessionkey")
    if not sessionkey:
        return respond("No sessionkey was found.")

    sessionuser = getSessionUser(sessionkey)

    if not (isNoteOfUser(noteid, sessionuser) or isAdmin(sessionuser)):
        return respond(f"No note with id#{noteid} was found for this specific user.")

    if note_functions.delete(noteid):
        return respond()
    else:
        return respond("Failed to delete note.")


@app.route('/note/<noteid>/items/', methods=["post", "get"])
def note_items(noteid: int):
    sessionkey = flask.session.get("sessionkey")
    if not sessionkey:
        return respond("No sessionkey was found.")

    sessionuser = getSessionUser(sessionkey)

    if not (isNoteOfUser(noteid, sessionuser) or isAdmin(sessionuser)):
        return respond(f"No note with id#{noteid} was found for this specific user.")

    # ===== Executing corresponding HTTP-method backend =====

    match flask.request.method:
        case "POST":
            return respond(response=note_functions.create_item(noteid))
        case "GET":
            return respond(response=dict(
                notes=[dict(
                    id=nitem.ID,
                    index=nitem.index,
                    content=nitem.content,
                    type=nitem.itemtype,
                ) for nitem in note_functions.get_items(noteid)]
            ))


"""
===============NOTEITEM routes_module===============
"""


@app.route('/noteitem/<noteitem_id>', methods=["delete", "put", "get"])
def noteitem(noteitem_id: int):
    sessionkey = flask.session.get("sessionkey")
    if not sessionkey:
        return respond("No sessionkey was found.")

    sessionuser = getSessionUser(sessionkey)

    if not isNitemOfUser(noteitem_id, sessionuser) or not isAdmin(sessionuser):
        return respond(f"No noteitem with id#{noteitem_id} was found for this specific user.")

    # ===== Executing corresponding HTTP-method backend =====

    match flask.request.method:
        case "GET":
            return respond(response=noteitem_functions.get(noteitem_id))

        case "PUT":
            return respond(response=noteitem_functions.edit(
                noteitem_id,
                content=flask.request.args.get("content")   or None,
                itemtype=flask.request.args.get("itemtype") or None
            ))

        case "DELETE":
            if noteitem_functions.delete(noteitem_id):
                return respond()
            else:
                return respond("Failed to delete note.")


"""
====================AUTH====================
"""


@app.route('/register/', methods=["post"])
def register_route():
    username = str(flask.request.form["username"])
    password = str(flask.request.form["password"])
    if not username or not password:
        return respond("Error: No parameters (username and/or password) given.")

    return flask.make_response(
        auth_functions.register(username, password))


@app.route('/login/', methods=["post"])
def login_route():
    if flask.session.get("sessionkey"):
        return respond("Already logged in.")

    username = str(flask.request.form["username"])
    password = str(flask.request.form["password"])
    if not username or not password:
        return respond("Error: No parameters (username and/or password) given.")

    sessionkey, status = auth_functions.login(username, password, remember=False)

    if status != "Success":
        return respond(status)

    if sessionkey:
        flask.session["sessionkey"] = sessionkey
        return respond(f"Login for user {username} successful! Sessionkey generated.")


@app.route('/logout/', methods=["post"])
def logout_route():
    sessionkey = flask.session.get("sessionkey")
    if not sessionkey:
        return flask.make_response("No sessionkey was found.")

    auth_functions.delete_session_by_key(sessionkey)
    flask.session.pop("sessionkey")
    return flask.make_response("You have been logged out.")
