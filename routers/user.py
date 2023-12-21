from typing import Annotated
from fastapi import Depends, HTTPException, Path, APIRouter
from models import Todos,Users #models.py
from database import SessionLocal #database.py
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from starlette import status
from .auth import get_current_user
from passlib.hash import pbkdf2_sha256 as sha256

router=APIRouter(
    prefix='/uesrs',   #the preific and tags are used to bring all endpoints in auth.py under /auth mentioned in the preifx
    tags=['user']
)


def get_db():
     db=SessionLocal()
     try:
         yield db
     finally:
         db.close()

class ChangePassword(BaseModel):
    password:str
    
class UpdatePhoneNumber(BaseModel):
    phone_number:str

db_dependency=Annotated[Session,Depends(get_db)]
user_dependency=Annotated[dict,Depends(get_current_user)] #function called form auth/auth.py get_current_user

@router.get('/user_info',status_code=status.HTTP_200_OK)
def get_user_info(user:user_dependency,
                  db:db_dependency):
    if user is None or user.get('user_role')!='user':
        raise HTTPException(status_code=404, detail="Not User Found")
    user_info=db.query(Users).filter(Users.id==user.get('id')).first()
    if user_info is None:
        raise HTTPException(status_code=404,detail="user is not found")
    print(sha256)
    return user_info

@router.put('/change_password',status_code=status.HTTP_204_NO_CONTENT)
def user_change_password(user:user_dependency,
                         db:db_dependency,change_password:ChangePassword):
    user_model=db.query(Users).filter(Users.id==user.get('id')).first()
    if user_model is None or user.get('user_role')!='user':
        raise HTTPException(status_code=404,detail="No User Found or Invaid User")
    print(user_model.first_name)
    new_password=sha256.hash(change_password.password)
    user_model.hashed_password=new_password
    db.add(user_model)
    db.commit()
    return {"password updated successfully"}

@router.put('/update_phonenumber',status_code=status.HTTP_204_NO_CONTENT)
def update_phone(user:user_dependency,
                 db:db_dependency,
                 update_phone:UpdatePhoneNumber):
    user_model=db.query(Users).filter(Users.id==user.get('id')).first()
    if user_model is None:
        raise HTTPException(status_code=404, detail="no user found")
    new_phone_number=update_phone.phone_number
    print(new_phone_number)
    user_model.phone_number=new_phone_number
    db.add(user_model)
    db.commit()
    return "updated successfully"