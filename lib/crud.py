from uuid import uuid4
import pytz
from datetime import datetime
from sqlalchemy.orm import Session

from . import models, schemas

def get_user(db: Session, api_key: str):
    return db.query(models.User).filter(models.User.api_key == api_key).first()

def delete_user(db: Session, name: str):
    db_user = get_user_by_name(db, name)
    db.delete(db_user)
    db.commit()
    return

def get_banned_ips(db: Session, user_id: int):
    return db.query(models.Guest.ip).where(models.Guest.is_banned).where(models.Guest.user_id == user_id).all()

def get_user_by_url(db: Session, user_url: str):
    return db.query(models.User).where(models.User.url == user_url).first()

def get_user_status(db: Session, user_id: int, status_id: int):
    return db.query(models.Status).where(models.Status.user_id == user_id).where(models.Status.id == status_id).first()

def get_user_statuses(db: Session, user_id: int):
    return db.query(models.Status).where(models.Status.user_id == user_id).all()

def get_visible_user_guest(db: Session, user_id: int, guest_id: int):
    return db.query(models.Guest).where(models.Guest.user_id == user_id).where(models.Guest.id == guest_id).where(models.Guest.is_banned == False).first()

def get_user_guest(db: Session, user_id: int, guest_id: int):
    return db.query(models.Guest).where(models.Guest.user_id == user_id).where(models.Guest.id == guest_id).first()

def get_user_guests(db: Session, user_id: int):
    return db.query(models.Guest).where(models.Guest.user_id == user_id).all()

def get_visible_user_guests(db: Session, user_id: int):
    return db.query(models.Guest).where(models.Guest.user_id == user_id).where(models.Guest.is_banned == False).all()

def get_user_by_name(db: Session, name: str):
    return db.query(models.User).filter(models.User.name == name).first()

def get_all_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def get_guest(db: Session, id: int):
    return db.query(models.Guest).filter(models.Guest.id == id).first()

def get_all_guests(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Guest).offset(skip).limit(limit).all()

def get_status(db: Session, id: int):
    return db.query(models.Status).filter(models.Status.id == id).first()

def get_all_statuses(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Status).order_by(models.Status.dt).offset(skip).limit(limit).all()

def create_user(db: Session, name: str, url: str):
    api_key = str(uuid4())
    db_user = models.User(name=name, api_key=api_key, url=url)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def toggle_admin(db: Session, user: schemas.UserPublic):
    db_user = get_user(db, user.api_key)
    db_user.is_admin = not db_user.is_admin
    db.commit()
    db.refresh(db_user)
    return db_user

def toggle_ban_guest(db: Session, guest: schemas.GuestPrivate):
    db_guest = get_guest(db, guest.id)
    db_guest.is_banned = not db_guest.is_banned
    db.commit()
    db.refresh(db_guest)
    return db_guest

def create_guest(db: Session, user: schemas.UserPublic, guest: schemas.GuestCreate, ip: str):
    db_guest = models.Guest(name=guest.name, message=guest.message, dt=datetime.now(pytz.timezone("UTC")), ip=ip, user=user)
    db.add(db_guest)
    db.commit()
    db.refresh(db_guest)
    return db_guest

def delete_guest(db: Session, id: int):
    db_guest = get_guest(db, id)
    db.delete(db_guest)
    db.commit()
    return

def create_status(db: Session, status: schemas.StatusCreate, user: schemas.UserPublic):
    db_status = models.Status(status=status.status, dt=datetime.now(pytz.timezone("UTC")), user=user)
    db.add(db_status)
    db.commit()
    db.refresh(db_status)
    return db_status

def get_client_session(db: Session, ip: str):
    db_session = db.query(models.ClientSession).where(models.ClientSession.ip == ip).first()
    if db_session == None:
        state = str(uuid4())
        cookie = str(uuid4())
        db_session = models.ClientSession(ip=ip, state=state, cookie=cookie)
        db.add(db_session)
    db_session.state = str(uuid4())  # regenerate the state each time the session is grabbed.
    db.commit()
    db.refresh(db_session)
    return db_session

def get_session_by_state(db: Session, state: str):
    return db.query(models.ClientSession).where(models.ClientSession.state == state).first()

def save_user_session(db: Session, ip: str, url: str):
    db_session = get_client_session(db, ip)
    db_session.user = get_user_by_url(db, url)
    db.commit()
    db.refresh(db_session)
    return db_session

def delete_status(db: Session, id: int):
    db_status = get_status(db, id)
    db.delete(db_status)
    db.commit()
    return

def update_URL(db: Session, user_private: schemas.UserPrivate, url: str):
    db_user = get_user(db, user_private.api_key)
    db_user.url = url
    db.commit()
    return

def store_user_session(db: Session, url: str):
    db_user = get_user_by_url(db, url)
    db_user_session = models.UserSession(id=str(uuid4()), user_id=db_user.id)
    db.add(db_user_session)
    db.commit()
    db.refresh(db_user_session)
    return db_user_session