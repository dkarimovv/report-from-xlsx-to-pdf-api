#RU
# Этот скрипт управляет запуском, остановкой и проверкой статуса фонового процесса.
# Он создаёт PID-файл для отслеживания процесса и логирует вывод в файлы.

#ENG
# This script manages starting, stopping, and checking the status of a background process.
# It creates a PID file to track the process and logs output to files.

import os
import sys
import signal
import subprocess
import platform

if platform.system() == "Windows":
    import win32process
    import win32con
    import win32api

#RU
# Константы
# PID_FILE: Имя файла, в котором хранится PID запущенного процесса.
# DEFAULT_PYTHON_COMMAND: Команда для запуска Python, зависящая от операционной системы.

#ENG
# Constants
# PID_FILE: The file name storing the PID of the running process.
# DEFAULT_PYTHON_COMMAND: The Python launch command, depending on the operating system.
PID_FILE = "process.pid"
DEFAULT_PYTHON_COMMAND = "python3" if platform.system() != "Windows" else "py"

#RU
# Функция start
# На вход: команда для запуска процесса (по умолчанию запускает `api.py`).
# Возвращает: ничего.
# Она запускает процесс в фоновом режиме и записывает его PID в PID-файл.
# На Windows запускает процесс без отображения окна, а на Linux — отвязывает процесс от терминала.

#ENG
# Function start
# Input: the command to start the process (defaults to launching `api.py`).
# Returns: none.
# It starts the process in the background and writes its PID to the PID file.
# On Windows, it launches the process without showing a window, and on Linux, it detaches the process from the terminal.
def start(command=None):
    if os.path.exists(PID_FILE):
        print("Процесс уже запущен!")
        sys.exit(1)

    # Устанавливаем команду по умолчанию
    if command is None:
        command = f"{DEFAULT_PYTHON_COMMAND} api.py"

    # Открываем лог-файлы
    stdout_log = open("output.log", "a")
    stderr_log = open("error.log", "a")

    if platform.system() == "Windows":
        # Windows: запускаем процесс без отображения консольного окна
        process = subprocess.Popen(
            command,
            stdout=stdout_log,
            stderr=stderr_log,
            shell=True,
            creationflags=subprocess.CREATE_NO_WINDOW  # Не показываем окно
        )
    else:
        # Linux/Unix: запускаем в фоновом режиме
        process = subprocess.Popen(
            command,
            stdout=stdout_log,
            stderr=stderr_log,
            shell=True,
            start_new_session=True  # Отвязка от терминала
        )

    # Записываем PID
    with open(PID_FILE, "w") as f:
        f.write(str(process.pid))

    print(f"Процесс запущен с PID {process.pid}!")

#RU
# Функция stop
# На вход: ничего.
# Возвращает: ничего.
# Она завершает процесс, используя его PID, и удаляет PID-файл.
# На Windows использует `taskkill`, а на Linux — `os.killpg`.

#ENG
# Function stop
# Input: none.
# Returns: none.
# It terminates the process using its PID and removes the PID file.
# On Windows, it uses `taskkill`, and on Linux, it uses `os.killpg`.
def stop():
    if not os.path.exists(PID_FILE):
        print("Процесс не запущен!")
        sys.exit(1)

    # Читаем PID из файла
    with open(PID_FILE, "r") as f:
        pid = int(f.read().strip())

    try:
        if platform.system() == "Windows":
            os.system(f"taskkill /PID {pid} /T /F")  # Убиваем процесс и дочерние процессы
        else:
            os.killpg(os.getpgid(pid), signal.SIGTERM)  # Завершаем группу процессов на Linux
    except Exception as e:
        print(f"Ошибка остановки процесса: {e}")
        sys.exit(1)

    # Удаляем PID-файл
    os.remove(PID_FILE)
    print("Процесс остановлен!")
    
#RU
# Функция status
# На вход: ничего.
# Возвращает: ничего.
# Она проверяет, запущен ли процесс, проверяя наличие PID-файла,
# и выводит соответствующее сообщение.

#ENG
# Function status
# Input: none.
# Returns: none.
# It checks if the process is running by checking the presence of the PID file,
# and prints an appropriate message.
def status():
    if os.path.exists(PID_FILE):
        with open(PID_FILE, "r") as f:
            pid = f.read().strip()
        print(f"Процесс запущен с PID {pid}.")
    else:
        print("Процесс не запущен.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python process_manager.py start|stop|status [команда]")
        sys.exit(1)

    action = sys.argv[1].lower()

    if action == "start":
        # Указываем команду по умолчанию, если не задана
        command = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else None
        start(command)
    elif action == "stop":
        stop()
    elif action == "status":
        status()
    else:
        print("Неизвестная команда!")
