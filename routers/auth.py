from typing import Annotated
from datetime import timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException, Request, Response, Form
from sqlalchemy.orm import Session
from models import Users
from database import SessionLocal
from pydantic import BaseModel, Field
from passlib.context import CryptContext #for hashing password : pip install passlib[bcrypt]
from passlib.hash import pbkdf2_sha256 as sha256
from starlette import status
from starlette.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer  #for user with swagger api
from jose import jwt, JWTError      #for importing jwt
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router=APIRouter(
    prefix='/auth',   #the preific and tags are used to bring all endpoints in auth.py under /auth mentioned in the preifx
    tags=['auth']
)


class LoginForm:
    def __init__(self,request:Request):
        self.request:Request=request
        self.username:Optional[str]=None
        self.password:Optional[str]=None
    async def create_oauth_form(self):
        form=await self.request.form()
        self.username=form.get("email")
        self.password=form.get("password") 
        
        
SECRET_KEY='29573e3de797179245c1b9938da868b4' #generated using openssl rand hex32 online
ALGORITHM='HS256'

# bcrypt_context=CryptContext(schemes=['bcrypt'], deprecated='auto')
#not used above method since im using sha256

oauth2_bearer=OAuth2PasswordBearer(tokenUrl='auth/user_verification')
templates=Jinja2Templates(directory="templates")


def get_db():
     db=SessionLocal()
     try:
         yield db
     finally:
         db.close()
         
db_dependency=Annotated[Session,Depends(get_db)]

    
class Token(BaseModel):
    access_token:str
    token_type:str

def authenticate_user(username:str,password:str,db):
    user=db.query(Users).filter(Users.username==username).first()
    try:
        hashed=str(user.hashed_password)
    except:
        pass
    if not user:
        print("no user found")
        return False
    if not sha256.verify(password,hashed):
        print("password failed")
        return False
        pass
    return user

#generates jwt access tokrn for user authentication
def create_access_token(username:str,user_id:int,role:str, expires_delta:timedelta):
    print(role)
    encode={'sub':username,'id':user_id,'role':role}
    expires=datetime.utcnow()+expires_delta
    encode.update({'exp':expires})
    return jwt.encode(encode, SECRET_KEY,algorithm=ALGORITHM)

#ensuring the jwt token is secure
def get_current_user(request:Request):
    try:
        token=request.cookies.get("access_token")
        if token is None:
            return None
        payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        username:str=payload.get('sub')
        user_id:int=payload.get('id')
        user_role:str=payload.get('role')
        print(user_role)
        if username is None or user_id is None:
            # return None using this will just passing the boolean value, does nothing with the token #
            logout(request) # this will delete the token request if there are no valid user found
        return {'username':username,'id':user_id,'user_role':user_role}
    except JWTError:
        return templates.TemplateResponse('login.html',{"request":request})

@router.get('/register',response_class=HTMLResponse)
def register(request:Request):
    return templates.TemplateResponse('register.html',{"request":request})  

@router.post('/register')
def add_user(request:Request,
             first_name:str=Form(...),
             last_name:str=Form(...),
             username:str=Form(...),
             email:str=Form(...),
             phone_number:int=Form(...),
             password1:str=Form(...),
             password2:str=Form(...),
             db:Session = Depends(get_db)):
    
    validation1=db.query(Users).filter(Users.username == username).first()
    validation2=db.query(Users).filter(Users.email == email).first()
    
    if password1 != password2 or validation1 is not None or validation2 is not None:
        msg="Invalid Registartion Details. Recheck Email, Username and Password"
        return templates.TemplateResponse('register.html',{"request":request,"msg":msg})
    
    user_model=Users()
    user_model.first_name=first_name
    user_model.last_name=last_name
    user_model.username=username
    user_model.email=email
    user_model.hashed_password=sha256.hash(password1)
    user_model.phone_number=phone_number
    user_model.role='user'
    db.add(user_model)
    db.commit()
    msg="User Successfully Created"
    return templates.TemplateResponse('login.html',{"request":request,"msg":msg})

@router.get('/',response_class=HTMLResponse)
def authentication_page(request:Request):
    return templates.TemplateResponse('login.html',{"request":request})


@router.post('/',response_class=HTMLResponse)
async def login(request:Request,db:Session=Depends(get_db)):
    try:
        form=LoginForm(request)
        await form.create_oauth_form()
        response=RedirectResponse(url='/todos',status_code=status.HTTP_302_FOUND)
        validate_user_cookie=await login_verification(response=response,form_data=form,db=db)
        if not validate_user_cookie:
            msg="Incorrect Login Credentials"
            return templates.TemplateResponse('login.html',{'request':request,'msg':msg})
        return response
    except HTTPException:
        msg="Unknown Error"
        return templates.TemplateResponse("login.html",{'request':request,'msg':msg})

@router.post("/user_verification", response_model=Token)
async def login_verification(response:Response,form_data:Annotated[OAuth2PasswordRequestForm,Depends()],
                       db:db_dependency):
    user=authenticate_user(form_data.username, form_data.password, db)
    if not user :
        return False 
    token=create_access_token(user.username,user.id,user.role,timedelta(minutes=60))
    response.set_cookie(key='access_token',value=token,httponly=True)
    return True 
    
    # return {'access_token':token, 'token_type':'bearer'}  ==> used when return token

@router.get("/logout")
def logout(request:Request):
    msg="Logout Successful"
    response=templates.TemplateResponse('login.html',{"request":request,"msg":msg})
    response.delete_cookie(key="access_token")
    return response

 