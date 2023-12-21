from fastapi import FastAPI
import models
import database
from database import engine
from routers import auth, todo,admin,user #todo has the functions
from starlette.staticfiles import StaticFiles
from starlette.responses import RedirectResponse
from starlette import status


app= FastAPI()

@app.get('/')
def root():
    return RedirectResponse("/todos", status_code=status.HTTP_302_FOUND)

models.Base.metadata.create_all(bind=engine) #after running uvicorn main:app this lines will create a database file in the directory

app.mount("/static",StaticFiles(directory="static"), name="static")

#the auth file is inside the routers folder. This is done to acccess the contents of auth.py file without calling FastAPI().add()
#calling via FastAPI() method limits its scope only to the file which declared
#implimenting calling by router will remove this issue
app.include_router(auth.router)
app.include_router(todo.router)
app.include_router(admin.router)
app.include_router(user.router)