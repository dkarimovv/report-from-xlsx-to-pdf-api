#RU
# Этот скрипт предоставляет функции для работы с файлами, возвращая абсолютные пути
# к различным файлам и директориям относительно текущей структуры проекта.

#ENG
# This script provides functions for working with files, returning absolute paths
# to various files and directories relative to the current project structure.

import os

#RU
# Функция get_file
# На вход: имя файла (строка).
# Возвращает: абсолютный путь к файлу, находящемуся на один уровень выше текущего скрипта.
# Используется для работы с файлами, расположенными в корневой директории проекта.

#ENG
# Function get_file
# Input: file name (string).
# Returns: absolute path to a file located one level above the current script.
# Used for working with files located in the project's root directory.
def get_file(filename : str) -> str:
        current_dir = os.path.dirname(os.path.abspath(__file__))  # Путь к директории текущего скрипта
        file_path = os.path.abspath(os.path.join(current_dir, '..', filename))

        return file_path

#RU
# Функция get_downloaded_file
# На вход: имя файла (строка).
# Возвращает: абсолютный путь к файлу в папке `downloads`, находящейся на уровень выше текущего скрипта.
# Предназначена для доступа к скачанным файлам.

#ENG
# Function get_downloaded_file
# Input: file name (string).
# Returns: absolute path to a file in the `downloads` folder located one level above the current script.
# Intended for accessing downloaded files.
def get_downloaded_file(filename : str) -> str:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.abspath(os.path.join(current_dir, '..', 'downloads',filename))

        return file_path

#RU
# Функция get_local_file
# На вход: имя файла с расширением (строка).
# Возвращает: абсолютный путь к файлу, находящемуся в той же директории, что и текущий скрипт.
# Используется для работы с локальными файлами.

#ENG
# Function get_local_file
# Input: file name with extension (string).
# Returns: absolute path to a file located in the same directory as the current script.
# Used for working with local files.
def get_local_file(filename_with_extension : str) -> str:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.abspath(os.path.join(current_dir, filename_with_extension))

        return file_path

#RU
# Функция get_downloaded_file_api
# На вход: имя файла (строка).
# Возвращает: абсолютный путь к файлу в папке `downloads/api` относительно корневой директории проекта.
# Если путь уже абсолютный и содержит `downloads/api`, возвращает его без изменений.

#ENG
# Function get_downloaded_file_api
# Input: file name (string).
# Returns: absolute path to a file in the `downloads/api` folder relative to the project's root directory.
# If the path is already absolute and contains `downloads/api`, it returns it unchanged.
def get_downloaded_file_api(filename: str) -> str:
    # Если путь уже абсолютный и содержит 'downloads/api', возвращаем его
    if os.path.isabs(filename) and 'downloads/api' in filename:
        return filename

    # Путь к корневой директории проекта
    current_dir = os.path.dirname(os.path.abspath(__file__))  # Текущая папка
    base_dir = os.path.abspath(os.path.join(current_dir, '..'))  # Корневая папка проекта

    # Формируем путь
    file_path = os.path.abspath(os.path.join(base_dir, 'downloads', 'api', filename))
    return file_path


