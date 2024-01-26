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

def get_user_status(db: Session, user_id: int, status_id: int):
    return db.query(models.Status).where(models.Status.user_id == user_id).where(models.Status.id == status_id).first()

def get_user_statuses(db: Session, user_id: int):
    return db.query(models.Status).where(models.Status.user_id == user_id).all()

def get_visible_user_guest(db: Session, user_id: int, guest_id: int):
    return db.query(models.Guest).where(models.Guest.user_id == user_id).where(models.Guest.id == guest_id).where(not models.Guest.is_banned).first()

def get_user_guest(db: Session, user_id: int, guest_id: int):
    return db.query(models.Guest).where(models.Guest.user_id == user_id).where(models.Guest.id == guest_id).first()

def get_user_guests(db: Session, user_id: int):
    return db.query(models.Guest).where(models.Guest.user_id == user_id).all()

def get_visible_user_guests(db: Session, user_id: int):
    return db.query(models.Guest).where(not models.Guest.is_banned).all()

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

def create_user(db: Session, name: str):
    api_key = str(uuid4())
    db_user = models.User(name=name, api_key=api_key)
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

def delete_status(db: Session, id: int):
    db_status = get_status(db, id)
    db.delete(db_status)
    db.commit()
    return
