# Owner: Helen Mezgebe
# Feature: User Registration and Secure Access

from uuid import UUID

from sqlalchemy.orm import Session

from models.users import User


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email.lower()).first()


def get_user_by_id(db: Session, user_id: UUID):
    return db.query(User).filter(User.user_id == user_id).first()


def create_user(db: Session, **values):
    user = User(**values)
    db.add(user)
    db.flush()
    return user
