from typing import Optional

from sqlalchemy.orm import Session

from user_service.app.entities.user_profile import UserProfile


class UserProfileRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, user_id: str) -> Optional[UserProfile]:
        return self.db.query(UserProfile).filter(UserProfile.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[UserProfile]:
        return self.db.query(UserProfile).filter(UserProfile.email == email).first()

    def create(self, profile: UserProfile) -> UserProfile:
        self.db.add(profile)
        self.db.flush()
        return profile

    def update_total_points(self, user_id: str, new_total: int) -> Optional[UserProfile]:
        profile = self.get(user_id)
        if profile is None:
            return None
        profile.total_points = new_total
        return profile
