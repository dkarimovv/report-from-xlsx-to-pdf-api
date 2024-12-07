#RU
# Этот скрипт реализует REST API с использованием FastAPI.
# Он предоставляет функции аутентификации, обработки файлов, 
# управления пользователями и работы с конфигурационными данными.

#ENG
# This script implements a REST API using FastAPI.
# It provides authentication, file processing, 
# user management, and configuration data management.





import logging
import os
import re
import subprocess
import platform
import sqlite3

import pandas as pd

from fastapi import FastAPI, HTTPException, File, UploadFile, Depends, Request
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from pathlib import Path
from datetime import datetime

from setcfg import add_user, delete_user, read_users, show_users
from main import get_config, sync_configs
from scripts.process import generate_report
from scripts.telegram_start import start_bot




DB_FILE = "users.db"

security = HTTPBearer()

columns_to_check = ['Операции на счетах', 'Unnamed: 1', 'Unnamed: 2', 'Unnamed: 3', 'Unnamed: 4', 'Unnamed: 5', 'Unnamed: 6', 'Unnamed: 7', 
                    'Unnamed: 8', 'Unnamed: 9', 'Unnamed: 10', 'Unnamed: 11', 'Unnamed: 12', 'Unnamed: 13', 'Unnamed: 14', 'Unnamed: 15', 
                    'Unnamed: 16', 'Unnamed: 17', 'Unnamed: 18', 'Unnamed: 19', 'Unnamed: 20', 'Unnamed: 21', 'Unnamed: 22', 'Unnamed: 23', 
                    'Unnamed: 24', 'Unnamed: 25', 'Unnamed: 26', 'Unnamed: 27', 'Unnamed: 28', 'Unnamed: 29', 
                    'Unnamed: 30', 'Unnamed: 31', 'Unnamed: 32', 'Unnamed: 33', 'Unnamed: 34', 'Unnamed: 35']

#RU
# Классы и зависимости
# Класс User представляет данные пользователя.
# Класс ConfigUpdate используется для работы с обновлениями конфигурации.

#ENG
# Classes and dependencies
# The User class represents user data.
# The ConfigUpdate class is used for configuration updates.

class User(BaseModel):
    name: str  #RU Имя пользователя / ENG User's name
    id: str  #RU ID пользователя / ENG User's ID

class ConfigUpdate(BaseModel):
    section: str #RU Секция конфигурации / ENG Configuration section
    key: str #RU Ключ конфигурации / ENG Configuration key
    value: str #RU Значение ключа / ENG Key's value


#RU
# Функция sanitize_filename
# На вход: имя файла в виде строки.
# Возвращает: очищенное имя файла, безопасное для использования в файловой системе.
# Она заменяет недопустимые символы в имени файла на символ подчеркивания.

#ENG
# Function sanitize_filename
# Input: file name as a string.
# Returns: cleaned file name safe for use in the file system.
# It replaces invalid characters in the file name with underscores.


def sanitize_filename(filename: str) -> str:
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

#RU
# Функция verify_token
# На вход: токен пользователя.
# Возвращает: True, если токен найден в базе данных, иначе False.
# Она проверяет валидность токена, запрашивая базу данных SQLite.

#ENG
# Function verify_token
# Input: user's token.
# Returns: True if the token is found in the database, otherwise False.
# It validates the token by querying the SQLite database.


def verify_token(token: str) -> bool:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT 1 FROM users WHERE token = ?", (token,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

#RU
# Функция authenticate
# На вход: HTTP-заголовки аутентификации.
# Возвращает: токен, если он валиден.
# Если токен недействителен, выбрасывает HTTPException с кодом 401.

#ENG
# Function authenticate
# Input: HTTP authentication headers.
# Returns: token if it is valid.
# If the token is invalid, raises HTTPException with code 401.


def authenticate(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    if not verify_token(token):
        raise HTTPException(status_code=401, detail="Недействительный токен")
    return token

#RU
# Функция get_username_by_token
# На вход: токен пользователя.
# Возвращает: имя пользователя, связанное с токеном.
# Она извлекает имя пользователя из базы данных SQLite.

#ENG
# Function get_username_by_token
# Input: user's token.
# Returns: username associated with the token.
# It retrieves the username from the SQLite database.


def get_username_by_token(token: str) -> str:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT username FROM users WHERE token = ?", (token,))
    result = cursor.fetchone()
    conn.close()

    return result[0] if result else "Unknown"

# Зависимость для логирования

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="api_requests.log",
    filemode="a",
)
#RU
# Зависимость log_request
# На вход: объект запроса.
# Возвращает: ничего.
# Она логирует информацию о запросе, включая имя пользователя, URL и метод.

#ENG
# Dependency log_request
# Input: request object.
# Returns: nothing.
# It logs request information, including username, URL, and method.


async def log_request(request: Request):
    token = request.headers.get("Authorization")
    username = "Unknown"

    if token and token.startswith("Bearer "):
        token_value = token.split(" ")[1]
        username = get_username_by_token(token_value)

    logging.info(
        f"Пользователь: {username}, Путь: {request.url.path}, Метод: {request.method}, Время: {datetime.now()}"
    )

### ENTRY POINT 


app = FastAPI(dependencies=[Depends(log_request)])

#RU
# Обработчик событий startup_event
# На вход: ничего.
# Возвращает: ничего.
# Он запускает Телеграм-бот как отдельный процесс.

#ENG
# Event handler startup_event
# Input: nothing.
# Returns: nothing.
# It launches the Telegram bot as a separate process.


@app.on_event("startup")
async def startup_event():
    try:
        if platform.system() == "Windows":
            command = ["py", "main.py"]
        else:
            command = ["python3", "main.py"]

        subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Телеграм-бот запущен как отдельный процесс.")
    except Exception as e:
        print(f"Ошибка при запуске телеграм-бота: {e}")

#RU
# Маршрут /users (GET)
# На вход: токен для аутентификации.
# Возвращает: список пользователей.
# Он читает данные пользователей из конфигурации.

#ENG
# Route /users (GET)
# Input: token for authentication.
# Returns: list of users.
# It reads user data from the configuration.


@app.get("/users")
def get_users(token: str = Depends(authenticate)):
    config = read_users()
    users = config["USERS"]
    if not users:
        return {"message": "Нет пользователей"}
    return users

#RU
# Маршрут /users (POST)
# На вход: данные нового пользователя и токен для аутентификации.
# Возвращает: сообщение об успешном добавлении пользователя.
# Он добавляет нового пользователя в конфигурацию.

#ENG
# Route /users (POST)
# Input: new user data and token for authentication.
# Returns: message about successful user addition.
# It adds a new user to the configuration.


@app.post("/users")
def create_user(user: User, token: str = Depends(authenticate)):
    add_user(user.name, user.id)
    return {"message": f"Пользователь {user.name} с ID {user.id} добавлен"}

#RU
# Маршрут /users/{user_id} (DELETE)
# На вход: ID пользователя и токен для аутентификации.
# Возвращает: сообщение об успешном удалении пользователя.
# Он удаляет пользователя из конфигурации.

#ENG
# Route /users/{user_id} (DELETE)
# Input: user ID and token for authentication.
# Returns: message about successful user deletion.
# It removes a user from the configuration.


@app.delete("/users/{user_id}")
def remove_user(user_id: str, token: str = Depends(authenticate)):
    try:
        delete_user(user_id)
        return {"message": f"Пользователь с ID {user_id} удален"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

#RU
# Маршрут /download/{file_name} (GET)
# На вход: имя файла.
# Возвращает: файл для скачивания.
# Он проверяет наличие файла и возвращает его, если он существует.

#ENG
# Route /download/{file_name} (GET)
# Input: file name.
# Returns: file for download.
# It checks for file existence and returns it if found.



@app.get("/download/{file_name}")
async def download_file(file_name: str):
    file_path = f"./processed/{file_name}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Файл не найден")
    return FileResponse(path=file_path, filename=file_name, media_type='application/pdf')

#RU
# Маршрут /process (POST)
# На вход: загружаемый файл и токен для аутентификации.
# Возвращает: URL для скачивания обработанного файла.
# Он обрабатывает файл, проверяет его структуру, генерирует PDF и сохраняет результат

#ENG
# Route /process (POST)
# Input: uploaded file and token for authentication.
# Returns: URL for downloading the processed file.
# It processes the file, validates its structure, generates a PDF, and saves the result.


@app.post("/process")
async def process_files(file: UploadFile = File(...), token: str = Depends(authenticate)):
    temp_file_path = None  # Инициализация переменной

    try:
        # Проверяем, что файл загружен
        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="Файл не был отправлен или его имя отсутствует."
            )
        logging.info(f"Получен файл: {file.filename}")

        # Проверяем расширение файла
        if not file.filename.endswith(".xlsx"):
            raise HTTPException(
                status_code=400,
                detail="Неверный формат файла. Ожидается файл с расширением .xlsx"
            )

        # Создаём временную директорию для файлов API
        api_dir = Path("./downloads/api/")
        api_dir.mkdir(parents=True, exist_ok=True)

        # Очищаем имя файла
        safe_filename = sanitize_filename(file.filename)
        temp_file_path = api_dir / safe_filename  # Pathlib автоматически адаптирует путь для ОС

        # Сохраняем файл
        with open(temp_file_path, "wb") as f:
            content = await file.read()
            logging.info(f"Размер полученного файла: {len(content)} байт")
            f.write(content)
        logging.info(f"Файл успешно сохранён: {temp_file_path}")

        # Проверяем, что файл существует
        if not temp_file_path.exists():
            raise HTTPException(
                status_code=500,
                detail=f"Файл {temp_file_path} не найден после сохранения."
            )

        # Проверяем структуру данных
        import warnings
        warnings.simplefilter("ignore", UserWarning)  # Подавляем предупреждения openpyxl

        df = pd.read_excel(temp_file_path, engine="openpyxl")
        if list(df.columns) != columns_to_check:
            logging.error(f"Структура файла не соответствует требованиям: {temp_file_path}")
            raise HTTPException(
                status_code=400,
                detail="Файл не соответствует ожидаемой структуре."
            )

        # Генерируем PDF
        logging.info(f"Передаём файл в generate_report: {safe_filename}")
        pdf_path = await generate_report(file_to_prepare=str(safe_filename), api=True)

        if not Path(pdf_path).exists():
            raise HTTPException(
                status_code=500,
                detail="Ошибка при генерации отчёта."
            )

        # Возвращаем ссылку на скачивание
        processed_dir = Path("./processed")
        processed_dir.mkdir(parents=True, exist_ok=True)
        processed_file_name = Path(pdf_path).name
        processed_file_path = processed_dir / processed_file_name
        Path(pdf_path).rename(processed_file_path)  # Перемещаем PDF

        download_url = f"http://127.0.0.1:8000/download/{processed_file_name}"
        return {
            "message": "Файл успешно обработан.",
            "download_url": download_url
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error(f"Неизвестная ошибка: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Произошла ошибка при обработке файла: {str(e)}"
        )

    finally:
        if temp_file_path and temp_file_path.exists():
            temp_file_path.unlink() 

#RU
# Маршрут /config (GET)
# На вход: токен для аутентификации.
# Возвращает: текущие данные конфигурации.
# Он считывает данные из файла config.ini.

#ENG
# Route /config (GET)
# Input: token for authentication.
# Returns: current configuration data.
# It reads data from the config.ini file.

@app.get('/config')
async def get_config_data(token: str = Depends(authenticate)):
    config = get_config()
    if not config:
        return {"message": "Не удалось получить доступ к config.ini"}
    config_dict = {section: dict(config.items(section)) for section in config.sections()}
    return config_dict

#RU
# Маршрут /config (POST)
# На вход: токен для аутентификации.
# Возвращает: сообщение об успешной синхронизации конфигурации.
# Он обновляет конфигурацию, синхронизируя данные.

#ENG
# Route /config (POST)
# Input: token for authentication.
# Returns: message about successful configuration synchronization.
# It updates the configuration by syncing data.


@app.post('/config')
async def update_config_data(token: str = Depends(authenticate)):
    responce = sync_configs()
    if responce == '':
        return {"message": "Не удалось обновить config.ini"}
    return responce

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
