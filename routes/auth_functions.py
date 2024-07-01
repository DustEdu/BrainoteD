import sqlalchemy

from main import dbs
from ormmodels import User, Session
from utility import isUsernameTaken


def register_admin() -> str:
    username, password = "ADMIN", "ADMIN"

    dbs.add(User(username=username, password=password))
    dbs.commit()

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

    return (f"User \"{username}\" registered successfully! "
            f"(bro what a dumb nickname u couldn't come up with anything better like seriously? "
            f"You should be ashamed.)")


def login(username: str, password: str, remember: bool) -> (str, str):
    user: User = dbs.execute(
        db.select(User)
        .where(User.username == str(username))
    ).one_or_none()

    if not user or not user[0].check_password(password):
        return None, "Invalid username or password."
    else:
        user = user[0]

    # flask.session["username"] = user.username

    usersession = Session(user.ID)
    dbs.add(usersession)
    dbs.commit()

    return usersession.key, "Success"


def delete_session_by_key(sessionkey: str) -> bool:
    dbs.execute(
        db.delete(Session)
        .where(Session.key == sessionkey)
    )
    dbs.commit()
    return True
