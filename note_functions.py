import sqlalchemy as db

import flask_routes.flaskroutes
from main import dbs
from ormmodels import Note, NoteItem


def delete(noteid: int) -> bool:
    note = dbs.execute(
        db.select(Note)
        .where(Note.ID == noteid)
    ).one_or_none()
    if not note: return False

    dbs.delete(note)
    dbs.commit()
    return True


def get_items(noteid: int) -> list[dict] | None:
    nitems = dbs.execute(
        db.select(NoteItem)
        .where(NoteItem.noteID == noteid)
    ).all()
    if not nitems: return
    # else: nitems, = nitems

    return [dict(
        id=nitem[0].ID,
        index=nitem[0].index,
        content=nitem[0].content,
        type=nitem[0].itemtype,
    ) for nitem in nitems]


def create_item(noteid: int,
                content: str = "",
                itemtype: str = "Text") -> dict | None:
    nitem = NoteItem(noteid, content, itemtype)
    if not nitem: return

    dbs.add(nitem)
    dbs.commit()

    return dict(
        id=nitem.ID,
        index=nitem.index,
    )
