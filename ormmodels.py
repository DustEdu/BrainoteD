# from sqlalchemy import Column, Integer, String, ForeignKey, select, Boolean
import secrets

import sqlalchemy as db

from werkzeug.security import generate_password_hash as hashed_password, check_password_hash
from flask_login import UserMixin

from authorize import login_manager
from main import dbs, DeclarativeBase


@login_manager.user_loader
def load_user(user_id):
    return db.session.execute(db.select(User).where(User.ID == user_id)).one_or_none()


class Session(DeclarativeBase):
    __tablename__ = "sessions"

    # Columns
    ID      = db.Column("id", db.Integer, primary_key=True)
    key     = db.Column("key", db.String, unique=True, nullable=False)
    userID  = db.Column("user_id", db.Integer,
                        db.ForeignKey("users.id", ondelete="CASCADE"),
                        nullable=False)

    # Relationships
    user = db.orm.Relationship("User", back_populates="sessions")

    def __init__(self, userID: str, key: str = None):
        if not key: key = secrets.token_urlsafe(16)
        self.key    = key
        self.userID = userID


class User(DeclarativeBase, UserMixin):
    __tablename__ = "users"

    # Columns
    ID       = db.Column("id", db.Integer, primary_key=True)
    username = db.Column("nickname", db.String(16), unique=True)
    password = db.Column("password", db.String(16))
    language = db.Column("language", db.String(8))
    # notesID  = Column("notes_id",
    #                   Integer, ForeignKey("notes.id"))

    # Relationships
    notes    = db.orm.Relationship("Note", back_populates="user",
                                   passive_deletes=True,
                                   cascade="save-update, merge, delete, delete-orphan")
    sessions = db.orm.Relationship("Session", back_populates="user",
                                   passive_deletes=True,
                                   cascade="save-update, merge, delete, delete-orphan")

    def __init__(self, username: str | None, password: str | None):
        self.username = username
        self.password = password

    def set_password(self, password) -> None:
        self.password = hashed_password(password)

    def check_password(self, password) -> bool:
        return check_password_hash(self.password, password)


class Note(DeclarativeBase):
    __tablename__ = "notes"

    # Columns
    ID       = db.Column("id", db.Integer, primary_key=True)
    name     = db.Column("name", db.String(32))
    isLocked = db.Column("is_locked", db.Boolean)
    userID   = db.Column("user_id", db.Integer,
                      db.ForeignKey("users.id", ondelete="CASCADE"))
    parentID = db.Column("parent_id", db.Integer,
                      db.ForeignKey("notes.id", ondelete="CASCADE"))

    # Relationships
    items = db.orm.Relationship("NoteItem", back_populates="note",
                                passive_deletes=True,
                                cascade="save-update, merge, delete, delete-orphan")
    user  = db.orm.Relationship("User", back_populates="notes")
    notes = db.orm.Relationship("Note", remote_side=ID, passive_deletes=True)

    def __init__(self, name: None|str = None, parent_id: None|int = None):
        self.name = name
        self.parent_id = parent_id
        self.isLocked = False

    def getItems(self):
        return dbs.execute(db.select(NoteItem).where(
            NoteItem.noteID == self.ID)).all()

    def create_item(self, *args):
        print(f"\n\n\n\t\tID: {int(self.ID)}\n\n\n")
        noteitem = NoteItem(*args, noteID=int(self.ID))
        print(f"\n\n\n\t\tNoteItem: {noteitem}; noteID: {noteitem.noteID}\n\n\n")
        dbs.add(noteitem)

    def create_subnote(self, *args):
        subnote = Note(*args, parent_id=int(self.ID))
        dbs.add(subnote)

        print(f"\n\n\n\t\t"
              f"self.ID: {int(self.ID)}"
              f"\n\n\n")
        print(f"\n\n\n\t\t"
              f"Subnote: {subnote}; SubnoteID: {subnote.ID}"
              f"\n\n\n")

    def rearrange(self, i, j):
        item1 = dbs.execute(db.select(NoteItem).where(
            NoteItem.noteID == self.ID, NoteItem.index == i)).one_or_none()
        items = dbs.execute(db.select(NoteItem).where(
            NoteItem.noteID == self.ID, NoteItem.index > i)).all()

        for i in items:
            i.index += 1
        item1.index = j

        print(f"items of note #{self.ID} were rearranged.")


class NoteItem(DeclarativeBase):
    __tablename__ = "noteitems"

    # Columns
    ID       = db.Column("id", db.Integer, primary_key=True)
    content  = db.Column("content", db.String)
    itemtype = db.Column("itemtype", db.String(16))
    noteID   = db.Column("note_id", db.Integer,
                      db.ForeignKey("notes.id", ondelete="CASCADE"))
    index    = db.Column("index", db.Integer, unique=True)

    # Relationships
    note = db.orm.Relationship("Note", back_populates="items",
                        # foreign_keys=noteID
                        )

    def __init__(self,
                 content:   str,
                 itemtype:  str = "Text",
                 noteID:    int | None = None,
                 index:     int | None = None):
        self.content    = content
        self.itemtype   = itemtype
        self.noteID     = noteID
        self.index      = index

    def updateItems(self,
                    content:  str | None = None,
                    itemtype: str | None = None,
                    noteID:   int | None = None,
                    index:    int | None = None
                    ):
        self.content    = content   if content  is not None else self.content
        self.itemtype   = itemtype  if itemtype is not None else self.itemtype
        self.noteID     = noteID    if noteID   is not None else self.noteID
        self.index      = index     if index    is not None else self.index

    def __repr__(self):
        return str(dict(
            itemID=self.ID,
            content=self.content,
            itemtype=self.itemtype,
            noteID=self.noteID
        ))
