import sqlalchemy as db

from main import dbs
from ormmodels import Note, NoteItem


def delete(noteid: int) -> bool:
    note = dbs.execute(
        db.select(Note)
        .where(Note.ID == noteid)
    ).one_or_none()
    if not note: return False

    dbs.delete(note[0])
    dbs.commit()
    return True


def get_items(noteid: int) -> list[NoteItem] | None:
    nitems = dbs.execute(
        db.select(NoteItem)
        .where(NoteItem.noteID == noteid)
    ).all()
    if not nitems:  return
    return [nitem[0] for nitem in nitems]


def create_item(noteid: int,
                content: str = " ",
                itemtype: str = "Text") -> NoteItem | None:
    nitem = NoteItem(noteid, content, itemtype)
    if not nitem: return

    dbs.add(nitem)
    dbs.commit()
    return nitem
