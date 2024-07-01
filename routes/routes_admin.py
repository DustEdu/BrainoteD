import flask

from objects_functions import noteitem_functions, user_functions
import flask_login

import rfunctions
from main import app
from utility import get_provided_user, isNoteOfUser, isNitemOfUser, getSessionUser, isAdmin, respond


def isIdInvalid(value, param_name: str) -> None | str:
    if not value:
        return f"Error: Methods GET and DELETE require the {param_name} parameter."

    try: int(value)
    except ValueError:
        return f"Error: The {param_name} parameter must be a number."


"""
====================MODELS INTERACTIONS====================
"""


@app.route("/admin/users/", methods=["get"])
def users_route() -> flask.Response:
    return flask.make_response(
        rfunctions.get_users())


@app.route("/admin/user/", methods=["post"])
def post_user_route() -> flask.Response:
    if not (sessionkey := flask.session.get("sessionkey")):
        return respond("No sessionkey was found.")

    sessionuser = getSessionUser(sessionkey)
    if not isAdmin(sessionuser):
        return respond("Access denied.")

    _, status = get_provided_user(sessionuser)
    if status:  return respond(status)

    return respond(rfunctions.post_user())


@app.route("/admin/user/<user_id>", methods=["get", "delete"])
def user_route(user_id: int) -> flask.Response:
    if not (sessionkey := flask.session.get("sessionkey")):
        return respond("No sessionkey was found.")

    sessionuser = getSessionUser(sessionkey)
    if not isAdmin(sessionuser):
        return respond("Access denied.")

    match flask.request.method:
        case "GET":
            return rfunctions.get_user(user_id)
        case "DELETE":
            return rfunctions.delete_user(user_id)


@app.route("/admin/note/", methods=["post"])
def post_note_route() -> flask.Response:
    sessionkey = flask.session.get("sessionkey")
    if not sessionkey:
        return respond("No sessionkey was found.")

    sessionuser = getSessionUser(sessionkey)
    if not isAdmin(sessionuser):
        return respond("Access denied.")

    user, status = get_provided_user(sessionuser)
    if status:  return respond(status)

    return user_functions.create_note(
        userid=user.ID,
        name=flask.request.args.get("name"),
        content=flask.request.args.get("content"),
    )


@app.route("/admin/note/<note_id>", methods=["get", "delete"])
def note_route(note_id: int = None) -> flask.Response:
    sessionkey = flask.session.get("sessionkey")
    if not sessionkey:
        return respond("No sessionkey was found.")

    sessionuser = getSessionUser(sessionkey)
    if not isAdmin(sessionuser):
        return respond("Access denied.")

    user, status = get_provided_user(sessionuser)
    if status:  return respond(status)

    # Checks and validations
    if errmsg := isIdInvalid(note_id, param_name="note_id"):
        return errmsg

    # Check for note belonging if sessionuser is not admin
    if not (isNoteOfUser(note_id, user) or isAdmin(user)):
        return f"No note with id#{note_id} was found for this specific user."

    #  ===== Executing corresponding HTTP-method =====

    match flask.request.method:
        case "GET":
            return rfunctions.get_note(int(note_id))
        case "DELETE":
            return rfunctions.delete_note(int(note_id))


@app.route("/admin/noteitem/<noteitem_id>", methods=["get", "delete", "put"])
def noteitem_route(nitem_id: int = None) -> flask.Response:
    sessionkey = flask.session.get("sessionkey")
    if not sessionkey:
        return respond("No sessionkey was found.")

    sessionuser = getSessionUser(sessionkey)
    if not isAdmin(sessionuser):
        return respond("Access denied.")

    user, status = get_provided_user(sessionuser)
    if status:  return respond(status)

    # Validations and checks
    if errmsg := isIdInvalid(nitem_id, param_name="noteitem_id"):
        return respond(errmsg)

    if not isNitemOfUser(nitem_id, user):
        return respond(f"No noteitem with id#{nitem_id} was found for this specific user.")

    #  ===== Executing corresponding HTTP-method =====

    match flask.request.method:
        case "POST":   return rfunctions.post_noteitem(nitem_id)
        case "GET":    return rfunctions.get_noteitem(nitem_id)
        case "DELETE":
            if noteitem_functions.delete(nitem_id):
                return respond(f"Item #{nitem_id} was successfully deleted!")
            else:
                return respond(f"ERROR: Could not find item by id #{nitem_id}.")
        case "PUT":
            content = str(flask.request.args.get("content"))
            if not content: return respond("Error: No content parameter given.")
            return respond(rfunctions.put_noteitem(nitem_id, content))


@app.route("/admin/noteitem/", methods=["post"])
def noteitem_route() -> flask.Response:
    sessionkey = flask.session.get("sessionkey")
    if not sessionkey:
        return respond("No sessionkey was found.")

    sessionuser = getSessionUser(sessionkey)
    if not isAdmin(sessionuser):
        return respond("Access denied.")

    user, status = get_provided_user(sessionuser)
    if status:  return respond(status)

    note_id = int(flask.request.args.get("note_id"))

    user = get_provided_user(sessionuser)

    # Check for note belonging if sessionuser is not admin
    if not isNoteOfUser(note_id, user):
        return respond(f"No note with id#{note_id} was found for this specific user.")

    return respond(response=rfunctions.post_noteitem(note_id))


#  ===== TESTS (not included to the actual project) =====

@app.route("/example_cookie/")
def cookie():
    foo_cookie = flask.request.cookies.get('foo')
    if not foo_cookie:
        res = flask.make_response("Setting a cookie")
        res.set_cookie('foo', 'bar', max_age=60*60*24*365*2)

    res = flask.make_response(f"Value of cookie foo is {foo_cookie}")
    return res


@app.route("/visits", methods=["post", "get", "delete", "put"])
def visits():
    method = flask.request.method

    if method == "POST":
        if "visits" not in flask.session:
            flask.session["visits"] = 0

        flask.session["visits"] += 1
        return flask.make_response(f"Total visits: {flask.session.get("visits")}")

    if method == "DELETE":
        flask.session.pop("visits", None)
        return flask.make_response("Visits deleted")
