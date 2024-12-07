#RU
# Этот скрипт управляет пользователями, хранящимися в файле `users.ini`.
# Он позволяет добавлять пользователей, удалять их и отображать текущий список.

#ENG
# This script manages users stored in the `users.ini` file.
# It allows adding users, deleting them, and displaying the current list.

import argparse
from configparser import ConfigParser
import logging
import os

# Настраиваем логирование
logging.basicConfig(level=logging.INFO, format='%(message)s')

#RU
# Функция read_users
# На вход: ничего.
# Возвращает: объект ConfigParser с данными из `users.ini`.
# Она создаёт файл `users.ini`, если он отсутствует, и загружает данные.

#ENG
# Function read_users
# Input: none.
# Returns: a ConfigParser object with data from `users.ini`.
# It creates the `users.ini` file if it doesn't exist and loads the data.
def read_users():
    if not os.path.exists('users.ini'):
        with open('users.ini', 'w') as f:
            f.write('[USERS]\n')
    config = ConfigParser()
    config.read('users.ini')
    return config

#RU
# Функция write_users
# На вход: объект ConfigParser с обновлёнными данными.
# Возвращает: ничего.
# Она записывает изменения в файл `users.ini`.

#ENG
# Function write_users
# Input: a ConfigParser object with updated data.
# Returns: none.
# It writes the changes to the `users.ini` file.
def write_users(config):
    with open('users.ini', 'w') as f:
        config.write(f)

#RU
# Функция add_user
# На вход: имя пользователя и его ID.
# Возвращает: ничего.
# Она добавляет нового пользователя в файл `users.ini`, если имя или ID ещё не используются.

#ENG
# Function add_user
# Input: username and user ID.
# Returns: none.
# It adds a new user to the `users.ini` file if the username or ID are not already used.
def add_user(user_name, user_id):
    config = read_users()
    users = config['USERS']
    
    if user_name in users:
        logging.info(f"Пользователь {user_name} уже существует с ID {users[user_name]}. Используйте флаг -s для просмотра пользователей.")
    elif user_id in users.values():
        logging.info(f"ID {user_id} уже привязан к пользователю {list(users.keys())[list(users.values()).index(user_id)]}. Используйте флаг -s для просмотра пользователей.")
    else:
        users[user_name] = user_id
        write_users(config)
        logging.info(f"Пользователь {user_name} с ID {user_id} успешно добавлен.")

#RU
# Функция delete_user
# На вход: имя пользователя или его ID.
# Возвращает: ничего.
# Она удаляет пользователя из файла `users.ini` по имени или ID.

#ENG
# Function delete_user
# Input: username or user ID.
# Returns: none.
# It removes the user from the `users.ini` file by name or ID.
def delete_user(identifier):
    config = read_users()
    users = config['USERS']
    
    if identifier in users:
        del users[identifier]
        write_users(config)
        logging.info(f"Пользователь {identifier} успешно удалён.")
    elif identifier in users.values():
        user_name = list(users.keys())[list(users.values()).index(identifier)]
        del users[user_name]
        write_users(config)
        logging.info(f"Пользователь с ID {identifier} ({user_name}) успешно удалён.")
    else:
        logging.info(f"Пользователь с именем или ID {identifier} не найден. Используйте флаг -s для просмотра пользователей.")

#RU
# Функция show_users
# На вход: ничего.
# Возвращает: ничего.
# Она отображает всех пользователей, хранящихся в файле `users.ini`.

#ENG
# Function show_users
# Input: none.
# Returns: none.
# It displays all users stored in the `users.ini` file.
def show_users():
    config = read_users()
    users = config['USERS']
    if users:
        logging.info("Список пользователей:")
        logging.info('USERNAME  |  ID')
        for user_name, user_id in users.items():
            logging.info(f"{user_name} = {user_id}")
    else:
        logging.info("В файле users.ini пока нет пользователей.")

# Основной блок для работы с флагами
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Управление пользователями в файле users.ini")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-a', '--add', nargs=2, metavar=('USER_NAME', 'USER_ID'), help='Добавить пользователя (имя и ID)')
    group.add_argument('-d', '--delete', metavar='IDENTIFIER', help='Удалить пользователя (имя или ID)')
    group.add_argument('-s', '--show', action='store_true', help='Показать список пользователей')

    args = parser.parse_args()

    if args.add:
        user_name, user_id = args.add
        add_user(user_name, user_id)
    elif args.delete:
        identifier = args.delete
        delete_user(identifier)
    elif args.show:
        show_users()
