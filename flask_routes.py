import flask
import routes
import flask_login

import sqlalchemy as db

from main import app, dbs
from ormmodels import User, Note, NoteItem


def validated_id(value: int | None, param_name: str) -> int | str:
    if not value:
        return f"Error: Methods GET and DELETE require the {param_name} parameter."

    try: value = int(value)
    except ValueError:
        return f"Error: The {param_name} parameter must be a number."
    return value


@app.route("/")
def index():
    return flask.make_response("Tf you wanted to see here bro? Want me to drop database?")


"""
====================AUTH====================
"""


@app.route('/register/')
def register_route():
    return flask.make_response(
        routes.register())


@app.route('/login/')
def login_route():
    resp, sessionkey = routes.login()
    if sessionkey:
        flask.session["sessionkey"] = sessionkey
    return flask.make_response(resp)


@app.route('/logout/')
@flask_login.login_required
def logout_route():
    sessionkey = flask.session.get("sessionkey")

    if not sessionkey:
        return flask.make_response("No sessionkey was found.")

    routes.logout(sessionkey)
    flask.session.pop("sessionkey")
    return flask.make_response("You have been logged out.")


"""
====================MODELS INTERACTIONS====================
"""


@app.route("/get_users/")
def users_route():
    return flask.make_response(
        routes.get_users())


"""
====================MODELS INTERACTIONS====================
"""


def get_user(user: flask_login.current_user) -> User | str:
    if user.username == "ADMIN":
        user_id = flask.request.args.get("id")

        if not user_id:
            return "No id was found. Probably, no id argument was provided."

        user = dbs.execute(
            db.select(User)
            .where(User.ID == user_id)
        ).one_or_none()

    return user


def isNoteOfUser(note_id: int, user: User) -> bool:
    if user.username == "ADMIN":
        return True

    note = dbs.execute(
        db.select(Note)
        .where(Note.ID == note_id)
    ).one_or_none()

    if note and note.user == user:
        return True

    return False


def isNitemOfUser(nitem_id: int, user: User) -> bool:
    if user.username == "ADMIN":
        return True

    nitem = dbs.execute(
        db.select(NoteItem)
        .where(NoteItem.ID == nitem_id)
    ).one_or_none()

    if nitem and nitem.note.user == user:
        return True

    return False


@app.route("/user/", methods=["post", "get", "delete"])
@flask_login.login_required
def user_route():
    method = flask.request.method
    respstr: str
    user_id = get_user(flask_login.current_user).id

    if method != "POST": user_id = validated_id(user_id, "user_id")

    # Executing corresponding HTTP-method
    if   flask.request.method == "POST":   respstr = routes.post_user()

    elif flask.request.method == "GET":    respstr = routes.get_user(user_id)
    elif flask.request.method == "DELETE": respstr = routes.delete_user(user_id)

    else:
        return f"Error: Unknown method. Allowed methods: {["post", "get", "delete"]}"

    return flask.make_response(respstr)


@app.route("/note/<note_id>", methods=["post", "get", "delete"])
@flask_login.login_required
def note_route(note_id: int = None):
    method = flask.request.method
    respstr: str

    # If method is not POST we're using note_id argument
    if method != "POST":
        note_id = validated_id(note_id, "note_id")

        # Checking if provided note id belongs to user unless user is ADMIN
        if not isNoteOfUser(note_id, flask_login.current_user):
            return f"No note with id#{note_id} was found for this specific user."

    # Executing corresponding HTTP-method

    if   method == "POST":   respstr = routes.post_note()

    elif method == "GET":    respstr = routes.get_note(note_id)
    elif method == "DELETE": respstr = routes.delete_note(note_id)

    else:
        return f"Error: Unknown method. Allowed methods: {["post", "get", "delete"]}"

    return flask.make_response(respstr)


@app.route("/noteitem/<obj_id>", methods=["post", "get", "delete", "put"])
@flask_login.login_required
def noteitem_route(obj_id: int = None):
    method = flask.request.method
    respstr: str

    if method == "POST":
        note_id: int = validated_id(obj_id, "note_id")
        if not isNoteOfUser(note_id, flask_login.current_user):
            return f"No note with id#{note_id} was found for this specific user."
    else:
        noteitem_id: int = validated_id(obj_id, "noteitem_id")
        if not isNitemOfUser(noteitem_id, flask_login.current_user):
            return f"No noteitem with id#{noteitem_id} was found for this specific user."

    # Executing corresponding HTTP-method

    if   method == "POST":   respstr = routes.post_noteitem(note_id)

    elif method == "GET":    respstr = routes.get_noteitem(noteitem_id)
    elif method == "DELETE": respstr = routes.delete_noteitem(noteitem_id)
    elif method == "PUT":
        content = str(flask.request.args.get("content"))
        if not content: return "Error: No content parameter given."
        respstr = routes.put_noteitem(noteitem_id, content)

    else:
        return f"Error: Unknown method. Allowed methods: {["post", "get", "delete", "put"]}"

    return flask.make_response(respstr)


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
