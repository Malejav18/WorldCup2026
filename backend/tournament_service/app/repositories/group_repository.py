from typing import Optional

from sqlalchemy.orm import Session

from tournament_service.app.entities.group import Group


class GroupRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_all(self) -> list[Group]:
        return self.db.query(Group).order_by(Group.letter).all()

    def get(self, group_id: str) -> Optional[Group]:
        return self.db.query(Group).filter(Group.id == group_id).first()

    def get_by_letter(self, letter: str) -> Optional[Group]:
        return self.db.query(Group).filter(Group.letter == letter).first()
