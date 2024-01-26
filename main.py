from fastapi import FastAPI, Depends, HTTPException, Security, Request
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session

from lib import crud, models, schemas
from lib.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if len(crud.get_all_users(next(get_db()))) == 0:
    print("No users detected, creating first admin user.")
    name = input("Username: ")
    user = crud.create_user(next(get_db()), name)
    user = crud.toggle_admin(next(get_db()), user)
    print(f"api-key: {user.api_key}")

api_key_header = APIKeyHeader(name="X-API-Key")

def authenticate_user(api_key_header: str = Security(api_key_header), db: Session = Depends(get_db)):
    if crud.get_user(db, api_key_header):
        return api_key_header
    raise HTTPException(status_code=401, detail="Unauthorized to access this resource.")
    
def authenticate_admin(api_key_header: str = Security(api_key_header), db: Session = Depends(get_db)):
    db_user = crud.get_user(db, api_key_header)
    if db_user.is_admin:
        return api_key_header
    raise HTTPException(status_code=401, detail="Unauthorized to access this resource.")

def get_user_status(db: Session, user: models.User, status_id: int):
    db_status = crud.get_user_status(db, user.id, status_id)
    if db_status is None:
        raise HTTPException(status_code=404, detail="User status not found.")
    return db_status

def get_user_guest(db: Session, user: models.User, guest_id: int, allow_banned = False):
    if allow_banned:
        db_status = crud.get_user_guest(db, user.id, guest_id)
    else:
        db_status = crud.get_visible_user_guest(db, user.id, guest_id)
    if db_status is None:
        raise HTTPException(status_code=404, detail="User guest not found.")
    return db_status

def get_user_by_name(db: Session, name: str):
    db_user = crud.get_user_by_name(db, name)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found.")
    return db_user

@app.get("/admin/user/", response_model=list[schemas.UserAdmin])
def get_users_admin(db: Session = Depends(get_db), api_key = Depends(authenticate_admin)):
    return crud.get_all_users(db)

@app.post("/admin/user/", response_model=schemas.UserAdmin)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db), api_key = Depends(authenticate_admin)):
    db_user = crud.get_user_by_name(db, user.name)
    if db_user is not None:
        raise HTTPException(status_code=400, detail="Name is already in use.")
    return crud.create_user(db, name=user.name)

@app.delete("/admin/user/{user_name}")
def delete_user_admin(user_name: str, db: Session = Depends(get_db), api_key = Depends(authenticate_admin)):
    db_user = get_user_by_name(db, user_name)
    crud.delete_user(db, db_user.name)
    return db_user

@app.get("/admin/user/{user_name}", response_model=schemas.UserAdmin)
def get_user_admin(user_name: str, db: Session = Depends(get_db), api_key = Depends(authenticate_admin)):
    db_user = get_user_by_name(db, user_name)
    return db_user

@app.get("/user/", response_model=list[schemas.UserPublic])
def get_users_public(db: Session = Depends(get_db)):
    return crud.get_all_users(db)

@app.get("/user/{user_name}/", response_model=schemas.UserPublic)
def get_user(user_name: str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_name(db, user_name)
    return db_user

@app.get("/me", response_model=schemas.UserPrivate)
def get_me(db: Session = Depends(get_db), api_key = Depends(api_key_header)):
    db_user = crud.get_user(db, api_key)
    return db_user

@app.post("/me/status", response_model=schemas.StatusPublic)
def create_status(status: schemas.StatusCreate, db: Session = Depends(get_db), api_key = Depends(authenticate_user)):
    db_user = crud.get_user(db, api_key)
    return crud.create_status(db, status, db_user)

@app.get("/me/status/{status_id}", response_model=schemas.StatusPublic)
def get_status_private(status_id: int, db: Session = Depends(get_db), api_key = Depends(authenticate_user)):
    db_user = crud.get_user(db, api_key)
    return get_user_status(db, db_user, status_id)

@app.get("/me/status", response_model=list[schemas.StatusPublic])
def get_statuses_private(db: Session = Depends(get_db), api_key = Depends(authenticate_user)):
    db_user = crud.get_user(db, api_key)
    return crud.get_user_statuses(db, db_user.id)

@app.delete("/me/status/{status_id}")
def delete_status(status_id: int, db: Session = Depends(get_db), api_key = Depends(authenticate_user)):
    db_user = crud.get_user(db, api_key)
    db_status = get_user_status(db, db_user, status_id)
    crud.delete_status(db, db_status.id)
    return db_status

@app.get("/me/guest/{guest_id}", response_model=schemas.GuestPrivate)
def get_guest_private(guest_id: int, db: Session = Depends(get_db), api_key = Depends(authenticate_user)):
    db_user = crud.get_user(db, api_key)
    return get_user_guest(db, db_user, guest_id, True)

@app.get("/me/guest")
def get_guests_private(db: Session = Depends(get_db), api_key = Depends(authenticate_user)):
    db_user = crud.get_user(db, api_key)
    return crud.get_user_guests(db, db_user.id)

@app.delete("/me/guest/{guest_id}")
def delete_guest(guest_id: int, db: Session = Depends(get_db), api_key = Depends(authenticate_user)):
    db_user = crud.get_user(db, api_key)
    db_guest = get_user_guest(db, db_user, guest_id)
    crud.delete_guest(db, db_guest.id)

@app.post("/me/guest/{guest_id}/ban")
def ban_guest(guest_id: int, db: Session = Depends(get_db), api_key = Depends(authenticate_user)):
    db_user = crud.get_user(db, api_key)
    db_guest = get_user_guest(db, db_user, guest_id, True) # need to see all users to potentially unban
    return crud.toggle_ban_guest(db, db_guest)

@app.get("/user/{user_name}/status/", response_model=list[schemas.StatusPublic])
def get_statuses_public(user_name: str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_name(db, user_name)
    return crud.get_user_statuses(db, db_user.id)

@app.get("/user/{user_name}/status/{status_id}", response_model=schemas.StatusPublic)
def get_status_public(user_name: str, status_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_name(db, user_name)
    return get_user_status(db, db_user, status_id)

@app.post("/user/{user_name}/guest", response_model=schemas.GuestPublic)
def create_guest(user_name: str, guest: schemas.GuestCreate, request: Request, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_name(db, user_name)
    banned_ips = crud.get_banned_ips(db, db_user.id)
    for ip in banned_ips:
        if request.client.host in ip:
            raise HTTPException(status_code=401, detail="Your IP has been banned from this user's guestbook.")
    db_guest = crud.create_guest(db, db_user, guest, request.client.host)
    return db_guest

@app.get("/user/{user_name}/guest", response_model=list[schemas.GuestPublic])
def get_guests_public(user_name: str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_name(db, user_name)
    return crud.get_visible_user_guests(db, db_user.id)

@app.get("/user/{user_name}/guest/{guest_id}", response_model=schemas.GuestPublic)
def get_guest_public(user_name: str, guest_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_name(db, user_name)
    return get_user_guest(db, db_user, guest_id, False)