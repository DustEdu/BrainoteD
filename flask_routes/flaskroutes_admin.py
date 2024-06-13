import flask

import noteitem_functions
import flask_login

import user_functions
from flask_routes import routes_functions
from main import app
from utility import get_provided_user, isNoteOfUser, isNitemOfUser, getSessionUser, isAdmin


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
def users_route():
    if flask.request.method == "GET":
        return flask.make_response(
            routes_functions.get_users())
    return "Only GET method is available."


@app.route("/admin/user/", methods=["post", "get", "delete"])
def user_route():
    if sessionkey := flask.session.get("sessionkey"):
        sessionuser = getSessionUser(sessionkey)
    else:
        return "No sessionkey was found."

    match flask.request.method:
        case "POST":
            if isAdmin(sessionuser): return routes_functions.post_user()
            else: return "POST user allowed only for ADMIN account."
        case "GET":
            return routes_functions.get_user(
                get_provided_user(sessionuser).id)
        case "DELETE":
            return routes_functions.delete_user(
                get_provided_user(sessionuser).id)


@app.route("/admin/note/", methods=["post"])
def post_note_route():  return note_route()


@app.route("/admin/note/<note_id>", methods=["get", "delete"])
def note_route(note_id: None|int = None):
    if sessionkey := flask.session.get("sessionkey"):
        sessionuser = getSessionUser(sessionkey)
    else:
        return "No sessionkey was found."

    user = get_provided_user(sessionuser)

    method = flask.request.method

    # Checks and validations
    if method != "POST":
        if errmsg := isIdInvalid(note_id, param_name="note_id"):
            return errmsg

        # Check for note belonging if sessionuser is not admin
        if not (isNoteOfUser(note_id, sessionuser) or isAdmin(sessionuser)):
            return f"No note with id#{note_id} was found for this specific user."

    # Executing corresponding HTTP-method

    match method:
        case "POST":
            return user_functions.create_note(
                userid=user.ID,
                name=flask.request.args.get("name"),
                content=flask.request.args.get("content"),
            )
        case "GET":
            return routes_functions.get_note(int(note_id))
        case "DELETE":
            return routes_functions.delete_note(int(note_id))


@app.route("/admin/noteitem/<obj_id>", methods=["post", "get", "delete", "put"])
def noteitem_route(arg_id: int = None):
    method = flask.request.method
    arg_name = "noteitem" if method != "POST" else "note"

    # Retrieving user by sessionkey
    sessionkey = flask.session.get("sessionkey")
    if not sessionkey:  return "No sessionkey was found."
    sessionuser = getSessionUser(sessionkey)

    # Validations and checks
    if method != "POST":
        if errmsg := isIdInvalid(arg_id, param_name=f"{arg_name}_id"):
            return errmsg

        # Check for note belonging if sessionuser is not admin
        if not (isNoteOfUser(arg_id, sessionuser) or isAdmin(sessionuser)):
            return f"No note with id#{arg_id} was found for this specific user."

        # Check belonging to sessionuser (unless executed by Admin)
        if not isAdmin(sessionuser):
            if method == "POST": isBelongs = isNoteOfUser(arg_id, sessionuser)
            else:                isBelongs = isNitemOfUser(arg_id, sessionuser)
            if not isBelongs:
                return f"No f{arg_name} with id#{arg_id} was found for this specific user."

    # Executing corresponding HTTP-method

    match method:
        case "POST":   return routes_functions.post_noteitem(arg_id)
        case "GET":    return routes_functions.get_noteitem(arg_id)
        case "DELETE":
            if noteitem_functions.delete(arg_id):
                return f"Item #{arg_id} was successfully deleted!"
            else:
                return f"ERROR: Could not find item by id #{arg_id}."
        case "PUT":
            content = str(flask.request.args.get("content"))
            if not content: return "Error: No content parameter given."
            return routes_functions.put_noteitem(arg_id, content)


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


@app.route("/check_flaskuser/")
@flask_login.login_required
def check_flaskuser():
    return flask_login.current_user
