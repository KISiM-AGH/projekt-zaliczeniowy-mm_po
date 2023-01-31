from sqlalchemy.orm import Session

import models, schemas


def get_user(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def save_user(email: str, hashed_password: str, db: Session):
    item = models.User(
        email=email,
        hashed_password=hashed_password,
        is_active=True
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return
