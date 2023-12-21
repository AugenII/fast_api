from typing import Annotated
from fastapi import Depends, Path, APIRouter, Request, Form
from models import Todos #models.py
from database import SessionLocal #database.py
from sqlalchemy.orm import Session
from starlette import status 
from .auth import get_current_user
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from models import *
from starlette.responses import RedirectResponse

# from main import templates #from main folder

router=APIRouter(
    prefix='/todos',
    tags=['todos'],
    responses={404:{"description":"Not Found"}}
)

templates=Jinja2Templates(directory="templates")

def get_db():
     db=SessionLocal()
     try:
         yield db
     finally:
         db.close()

@router.get("/", response_class=HTMLResponse)
def read_all(request:Request, db:Session=Depends(get_db)): 
    user=get_current_user(request)
    if user is None:
        return RedirectResponse(url='/auth',status_code=status.HTTP_302_FOUND) 
    todos=db.query(Todos).filter(Todos.user_id==user.get('id')).all()
    return templates.TemplateResponse('home.html',{"request":request,"todos":todos,"user":user})

@router.get("/add_todo", response_class=HTMLResponse)
def read_all(request:Request, db:Session=Depends(get_db)):
    user=get_current_user(request)
    if user is None:
        return RedirectResponse(url='/auth',status_code=status.HTTP_302_FOUND) 
    return templates.TemplateResponse('add-todo.html',{"request":request})

@router.post("/add_todo", response_class=HTMLResponse)
def add_todo(request:Request,
             title:str=Form(...),
             description:str=Form(...),
             priority:int=Form(...),
             db:Session=Depends(get_db)):
    user=get_current_user(request)
    if user is None:
        return RedirectResponse(url='/auth',status_code=status.HTTP_302_FOUND) 
    todo_model=Todos()
    todo_model.title=title
    todo_model.description=description
    todo_model.priority=priority
    todo_model.complete=False
    todo_model.user_id=user.get('id') 
    db.add(todo_model)
    db.commit()
    return RedirectResponse(url='/todos',status_code=status.HTTP_302_FOUND)

@router.get("/edit_todo/{id}", response_class=HTMLResponse, name="edit_todo")
def edit_todo(id:int,request:Request,db:Session=Depends(get_db)):
    user=get_current_user(request)
    if user is None:
        return RedirectResponse(url='/auth',status_code=status.HTTP_302_FOUND) 
    todo_model=db.query(Todos).filter(Todos.id==id).first()
    return templates.TemplateResponse('edit-todo.html',{"request":request,"todos":todo_model,"user":user})

@router.post('/edit_todo/{id}', response_class=HTMLResponse)
def edit_todo_commit(id:int,request:Request, db:Session=Depends(get_db),
              title:str=Form(...),
              description:str=Form(...),
              priority:int=Form(...)):
    user=get_current_user(request)
    if user is None:
        return RedirectResponse(url='/auth',status_code=status.HTTP_302_FOUND) 
    todo_model=db.query(Todos).filter(Todos.id==id).first()
    todo_model.title=title
    todo_model.description=description
    todo_model.priority=priority
    db.add(todo_model)
    db.commit()
    print(todo_model)
    return RedirectResponse(url='/todos',status_code=status.HTTP_302_FOUND)

@router.get("/delete_todo/{id}", response_class=HTMLResponse, name="delete_todo")
def delete_todo(id:int,request:Request,db:Session=Depends(get_db)):
    user=get_current_user(request)
    if user is None:
        return RedirectResponse(url='/auth',status_code=status.HTTP_302_FOUND) 
    todo_model=db.query(Todos).filter(Todos.id==id).first()
    if todo_model is None:
        raise HTTPException(status_code='404',detail="Not Found")
    db.delete(todo_model)
    db.commit()
    return RedirectResponse(url='/todos',status_code=status.HTTP_302_FOUND)

@router.get('/complete_todo/{id}', response_class=HTMLResponse, name='complete_todo')
def complete_todo(id:int,
                  request:Request,
                  db:Session=Depends(get_db)):
    user=get_current_user(request)
    if user is None:
        return RedirectResponse(url='/auth',status_code=status.HTTP_302_FOUND) 
    todo_model=db.query(Todos).filter(Todos.id==id).first()
    todo_model.complete=True
    db.add(todo_model)
    db.commit()
    return RedirectResponse(url='/todos', status_code=status.HTTP_302_FOUND)


