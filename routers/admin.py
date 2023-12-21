from typing import Annotated

from fastapi import Depends, HTTPException, Path, APIRouter
from models import Todos #models.py
from database import SessionLocal #database.py
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from starlette import status
from .auth import get_current_user

router=APIRouter(
    prefix='/admin',   #the preific and tags are used to bring all endpoints in auth.py under /auth mentioned in the preifx
    tags=['admin']
)


def get_db():
     db=SessionLocal()
     try:
         yield db
     finally:
         db.close()

db_dependency=Annotated[Session,Depends(get_db)]
user_dependency=Annotated[dict,Depends(get_current_user)] #function called form auth/auth.py get_current_user

@router.get("/todo",status_code=status.HTTP_200_OK)
def read_all(user:user_dependency,db:db_dependency):
    if user is None or user.get('user_role')!='admin':
        raise HTTPException(status_code=401, detail='authentication failed')
    return db.query(Todos).all()

@router.delete("todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_todo(user:user_dependency,
                db:db_dependency,
                todo_id:int=Path(gt=0)):
    if user is None or user.get('user_role')!='admin':
        raise HTTPException(status_code=404,detail='User Not Found')
    todo_model=db.query(Todos).filter(Todos.id==todo_id)
    if todo_model is not None:
        todo_model.delete()
        db.commit()
        print('model removed succesfully')
    raise HTTPException(status_code=404, detail="Model not Found")