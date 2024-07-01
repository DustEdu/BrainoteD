import sqlalchemy as db

import routes_module.routes
from main import dbs
from ormmodels import NoteItem


def delete(nitemid: int) -> bool:
    nitem = dbs.execute(
        db.select(NoteItem)
        .where(NoteItem.ID == nitemid)
    ).one_or_none()
    if not nitem: return False
    else: nitem, = nitem

    dbs.delete(nitem)
    dbs.commit()
    return True


def get(nitemid: int) -> dict | None:
    nitem = dbs.execute(
        db.select(NoteItem)
        .where(NoteItem.ID == nitemid)
    ).one_or_none()
    if not nitem: return
    else: nitem, = nitem

    return dict(
        index=nitem.index,
        content=nitem.content,
        type=nitem.itemtype,
    )


def edit(nitemid: int, content: str|None = None, itemtype: str|None = None) -> dict | None:
    nitem: NoteItem = dbs.execute(
        db.select(NoteItem)
        .where(NoteItem.ID == nitemid)
    ).one_or_none()
    if not nitem: return
    else: nitem, = nitem

    nitem.update_item(content=content, itemtype=itemtype)

    return dict(
        index=nitem.index,
        content=nitem.content,
        type=nitem.itemtype,
    )
