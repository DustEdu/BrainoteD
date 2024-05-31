import flask
import flask_login
import sqlalchemy as db

from main import session, app
from ormmodels import User, Session, Note, NoteItem


def validate_username(name: str) -> True:
    existing_user = session.execute(db.select(User).where(User.username == name)).one_or_none()
    if not existing_user: return True
    else: return False


def register() -> str:
    username = flask.request.form["username"]
    password = flask.request.form["password"]

    msg: str

    if validate_username(username):
        msg = "Such user already exists. Please choose another username or login instead."
    if len(password) < 5:
        msg = "The password is too short: Password needs to be longer than 4 characters (like I really care lol bro)"
    else:
        session.add(User(username=username, password=password))
        session.commit()
        msg = (f"User \"{username}\" registered successfully! "
               f"(bro what a dumb nickname u couldn't come up with anything better like seriously? "
               f"You should be ashamed.)")
        flask.redirect("login")

    flask.flash(msg)
    return msg


def login() -> str:
    # form = LoginForm()

    # username: str =  form.username.data
    # password: str =  form.password.data
    # remember: bool = form.remember.data

    # if form.validate_on_submit():

    username: str = flask.request.form["username"]
    password: str = flask.request.form["password"]
    remember: bool = bool(flask.request.form["remember"])

    user = session.execute(db.select(User).where(User.username == str(username))).one_or_none()

    if not (user and user.check_password(password)):
        return flask.flash("Invalid username or password.")
    else:
        flask.session["username"] = user.username
        flask.session["password"] = user.password
        flask.session["remember"] = user.remember

        usersession = Session(user.ID)
        session.add(usersession)
        session.commit()
        flask_login.login_user(user, remember=remember)
        flask.redirect(flask.url_for('admin'))
        return usersession.key


def logout() -> str:
    flask.session.pop("name", None)
    flask.logout_user()
    msg = "You have been logged out."
    flask.flash(msg)
    flask.redirect(flask.url_for('login'))
    return msg


"""
==========Users functions==========
"""


def get_users() -> str:
    users = session.execute(db.select(User)).all()
    res = ""
    if users:
        for n, i in users, enumerate(users):
            res += f"\nUser #{i}: {n}\n"
    else: res = "No users."
    return res


def get_user(user_id: int) -> str:
    # Find note by id and update its value
    user = session.execute(db.select(User).where(User.ID == user_id)).one_or_none()

    if not user:
        return f"ERROR: Could not find user by id #{user_id}."

    return f"User #{user_id} notes: {user[0].notes}"


def delete_user(user_id: int) -> str:
    user = session.execute(db.select(User).where(User.ID == user_id)).one_or_none()
    if not user:
        return f"ERROR: Could not find user by id #{user_id}."

    session.delete(user[0])
    # for i in item[0].getItems():
    #     session.delete(i[0])
    session.commit()
    return f"User #{user_id} was successfully deleted!"


def post_user() -> str:
    name = flask.request.args.get("name")
    password = flask.request.args.get("password")
    if not (name or password):
        return "Error: No parameters (name and/or password) given."

    user = User(name, password)
    session.add(user)
    session.commit()

    return f"User posted under the ID #{user.ID}."


"""
==========Notes functions==========
"""


def get_notes() -> str:
    notes = session.execute(db.select(Note)).all()
    res = ""
    if notes:
        for n, i in notes, enumerate(notes):
            res += f"\nNote #{i}: {n}\n"
    else: res = "No notes."
    return res


def get_note(note_id: int) -> str:
    # Find note by id and update its value
    item = session.execute(
        db.select(NoteItem).where(NoteItem.parentnote == note_id)
    ).one_or_none()

    if not item:
        return f"ERROR: Could not find item by id #{note_id}."

    return f"Note #{note_id} content: {item[0].content}"


def delete_note(note_id: int) -> str:
    item = session.execute(
        db.select(Note).where(Note.ID == note_id)
    ).one_or_none()
    if not item:
        return f"ERROR: Could not find note by id #{note_id}."

    session.delete(item[0])
    # for i in item[0].getItems():
    #     session.delete(i[0])
    session.commit()
    return f"Note #{note_id} was successfully deleted!"


def post_note() -> str:
    content = flask.request.args.get("content")
    name = flask.request.args.get("name")
    if not content: content = ""
    if not name: name = ""

    note = Note(name)
    session.add(note)
    session.commit()
    note.create_item(content)
    session.commit()

    return f"Note posted under the ID #{note.ID}."


"""
==========Items functions==========
"""


def get_item(item_id: int) -> str:
    if not session.execute(db.db.select(Note).where(Note.ID == item_id)).one_or_none():
        return f"ERROR: Could not find note by id #{item_id}."

    items = session.execute(db.select(NoteItem).where(NoteItem.parentnote == item_id)).all()
    content = [i for i in items]

    content.sort(key=lambda i: i.index)

    return f"Note #{item_id} contents: {flask.jsonify(content)}"


def post_item(note_id: int) -> str:
    content = flask.request.args.get("content")

    noteitem = session.execute(db.select(Note).where(Note.ID == note_id)).one_or_none()
    if not noteitem:
        return f"ERROR: Could not find noteitem by id #{note_id}."
    else: noteitem = noteitem[0]
    session.add(NoteItem(content))
    session.commit()

    return f"Item posted under the ID #{noteitem.ID}"


def delete_item(item_id: int) -> str:
    item = session.execute(db.select(NoteItem).where(NoteItem.ID == item_id)).one_or_none()
    if not item:
        return f"ERROR: Could not find item by id #{item_id}."
    session.delete(item[0])
    return f"Item #{item_id} was successfully deleted!"


def put_item(item_id: int, content: str) -> str:
    nitem: NoteItem = session.execute(db.select(NoteItem).where(NoteItem.ID == item_id)).one_or_none()

    if not nitem:
        return f"ERROR: Could not find item by id #{item_id}."

    nitem[0].content = content

    return f"Item #{item_id} updated! Notes file now has the following content: \n\n{nitem[0].content}"
