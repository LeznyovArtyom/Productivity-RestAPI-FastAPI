from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Annotated
from passlib.context import CryptContext
import jwt
from database import get_session
from models import User as UserModel, Task as TaskModel, Role as RoleModel
from sqlmodel import Session, select
from sqlalchemy.orm import joinedload
from datetime import datetime, timedelta, timezone
from base64 import b64encode, b64decode
import os


app = FastAPI(title="API Productivity", description="API для управления пользователями и задачами", version="1.0.0")


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


class UserUpdate(BaseModel):
    name: str | None = None
    login: str | None = None
    password: str | None = None
    image: bytes | None = None
    role_id: int | None = None


class Role(BaseModel):
    name: str


class Task(BaseModel):
    name: str
    description: str
    importance_id: int
    deadline: str


class TaskUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    importance_id: int | None = None
    status_id: int | None = None
    deadline: str | None = None


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


@app.get("/", summary="Получить индексную страницу", tags=["Страницы"])
def get_index_page():
    return FileResponse("html/index.html")

@app.get("/authorization", summary="Получить страницу авторизации", tags=["Страницы"])
def get_authorization_page():
    return FileResponse("html/Authorization.html")

@app.get("/registration", summary="Получить страницу регистрации", tags=["Страницы"])
def get_registration_page():
    return FileResponse("html/Registration.html")

@app.get("/my_tasks", summary="Получить страницу авторизации", tags=["Страницы"])
def get_my_tasks_page():
    return FileResponse("html/My_tasks.html")

@app.get("/complete_tasks", summary="Получить страницу завершенных задач", tags=["Страницы"])
def get_complete_tasks_page():
    return FileResponse("html/Complete_tasks.html")

@app.get("/the_trash", summary="Получить страницу корзины", tags=["Страницы"])
def get_the_trash_page():
    return FileResponse("html/The_trash.html")

@app.get("/add_task", summary="Получить страницу добавления задачи", tags=["Страницы"])
def get_add_task_page():
    return FileResponse("html/Add_task.html")

@app.get("/the_task", summary="Получить страницу задачи", tags=["Страницы"])
def get_the_task_page():
    return FileResponse("html/The_task.html")

@app.get("/settings", summary="Получить страницу настроек", tags=["Страницы"])
def get_settings_page():
    return FileResponse("html/Settings.html")


# Зарегистрировать пользователя
@app.post("/users/register", summary="Регистрация пользователя", tags=["Пользователи"])
async def register_new_user(user_data: User, session: Session = Depends(get_session)):
    """
    Регистрирует нового пользователя в системе.
    
    - **name**: имя пользователя
    - **login**: уникальный логин
    - **password**: пароль пользователя
    """
    
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
@app.post("/users/login", summary="Авторизация пользователя", tags=["Пользователи"])
async def login_user(user_data: UserLogin, session: Session = Depends(get_session)):
    """
    Авторизует пользователя и возвращает токен доступа.

    - **login**: логин пользователя
    - **password**: пароль пользователя
    """
    user = session.exec(select(UserModel).where(UserModel.login == user_data.login)).first()

    if user and verify_password(user_data.password, user.password):
        access_token = create_access_token(data={"sub": user_data.login}, expires_delta=timedelta(ACCESS_TOKEN_EXPIRE_MINUTES))
        return JSONResponse({"access_token": access_token, "token_type": "bearer"})
    else:
        raise HTTPException(status_code=401, detail="Неправильные данные для входа")


# Получить информацию о пользователе
@app.get("/users/me", summary="Получить инфорацию о текущем пользователе", tags=["Пользователи"])
async def get_info_about_me(token: Annotated[str, Depends(oauth2_scheme)], session: Session = Depends(get_session)):
    """
    Возвращает информацию о пользователе.
    Требуется авторизация с использованием токена доступа.
    """
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


# Удалить пользователя
@app.delete("/users/me/delete", summary="Удалить текущего пользователя", tags=["Пользователи"])
async def delete_user(token: Annotated[str, Depends(oauth2_scheme)], session: Session = Depends(get_session)):
    """
    Удаляет текущего пользователя из системы.
    Требуется авторизация с использованием токена доступа.
    """
    user_login = decode_access_token(token)

    user = session.exec(select(UserModel).options(joinedload(UserModel.role)).where(UserModel.login == user_login)).first()

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    session.delete(user)
    session.commit()

    return JSONResponse({"message": "Пользователь удален"}, status_code=200)


# Обновить инфорацию о пользователе
@app.put("/users/me/update", summary="Обновить информацию о текущем пользователе", tags=["Пользователи"])
async def update_user(user_data: UserUpdate, token: Annotated[str, Depends(oauth2_scheme)], session: Session = Depends(get_session)):
    """
    Обновляет информацию о текущем пользователе
    Требуется авторизация с использованием токена доступа.

    Поля для обновления: 
    - **name**: Имя пользователя
    - **login**: Логин пользователя
    - **password**: Пароль
    - **role_id**: Роль
    - **image**: Изображение пользователя
    """
    user_login = decode_access_token(token)

    user = session.exec(select(UserModel).where(UserModel.login == user_login)).first()

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    old_login = user.login

    if user_data.name:  
        user.name = user_data.name
    if user_data.login:
        user.login = user_data.login
    if user_data.password:
        user.password = get_password_hash(user_data.password)
    if user_data.role_id:
        user.role_id = user_data.role_id
    if user_data.image:
        user.image = b64decode(user_data.image)

    session.add(user)
    session.commit()
    session.refresh(user)

    if user_data.login and user_data.login != old_login:
        new_token = create_access_token(data={"sub": user_data.login})
        return JSONResponse({"message": "Пользователь успешно обновлен", "new_token": new_token}, status_code=200)

    return JSONResponse({"message": "Пользователь успешно обновлен"}, status_code=200)


# Получить все задачи текущего пользователя
@app.get("/users/me/tasks", summary="Получить все задачи текущего пользователя", tags=["Задачи"])
async def get_user_tasks(token: Annotated[str, Depends(oauth2_scheme)], session: Session = Depends(get_session)):
    """
    Возвращает список задач текущего пользователя.
    Требуется авторизация с использованием токена доступа.
    """
    user_login = decode_access_token(token)

    user = session.exec(select(UserModel).where(UserModel.login == user_login)).first()

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    tasks = session.exec(select(TaskModel).options(joinedload(TaskModel.importance), joinedload(TaskModel.status)).filter(TaskModel.user_id == user.id)).all()

    tasks_data = [
        {
            "id": task.id,
            "name": task.name,
            "description": task.description,
            "importance": task.importance.name,
            "importance_id": task.importance_id,
            "status": task.status.name,
            "deadline": task.deadline.isoformat() if task.deadline else None
        } for task in tasks
    ]

    return JSONResponse({"Tasks": tasks_data}, status_code=200)


# Получить задачу по ID
@app.get("/tasks/{task_id}", summary="Получить задачу по ID", tags=["Задачи"])
async def get_task_by_id(task_id: int, token: Annotated[str, Depends(oauth2_scheme)], session: Session = Depends(get_session)):
    """
    Возвращает информацию о задаче по её ID.
    Требуется авторизация с использованием токена доступа.

    Параметр пути: **task_id**
    """
    task = session.exec(select(TaskModel).options(joinedload(TaskModel.importance), joinedload(TaskModel.status)).filter(TaskModel.id == task_id)).first()

    if not task:
        return JSONResponse({"error": "Информация о задаче не найдена"}, status_code=404)
    
    return JSONResponse({"Task": {
                            "id": task.id,
                            "name": task.name,
                            "description": task.description,
                            "importance": task.importance.name,
                            "importance_id": task.importance_id,
                            "status": task.status.name,
                            "status_id": task.status_id,
                            "deadline": task.deadline.isoformat() if task.deadline else None 
                        }})


# Добавить задачу к конкретному пользователю
@app.post("/users/me/tasks/add", summary="Добавить новую задачу текущему пользователю", tags=["Задачи"])
async def add_new_task(task_data: Task, token: Annotated[str, Depends(oauth2_scheme)], session: Session = Depends(get_session)):
    """
    Добавляет новую задачу текущему пользователю.
    Требуется авторизация с использованием токена доступа.

    Поля для добавления задачи:
    - **name**: Название задачи
    - **descripton**: Описание задачи
    - **importance_id**: ID важности задачи
    - **deadline**: Срок выполнения задачи
    """
    user_login = decode_access_token(token)

    user = session.exec(select(UserModel).where(UserModel.login == user_login)).first()

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    new_task = TaskModel(
        name=task_data.name,
        description=task_data.description,
        importance_id=task_data.importance_id,
        status_id=1,
        deadline=datetime.fromisoformat(task_data.deadline),
        user_id=user.id
    )

    session.add(new_task)
    session.commit()
    session.refresh(new_task)

    return JSONResponse({"message": "Задача успешно добавлена"}, status_code=201)


# Обновить информацию о задаче
@app.put("/tasks/{task_id}/update", summary="Обновить информацию о задаче", tags=["Задачи"])
async def update_task(task_data: TaskUpdate, task_id: int, token: Annotated[str, Depends(oauth2_scheme)], session: Session = Depends(get_session)):
    """
    Обновляет информацию о задаче по её ID.
    Требуется авторизация с использованием токена доступа.

    Поля для обновления:
    - **name**: Название задачи
    - **descripton**: Описание задачи
    - **importance_id**: ID важности задачи
    - **status_id**: ID статуса задачи
    - **deadline**: Срок выполнения задачи
    """
    task = session.exec(select(TaskModel).filter(TaskModel.id == task_id)).first()

    if not task:
        return JSONResponse({"error": "Информация о задаче не найдена"}, status_code=404)
    
    if task_data.name:
        task.name = task_data.name
    if task_data.description:
        task.description = task_data.description
    if task_data.importance_id:
        task.importance_id = task_data.importance_id
    if task_data.status_id:
        task.status_id = task_data.status_id
    if task_data.deadline:
        task.deadline = datetime.fromisoformat(task_data.deadline)

    session.add(task)
    session.commit()
    
    return JSONResponse({"message": "Задача успешно обновлена"}, status_code=200)


# Получить список ролей
@app.get("/roles", summary="Получить список ролей", tags=["Пользователи"])
async def get_roles(token: Annotated[str, Depends(oauth2_scheme)], session: Session = Depends(get_session)):
    """
    Возвращает список всех ролей в системе.
    Требуется авторизация с использованием токена доступа.
    """
    roles = session.exec(select(RoleModel)).all()

    if not roles:
        return JSONResponse({"error": "Роли не найдены"}, status_code=404)
    
    return JSONResponse({"Roles": [
                            {
                                "id": role.id,
                                "name": role.name
                            } 
                            for role in roles
                        ]}, status_code=200)