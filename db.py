#RU
# Этот скрипт управляет базой данных пользователей `users.db`.
# Он позволяет инициализировать базу, добавлять пользователей, 
# выводить список пользователей и отображать токен конкретного пользователя.
# Для выполнения операций используются аргументы командной строки.

#ENG
# This script manages the `users.db` database.
# It allows initializing the database, adding users, 
# listing users, and displaying a specific user's token.
# Operations are performed via command-line arguments.



import argparse
import os
import secrets
import sqlite3

#RU
# Константы
# DB_FILE: Имя файла базы данных.
# MASTER_PASSWORD: Пароль для доступа к токенам.

#ENG
# Constants
# DB_FILE: Database file name.
# MASTER_PASSWORD: Password for accessing tokens.
DB_FILE = "users.db"
MASTER_PASSWORD = ' '  # Простой пароль для доступа к токенам

#RU
# Функция init_db
# На вход: ничего.
# Возвращает: ничего.
# Она создаёт базу данных `users.db`, если она ещё не существует, и создаёт таблицу `users`.

#ENG
# Function init_db
# Input: none.
# Returns: none.
# It creates the `users.db` database if it does not already exist and sets up the `users` table.
def init_db():
    if not os.path.exists(DB_FILE):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            token TEXT NOT NULL
        )
        """)
        conn.commit()
        conn.close()
        print("База данных успешно создана.")
    else:
        print("База данных уже существует.")

#RU
# Функция generate_token
# На вход: ничего.
# Возвращает: строку токена, сгенерированную с помощью secrets.token_hex.
# Она создаёт уникальный токен для пользователя.

#ENG
# Function generate_token
# Input: none.
# Returns: a token string generated using secrets.token_hex.
# It generates a unique token for a user.
def generate_token():
    return secrets.token_hex(16)

#RU
# Функция add_user
# На вход: имя пользователя.
# Возвращает: ничего.
# Она добавляет нового пользователя в базу данных с уникальным токеном.

#ENG
# Function add_user
# Input: username.
# Returns: none.
# It adds a new user to the database with a unique token.
def add_user(username):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        print(f"Пользователь {username} уже существует.")
        conn.close()
        return

    token = generate_token()

    cursor.execute("INSERT INTO users (username, token) VALUES (?, ?)", (username, token))
    conn.commit()
    conn.close()
    print(f"Пользователь {username} успешно создан.")
    print(f"Токен: {token}")

#RU
# Функция mask_token
# На вход: токен в виде строки.
# Возвращает: строку токена, замаскированного для безопасности.
# Она скрывает часть токена, оставляя только первые и последние 4 символа.

#ENG
# Function mask_token
# Input: token as a string.
# Returns: the token string masked for security.
# It hides part of the token, leaving only the first and last 4 characters.
def mask_token(token):
    return f"{token[:4]}****{token[-4:]}"

#RU
# Функция list_users
# На вход: ничего.
# Возвращает: ничего.
# Она выводит список всех пользователей из базы данных, маскируя их токены.

#ENG
# Function list_users
# Input: none.
# Returns: none.
# It displays a list of all users in the database, masking their tokens.
def list_users():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT username, token FROM users")
    users = cursor.fetchall()
    conn.close()

    if not users:
        print("В базе данных нет пользователей.")
        return

    print("Список пользователей:")
    for username, token in users:
        print(f"Имя: {username}, Токен: {mask_token(token)}")

#RU
# Функция show_token
# На вход: имя пользователя и пароль.
# Возвращает: ничего.
# Она отображает полный токен указанного пользователя, если пароль введён верно.

#ENG
# Function show_token
# Input: username and password.
# Returns: none.
# It displays the full token of the specified user if the password is correct.
def show_token(username, password):
    if password != MASTER_PASSWORD:
        print("Неверный пароль.")
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT token FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()

    if not result:
        print(f"Пользователь {username} не найден.")
        return

    token = result[0]
    print(f"Токен пользователя {username}: {token}")

# Функция main
# На вход: ничего (аргументы командной строки обрабатываются автоматически).
# Возвращает: ничего.
# Она обрабатывает аргументы командной строки для выполнения операций:
# инициализация базы, добавление пользователя, вывод списка или отображение токена.

#ENG
# Function main
# Input: none (command-line arguments are processed automatically).
# Returns: none.
# It handles command-line arguments to perform operations:
# database initialization, user addition, listing users, or displaying a token.
def main():
    parser = argparse.ArgumentParser(description="Скрипт для управления users.db")
    parser.add_argument("-i", "--init", action="store_true", help="Инициализация базы данных")
    parser.add_argument("-a", "--add", metavar="USERNAME", help="Добавить нового пользователя")
    parser.add_argument("-l", "--list", action="store_true", help="Вывести список пользователей")
    parser.add_argument("-s", "--show", nargs=2, metavar=("USERNAME", "PASSWORD"), help="Показать токен пользователя")

    args = parser.parse_args()

    if args.init:
        init_db()
    elif args.add:
        add_user(args.add)
    elif args.list:
        list_users()
    elif args.show:
        username, password = args.show
        show_token(username, password)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
