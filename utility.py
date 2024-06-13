import flask
import sqlalchemy as db

import flask_routes.flaskroutes
from main import dbs
from ormmodels import User, Note, NoteItem, Session


def isAdmin(user: User) -> bool:
    if user.username == "ADMIN":
        return True
    else:
        return False


def get_provided_user(user: User) -> User | str:
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

    if not note:
        return False

    if note[0].user == user:
        return True

    return False


def isNitemOfUser(nitem_id: int, user: User) -> bool:
    if user.username == "ADMIN":
        return True

    nitem = dbs.execute(
        db.select(NoteItem)
        .where(NoteItem.ID == nitem_id)
    ).one_or_none()

    if nitem and nitem[0].note.user == user:
        return True

    return False


def getSessionUser(sessionkey: str = None) -> User | None:
    if not sessionkey: return

    usersession = dbs.execute(
        db.select(Session)
        .where(Session.key == sessionkey)
    ).one_or_none()
    if not usersession: return

    user = dbs.execute(
        db.select(User)
        .where(User.ID == int(usersession[0].userID))
    ).one_or_none()
    if not user: return

    return user[0]


def isUsernameTaken(name: str) -> bool:
    existing_user = dbs.execute(
        db.select(User)
        .where(User.username == name)
    ).one_or_none()
    if existing_user: return True
    else: return False
