from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from config import data
from typing import Annotated
import os
from passlib.context import CryptContext
import jwt
from database import get_session
from models import User as UserModel
from sqlmodel import Session, select
from sqlalchemy.orm import joinedload
from base64 import b64encode


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/css", StaticFiles(directory="css"), name="css")
app.mount("/html", StaticFiles(directory="html"), name="html")
app.mount("/js", StaticFiles(directory="js"), name="js")
app.mount("/images", StaticFiles(directory="images"), name="images")


class Token(BaseModel):
    access_token: str
    token_type: str | None = None


class User(BaseModel):
    name: str
    login: str
    password: str
    image: bytes | None = None
    role_id: int | None = None


class UserLogin(BaseModel):
    login: str
    password: str


class Role(BaseModel):
    name: str


class Task(BaseModel):
    name: str
    description: str
    importance_id: int
    status_id: int
    deadline: datetime
    user_id: int


class Imposrtanse(BaseModel):
    name: str


class Status(BaseModel):
    name: str


SECRET_KEY = "Praktika2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен истек",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    

def encode_image_to_base64(image_data):
    return b64encode(image_data).decode('utf-8')


@app.get("/")
def get_index_page():
    return FileResponse("index.html")

@app.get("/authorization")
def get_authorization_page():
    return FileResponse("html/Authorization.html")

@app.get("/registration")
def get_authorization_page():
    return FileResponse("html/Registration.html")

@app.get("/my_tasks")
def get_authorization_page():
    return FileResponse("html/My_tasks.html")

@app.get("/complete_tasks")
def get_authorization_page():
    return FileResponse("html/Complete_tasks.html")

@app.get("/the_trash")
def get_authorization_page():
    return FileResponse("html/The_trash.html")

@app.get("/add_task")
def get_authorization_page():
    return FileResponse("html/Add_task.html")

@app.get("/the_task")
def get_authorization_page():
    return FileResponse("html/The_task.html")

@app.get("/settings")
def get_authorization_page():
    return FileResponse("html/Settings.html")


# Зарегистрировать пользователя
@app.post("/users/register")
def register_new_user(user_data: User, session: Session = Depends(get_session)):
    existing_user = session.exec(select(UserModel).where(UserModel.login == user_data.login)).first()

    if existing_user:
        raise HTTPException(status_code=409, detail="Пользователь с таким логином уже существует")
    
    hashed_password = get_password_hash(user_data.password)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(current_dir, 'images/профиль.jpg')
    # Читаем изображение как байты
    with open(image_path, 'rb') as image_file:
        image_data = image_file.read()

    new_user = UserModel(
        name=user_data.name,
        login=user_data.login,
        password=hashed_password,
        image=image_data,
        role_id=1
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return JSONResponse({"message": "Пользователь успешно зарегистрирован"}, status_code=201)


# Авторизовать пользователя
@app.post("/users/login")
def login_user(user_data: UserLogin, session: Session = Depends(get_session)):
    user = session.exec(select(UserModel).where(UserModel.login == user_data.login)).first()

    if user and verify_password(user_data.password, user.password):
        access_token = create_access_token(data={"sub": user_data.login}, expires_delta=timedelta(ACCESS_TOKEN_EXPIRE_MINUTES))
        return JSONResponse({"access_token": access_token, "token_type": "bearer"})
    else:
        raise HTTPException(status_code=401, detail="Неправильные данные для входа")
    
# Получить информацию о пользователе
@app.get("/users/me")
async def get_info_about_me(token: Annotated[str, Depends(oauth2_scheme)], session: Session = Depends(get_session)):
    user_login = decode_access_token(token)

    user = session.exec(select(UserModel).options(joinedload(UserModel.role)).where(UserModel.login == user_login)).first()

    if user:
        image_base64 = encode_image_to_base64(user.image)
        return JSONResponse({"User": {
            "id": user.id,
            "name": user.name,
            "login": user.login,
            "role": user.role.name,
            "role_id": user.role.id,
            "image": image_base64
        }})
    return JSONResponse({"error": "Пользователь не найден"}, status_code=404)


# from starlette.applications import Starlette
# from starlette.routing import Route, Mount
# from starlette.templating import Jinja2Templates
# from starlette.staticfiles import StaticFiles
# from starlette.responses import JSONResponse
# from starlette.middleware.authentication import AuthenticationMiddleware
# from starlette.authentication import (
#     AuthCredentials, AuthenticationBackend, SimpleUser, UnauthenticatedUser, requires
# )
# from sqlalchemy.orm import sessionmaker, joinedload
# from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
# from sqlalchemy.future import select
# from databases import Database
# from passlib.context import CryptContext
# from datetime import datetime, timedelta
# import jwt
# from models import User, Task, Role
# from starlette.middleware.cors import CORSMiddleware
# import base64
# import os
# import config


# DATABASE_URL = f"mysql+aiomysql://root:{config.password}@localhost:3306/Productivity"


# # Создание асинхронного двигателя и базы данных
# database = Database(DATABASE_URL)
# engine = create_async_engine(DATABASE_URL, echo=True)
# SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# templates = Jinja2Templates(directory="templates")


# SECRET_KEY = "MenedgerZadach"
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 60

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# # Сверить введенный пароль с хешированным 
# def verify_password(plain_password, hashed_password):
#     return pwd_context.verify(plain_password, hashed_password)

# # Получить захешированный пароль
# def get_password_hash(password):
#     return pwd_context.hash(password)

# # Создать токен доступа
# def create_access_token(data: dict, expires_delta: timedelta = None):
#     to_encode = data.copy()
#     if expires_delta:
#         expire = datetime.utcnow() + expires_delta
#     else:
#         expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt

# # Извлечь информацию из токена
# def decode_access_token(token: str):
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         return payload
#     except jwt.ExpiredSignatureError:
#         return None
#     except jwt.InvalidTokenError:
#         return None


# # Проверка отправленного токена
# class JWTAuthanticationBackend(AuthenticationBackend):
#     async def authenticate(self, request):
#         if "authorization" not in request.headers:
#             # return UnauthenticatedUser(), AuthCredentials([])\
#             return None
        
#         auth = request.headers["authorization"]
#         scheme, token = auth.split()
#         if scheme.lower() != 'bearer':
#             return None

#         payload = decode_access_token(token)
#         if payload is None:
#             return None

#         return AuthCredentials(["authenticated"]), SimpleUser(payload["sub"])


# # Получить страницу index
# async def homepage(request):
#     return templates.TemplateResponse("index.html", {"request": request})

# # Получить страницу авторизации
# async def authorization_page(request):
#     return templates.TemplateResponse("Authorization.html", {"request": request})

# # Получить страницу регистрации
# async def registration_page(request):
#     return templates.TemplateResponse("Registration.html", {"request": request})

# # Получить страницу моих задач
# async def my_tasks_page(request):
#     return templates.TemplateResponse("My_tasks.html", {"request": request})

# # Получить страницу завершенных задач
# async def complete_tasks_page(request):
#     return templates.TemplateResponse("Complete_tasks.html", {"request": request})

# # Получить страницу корзины
# async def the_trash_page(request):
#     return templates.TemplateResponse("The_trash.html", {"request": request})

# # Получить страницу добавления задачи
# async def add_task_page(request):
#     return templates.TemplateResponse("Add_task.html", {"request": request})

# # Получить страницу задачи
# async def the_task_page(request):
#     return templates.TemplateResponse("The_task.html", {"request": request})

# # Получить страницу настроек
# async def settings_page(request):
#     return templates.TemplateResponse("Settings.html", {"request": request})

# def encode_image_to_base64(image_data):
#     return base64.b64encode(image_data).decode('utf-8') if image_data else None

# # Получить информацию о пользователе
# @requires("authenticated")
# async def get_user_info(request):
#     user_login = request.user.username
#     async with SessionLocal() as session:
#         async with session.begin():
#             result = await session.execute(select(User).options(joinedload(User.role)).filter(User.login == user_login))
#             user = result.scalar_one_or_none()
#     if user:
#         image_base64 = encode_image_to_base64(user.image)
#         return JSONResponse({"User": {
#             "id": user.id,
#             "name": user.name,
#             "login": user.login,
#             "role": user.role.name,
#             "role_id": user.role.id,
#             "image": image_base64
#         }})
#     return JSONResponse({"error": "Пользователь не найден"}, status_code=404)


# # Удалить пользователя
# @requires("authenticated")
# async def delete_user(request):
#     user_login = request.user.username
#     async with SessionLocal() as session:
#         async with session.begin():
#             result = await session.execute(select(User).filter(User.login == user_login))
#             user = result.scalar_one_or_none()
#             if user:
#                 await session.delete(user)
#                 await session.commit()
#                 return JSONResponse({"message": "Пользователь удален"}, status_code=200)
#     return JSONResponse({"error": "Пользователь не найден"}, status_code=404)


# # Зарегистрировать нового пользователя
# async def register_new_user(request):
#     data = await request.json()
#     async with SessionLocal() as session:
#         async with session.begin():
#             result = await session.execute(select(User).filter(User.login == data['login']))
#             existing_user = result.scalar_one_or_none()
#             if existing_user:
#                 return JSONResponse({"error": "Пользователь с таким логином уже существует"}, status_code=400)
            
#             try:
#                 # Декодируем изображение из base64
#                 # image_data = base64.b64decode(data['image'])

#                 current_dir = os.path.dirname(os.path.abspath(__file__))
#                 # Получить абсолютный путь к файлу image2.jpg
#                 image_path = os.path.join(current_dir, 'images/профиль.jpg')

#                 # Читаем изображение как байты
#                 with open(image_path, 'rb') as image_file:
#                     image_data = image_file.read()


#                 user = User(
#                     name=data['name'],
#                     login=data['login'], 
#                     password=get_password_hash(data['password']), 
#                     image=image_data, 
#                     role_id=1
#                 )
#                 session.add(user)
#                 await session.commit()
#                 return JSONResponse({"message": "Пользователь успешно зарегистрирован"})
#             except Exception as e:
#                 print(f"Ошибка при регистрации пользователя: {e}")
#                 await session.rollback()
#                 return JSONResponse({"error": str(e)}, status_code=400)
#         await session.close()
            

# # Авторизовать пользователя
# async def login_user(request):
#     data = await request.json()
#     async with SessionLocal() as session:
#         async with session.begin():
#             result = await session.execute(select(User).filter(User.login == data['login']))
#             user = result.scalar_one_or_none()
#             if user and verify_password(data['password'], user.password):
#                 token = create_access_token(data={'sub': user.login})
#                 return JSONResponse({"access_token": token}, status_code=200)
#             return JSONResponse({"error": "Неправильные данные"}, status_code=401)


# # Обновить инфорацию о пользователе
# @requires("authenticated")
# async def update_user(request):
#     user_login = request.user.username
#     data = await request.json()
#     async with SessionLocal() as session:
#         async with session.begin():
#             result = await session.execute(select(User).filter(User.login == user_login))
#             user = result.scalar_one_or_none()
#             if user:
#                 user.name = data.get("name", user.name)
#                 user.login = data.get("login", user.login)
#                 if "password" in data:
#                     user.password = get_password_hash(data["password"])
#                 user.role_id = data.get("role_id", user.role_id)
#                 if "image" in data:
#                     # Декодируем изображение из base64
#                     image_data = base64.b64decode(data['image'])
#                     user.image = image_data
#                 await session.commit()
#                 return JSONResponse({"message": "Пользователь успешно обновлен"}, status_code=200)
#     return JSONResponse({"error": "Пользователь не найден"}, status_code=404)


# # Получить все задачи конкретного пользователя
# @requires("authenticated")
# async def get_user_tasks(request):
#     user_login = request.user.username
#     async with SessionLocal() as session:
#         async with session.begin():
#             result = await session.execute(select(User).filter(User.login == user_login))
#             user = result.scalar_one_or_none()
#             if user:
#                 result = await session.execute(select(Task).options(joinedload(Task.importance), joinedload(Task.status)).filter(Task.user_id == user.id))
#                 tasks = result.scalars().all()
#                 return JSONResponse({"Tasks": [
#                     {
#                         "id": task.id,
#                         "name": task.name,
#                         "description": task.description,
#                         "importance": task.importance.name,
#                         "importance_id": task.importance_id,
#                         "status": task.status.name,
#                         "deadline": task.deadline.isoformat() if task.deadline else None
#                     } for task in tasks
#                 ]}, status_code=200)
#     return JSONResponse({"error": "Пользователь не найден"}, status_code=404)


# # Получить задачу по ID
# @requires("authenticated")
# async def get_task_by_id(request):
#     task_id = request.path_params["task_id"]
#     async with SessionLocal() as session:
#         async with session.begin():
#             result = await session.execute(select(Task).options(joinedload(Task.importance), joinedload(Task.status)).filter(Task.id == task_id))
#             task = result.scalar_one_or_none()
#             if task:
#                 return JSONResponse({"Task": {
#                     "id": task.id,
#                     "name": task.name,
#                     "description": task.description,
#                     "importance": task.importance.name,
#                     "importance_id": task.importance_id,
#                     "status": task.status.name,
#                     "status_id": task.status_id,
#                     "deadline": task.deadline.isoformat() if task.deadline else None 
#                 }})
#     return JSONResponse({"error": "Информация о задаче не найдена"}, status_code=404)


# # Удалить задачу
# @requires("authenticated")
# async def delete_task(request):
#     task_id = request.path_params["task_id"]
#     async with SessionLocal() as session:
#         async with session.begin():
#             result = await session.execute(select(Task).filter(Task.id == task_id))
#             task = result.scalar_one_or_none()
#             if task:
#                 await session.delete(task)
#                 await session.commit()
#                 return JSONResponse({"messege": "Задача удалена"}, status_code=200)
#     return JSONResponse({"error": "Информация о задаче не найдена"}, status_code=404)


# # Добавить задачу к конкретному пользователю
# @requires("authenticated")
# async def add_new_task(request):
#     user_login = request.user.username
#     data = await request.json()
#     async with SessionLocal() as session:
#         async with session.begin():
#             result = await session.execute(select(User).filter(User.login == user_login))
#             user = result.scalar_one_or_none()
#             if user:
#                 task = Task(
#                     name=data['name'],
#                     description=data['description'],
#                     importance_id=data['importance_id'],
#                     status_id=1,
#                     deadline=datetime.fromisoformat(data['deadline']),
#                     user_id=user.id
#                 )
#                 session.add(task)
#                 await session.commit()
#                 return JSONResponse({"message": "Задача успешно добавлена"})
#     return JSONResponse({"error": "Пользователь не найден"}, status_code=404)


# # Обновить информацию о задаче
# @requires("authenticated")
# async def update_task(request):
#     task_id = request.path_params["task_id"]
#     data = await request.json()
#     async with SessionLocal() as session:
#         async with session.begin():
#             result = await session.execute(select(Task).filter(Task.id == task_id))
#             task = result.scalar_one_or_none()
#             if task:
#                 task.name = data.get("name", task.name)
#                 task.description = data.get("description", task.description)
#                 task.importance_id = data.get("importance_id", task.importance_id)
#                 task.status_id = data.get("status_id", task.status_id)
#                 if "deadline" in data:
#                     task.deadline = datetime.fromisoformat(data["deadline"])
#                 await session.commit()
#                 return JSONResponse({"message": "Задача успешно обновлена"}, status_code=200)
#     return JSONResponse({"error": "Информация о задаче не найдена"}, status_code=404)


# # Получить список ролей
# @requires("authenticated")
# async def get_roles(request):
#     async with SessionLocal() as session:
#         async with session.begin():
#             result = await session.execute(select(Role))
#             roles = result.scalars().all()
#             if roles:
#                 return JSONResponse({"Roles": [
#                     {
#                         "id": role.id,
#                         "name": role.name
#                     } for role in roles
#                 ]}, status_code=200)
#     return JSONResponse({"error": "Роли не найдены"}, status_code=404)


# routes = [
#     Route("/", homepage),
#     Route("/authorization", authorization_page),
#     Route("/registration", registration_page),
#     Route("/my_tasks", my_tasks_page),
#     Route("/complete_tasks", complete_tasks_page),
#     Route("/the_trash", the_trash_page),
#     Route("/add_task", add_task_page),
#     Route("/the_task", the_task_page),
#     Route("/settings", settings_page),
#     Mount("/css", StaticFiles(directory="css"), name="css"),
#     Mount("/js", StaticFiles(directory="js"), name="js"),
#     Mount("/images", StaticFiles(directory="images"), name="images"),
#     Route("/users/me", get_user_info, methods=["GET"]),
#     Route("/users/me/delete", delete_user, methods=["DELETE", "POST"]),
#     Route("/users/register", register_new_user, methods=["POST"]),
#     Route("/users/login", login_user, methods=["POST"]),
#     Route("/users/me/update", update_user, methods=["PUT"]),
#     Route("/users/me/tasks", get_user_tasks, methods=["GET"]),
#     Route("/tasks/{task_id:int}", get_task_by_id, methods=["GET"]),
#     Route("/tasks/{task_id:int}/delete", delete_task, methods=["DELETE"]),
#     Route("/users/me/tasks/add", add_new_task, methods=["POST"]),
#     Route("/tasks/{task_id:int}/update", update_task, methods=["PUT"]),
#     Route("/roles", get_roles, methods=["GET"]),
# ]

# app = Starlette(routes=routes)
# app.add_middleware(AuthenticationMiddleware, backend=JWTAuthanticationBackend())

# # Настройка CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://127.0.0.1:5500"],  # Список разрешенных источников
#     allow_credentials=True,
#     allow_methods=["*"],  # Разрешенные методы
#     allow_headers=["*"],  # Разрешенные заголовки
# )