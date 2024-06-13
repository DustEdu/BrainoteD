import sqlalchemy as db
from main import dbs
from ormmodels import Note


def create_note(userid: int,
                name: str = "",
                content: str = "") -> dict | None:
    # Creating note
    note = Note(userid, name)
    dbs.add(note)
    dbs.commit()

    # First nitem
    note.create_item(content)
    dbs.commit()

    return dict(id=note.ID)


def get_notes(userid: int) -> list[dict] | None:
    notes = dbs.execute(
        db.select(Note)
        .where(Note.userID == userid)
    ).all()
    if not notes: return

    return [dict(
        id=note[0].ID,
        name=note[0].name
    ) for note in notes]


def get_info() -> dict | None:
    # TODO functionality
    pass


def edit_info() -> dict | None:
    # TODO functionality
    pass
