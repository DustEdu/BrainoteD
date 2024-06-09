import flask
import flask_login
import sqlalchemy as db

from main import dbs, app
from ormmodels import User, Session, Note, NoteItem


def getUser_bySessionkey(sessionkey: str) -> User:
    usersession = dbs.execute(
        db.select(Session)
        .where(Session.key == sessionkey)
    ).one_or_none()

    user = dbs.execute(
        db.select(User)
        .where(User.ID == int(usersession.userID))
    ).one_or_none()
    return user


def isUsernameTaken(name: str) -> bool:
    existing_user = dbs.execute(
        db.select(User)
        .where(User.username == name)
    ).one_or_none()
    if existing_user: return True
    else: return False


def register_admin() -> str:
    username, password = "ADMIN", "ADMIN"

    dbs.add(User(username=username, password=password))
    dbs.commit()

    flask.redirect("login")

    return f"ADMIN account was created."


def register() -> str:
    username, password = flask.request.form["username"], flask.request.form["password"]

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


def login() -> (str, None|str):
    username =  str(flask.request.form["username"])
    password =  str(flask.request.form["password"])
    remember = bool(flask.request.form["remember"])

    user = dbs.execute(
        db.select(User)
        .where(User.username == str(username))
    ).one_or_none()

    if not (user and user.check_password(password)):
        return "Invalid username or password.", None

    flask.session["username"] = user.username
    flask.session["password"] = user.password
    flask.session["remember"] = user.remember

    usersession = Session(user.ID)
    dbs.add(usersession)
    dbs.commit()

    flask_login.login_user(user, remember=remember)
    # flask.redirect(flask.url_for('admin'))
    return f"Login for user {user.username} successful! Sessionkey generated.", usersession.key


def logout(sessionkey: str) -> bool:
    # Flask logout
    flask.logout_user()
    flask.redirect(flask.url_for('login'))

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


def get_users() -> str:
    users = dbs.execute(db.select(User)).all()
    res = ""
    if users:
        for n, i in users, enumerate(users):
            res += f"\nUser #{i}: {n}\n"
    else: res = "No users."
    return res


def get_user(user_id: int) -> str:
    user = dbs.execute(
        db.select(User)
        .where(User.ID == user_id)
    ).one_or_none()

    if not user:
        return f"ERROR: Could not find user by id #{user_id}."

    return f"User #{user_id} notes: {user.notes}"


def delete_user(user_id: int) -> str:
    user = dbs.execute(db.select(User).where(User.ID == user_id)).one_or_none()
    if not user:
        return f"ERROR: Could not find user by id #{user_id}."

    dbs.delete(user[0])
    # for i in item[0].getItems():
    #     session.delete(i[0])
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


def get_notes() -> str:
    notes = dbs.execute(
        db.select(Note)
    ).all()

    if not notes:  return "No notes."

    res = ""
    for n, i in notes, enumerate(notes):
        res += f"\nNote #{i}: {n}\n"

    return res


def get_note(note_id: int) -> str:
    # Find note by id and update its value
    item = dbs.execute(
        db.select(NoteItem).where(NoteItem.parentnote == note_id)
    ).one_or_none()

    if not item:
        return f"ERROR: Could not find item by id #{note_id}."

    return f"Note #{note_id} content: {item[0].content}"


def delete_note(note_id: int) -> str:
    item = dbs.execute(
        db.select(Note).where(Note.ID == note_id)
    ).one_or_none()
    if not item:
        return f"ERROR: Could not find note by id #{note_id}."

    dbs.delete(item[0])
    dbs.commit()

    return f"Note #{note_id} was successfully deleted!"


def post_note() -> str:
    content = flask.request.args.get("content")
    name = flask.request.args.get("name")
    if not content: content = ""
    if not name: name = ""

    # Creating note
    note = Note(name)
    dbs.add(note)
    dbs.commit()

    # First nitem
    note.create_item(content)
    dbs.commit()

    return f"Note posted under the ID #{note.ID}."


"""
==========Items functions==========
"""


def get_noteitem(item_id: int) -> str:
    if not dbs.execute(db.db.select(Note).where(Note.ID == item_id)).one_or_none():
        return f"ERROR: Could not find note by id #{item_id}."

    nitems = dbs.execute(db.select(NoteItem).where(NoteItem.parentnote == item_id)).all()
    content = [nitem for nitem in nitems]

    content.sort(key=lambda nitem: nitem.index)

    return f"Note #{item_id} contents: {flask.jsonify(content)}"


def post_noteitem(note_id: int) -> str:
    content = flask.request.args.get("content")

    nitem = dbs.execute(db.select(Note).where(Note.ID == note_id)).one_or_none()
    if not nitem:
        return f"ERROR: Could not find noteitem by id #{note_id}."
    else: nitem = nitem[0]
    dbs.add(NoteItem(content))
    dbs.commit()

    return f"Item posted under the ID #{nitem.ID}"


def delete_noteitem(item_id: int) -> str:
    nitem = dbs.execute(db.select(NoteItem).where(NoteItem.ID == item_id)).one_or_none()
    if not nitem:
        return f"ERROR: Could not find item by id #{item_id}."
    dbs.delete(nitem[0])
    return f"Item #{item_id} was successfully deleted!"


def put_noteitem(item_id: int, content: str) -> str:
    nitem: NoteItem = dbs.execute(db.select(NoteItem).where(NoteItem.ID == item_id)).one_or_none()

    if not nitem:
        return f"ERROR: Could not find item by id #{item_id}."

    nitem[0].content = content

    return f"Item #{item_id} updated! Notes file now has the following content: \n\n{nitem[0].content}"
