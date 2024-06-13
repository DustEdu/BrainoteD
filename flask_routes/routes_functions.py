import flask
import sqlalchemy as db

import flask_routes.flaskroutes
from main import dbs
import user_functions, note_functions, noteitem_functions
from ormmodels import *
from utility import isUsernameTaken


def register_admin() -> str:
    username, password = "ADMIN", "ADMIN"

    dbs.add(User(username=username, password=password))
    dbs.commit()

    flask.redirect("login")

    return "ADMIN account was created."


def register(username: str, password: str) -> str:
    if username == "ADMIN":
        return "Cannot register own ADMIN account."

    if isUsernameTaken(username):
        return "Such user already exists. Please choose another username or login instead."

    if len(password) < 5:
        return "The password is too short: Password needs to be longer than 4 characters (like I really care lol bro)"

    dbs.add(User(username=username, password=password))
    dbs.commit()

    flask.redirect("login")

    return (f"User \"{username}\" registered successfully! "
            f"(bro what a dumb nickname u couldn't come up with anything better like seriously? "
            f"You should be ashamed.)")


def login(username: str, password: str, remember: bool) -> (str, None|str):
    user: User = dbs.execute(
        db.select(User)
        .where(User.username == str(username))
    ).one_or_none()

    if not user or not user[0].check_password(password):
        return "Invalid username or password.", None

    user = user[0]

    flask.session["username"] = user.username
    # flask_login.login_user(user, remember=remember)

    usersession = Session(user.ID)
    dbs.add(usersession)
    dbs.commit()

    return f"Login for user {user.username} successful! Sessionkey generated.", usersession.key


def logout(sessionkey: str) -> bool:
    # Flask logout
    # flask.logout_user()
    # flask.redirect(flask.url_for('login'))

    # DB logout
    dbs.execute(
        db.delete(Session)
        .where(Session.key == sessionkey)
    )
    dbs.commit()

    return True


"""
==========Users functions==========
"""


def get_users() -> dict:
    users = dbs.execute(
        db.select(User)
    ).all()
    res = ""
    if users:
        for n, i in users, enumerate(users):
            res += f"\nUser #{i}: {n[0]}\n"
    else: res = "No users."

    return res


def get_user(user_id: int) -> str:
    user = dbs.execute(
        db.select(User)
        .where(User.ID == user_id)
    ).one_or_none()

    if not user:
        return f"ERROR: Could not find user by id #{user_id}."

    return f"User #{user_id} notes: {user[0].notes}"


def delete_user(user_id: int) -> str:
    user = dbs.execute(db.select(User).where(User.ID == user_id)).one_or_none()
    if not user:
        return f"ERROR: Could not find user by id #{user_id}."

    dbs.delete(user[0])
    dbs.commit()
    return f"User #{user_id} was successfully deleted!"


def post_user() -> str:
    name = flask.request.args.get("name")
    password = flask.request.args.get("password")
    if not (name or password):
        return "Error: No parameters (name and/or password) given."

    user = User(name, password)
    dbs.add(user)
    dbs.commit()

    return f"User posted under the ID #{user.ID}."


"""
==========Notes functions==========
"""


def get_note(note_id: int) -> dict | None:
    note = dbs.execute(
        db.select(Note)
        .where(Note.noteID == note_id)
    ).one_or_none()

    if not note: return

    return dict(
        id=note[0].ID,
        name=note[0].name,
        isLocked=note[0].isLocked,
        parentID=note[0].parentID
    )


def delete_note(note_id: int) -> str:
    if note_functions.delete(note_id):
        return f"Note #{note_id} was successfully deleted!"
    else:
        return f"ERROR: Could not find note by id #{note_id}."


"""
==========Items functions==========
"""


def get_noteitem(item_id: int) -> str:
    if not dbs.execute(db.select(Note).where(Note.ID == item_id)).one_or_none():
        return f"ERROR: Could not find note by id #{item_id}."

    nitems = dbs.execute(
        db.select(NoteItem)
        .where(NoteItem.parentnote == item_id)
    ).all()
    content = [nitem for nitem in nitems]

    content.sort(key=lambda nitem: flask_routes.flaskroutes.index)

    return f"Note #{item_id} contents: {flask.jsonify(content)}"


def post_noteitem(note_id: int):
    note = dbs.execute(
        db.select(Note)
        .where(Note.ID == note_id)
    ).one_or_none()
    if not note:
        return f"ERROR: Could not find nitem by id #{note_id}."

    new_item = note_functions.create_item(noteid=note_id,
                                          itemtype="Text",
                                          content=flask.request.args.get("content"))

    if new_item:    return f"Nitem posted under the ID #{new_item["id"]}"
    else:           return "ERROR: Could not post nitem."


def put_noteitem(item_id: int, content: str) -> str:
    nitem: NoteItem = dbs.execute(
        db.select(NoteItem)
        .where(NoteItem.ID == item_id)
    ).one_or_none()

    if not nitem:
        return f"ERROR: Could not find item by id #{item_id}."

    nitem[0].content = content

    return f"Item #{item_id} updated! Notes file now has the following content: \n\n{nitem[0].content}"
