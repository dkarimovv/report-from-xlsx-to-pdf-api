#RU
# Этот скрипт реализует функциональность Telegram-бота для обработки .xlsx файлов.
# Основные задачи включают: проверку доступа пользователей, загрузку файлов, их обработку
# и генерацию отчетов в формате PDF. Также предусмотрена очередь для последовательной
# обработки файлов.

#ENG
# This script implements a Telegram bot for processing .xlsx files.
# Key functionalities include user access control, file upload, file processing,
# and generating PDF reports. A queue is used for sequential file processing.
import logging
import os
import asyncio
import re
import sys

from configparser import ConfigParser

import pandas as pd
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from scripts.commands import get_file
from scripts.process import generate_report

queue = asyncio.Queue()
queue_positions = {}

#RU
# Функция is_user_allowed
# На вход: ID пользователя (int).
# Возвращает: True, если пользователь разрешен, иначе False.
# Проверяет доступ пользователя по ID, сверяя с конфигурацией.

#ENG
# Function is_user_allowed
# Input: user ID (int).
# Returns: True if the user is allowed, otherwise False.
# Verifies user access by ID against the configuration.
def is_user_allowed(user_id: int) -> bool:
    config_path = get_file('config.ini')
    config = ConfigParser()
    config.read(config_path)
    users_str = config['PARAMS']['Users']
    allowed_users = [int(user_id.strip()) for user_id in users_str.split(',')]
    return user_id in allowed_users

#RU
# Функция check_user
# На вход: ID пользователя (int).
# Возвращает: True, если пользователь имеет доступ, иначе False.
# Логирует попытки доступа для пользователей без разрешений.

#ENG
# Function check_user
# Input: user ID (int).
# Returns: True if the user has access, otherwise False.
# Logs access attempts for unauthorized users.
def check_user(user_id) -> bool:
    if not is_user_allowed(user_id):
        logging.info(f"Попытка доступа от пользователя {user_id}, которому запрещено пользоваться ботом.")
        return  False
    
    return True

#RU
# Функция start_bot
# На вход: объект конфигурации ConfigParser и BOT-TOKEN.
# Возвращает: ничего.
# Инициализирует и запускает Telegram-бот с проверкой корректности токена.

#ENG
# Function start_bot
# Input: ConfigParser object and BOT-TOKEN.
# Returns: none.
# Initializes and starts the Telegram bot, verifying the token's validity.
def start_bot(config: ConfigParser, API_KEY='') -> None:
    try:
        if API_KEY == '':
            setup_logging()
            logging.info('Не был получен BOT-TOKEN. Берем значение из config.ini')
            API_KEY = config['KEYS']['Bot_api']
                
            if API_KEY != '' and len(API_KEY) == 46:
                logging.info("Запускаем бота.")
                main(API_KEY, config)
            else:
                logging.error('Не удалось получить корректный BOT-TOKEN. Завершаем работу')
                sys.exit(1)

        elif len(API_KEY) == 46:
            logging.info('Получен BOT-TOKEN')
            logging.info("Запускаем бота.")
            main(API_KEY, config)
        else:
            logging.error('Не удалось получить корректный BOT-TOKEN. Завершаем работу')
            sys.exit(1)

    except Exception as e:
        logging.error(f'Возникла ошибка при запуске бота {e}. Выключаем программу')

#RU
# Функция download_xlsx_file
# На вход: объект Update и контекст ContextTypes.
# Возвращает: ничего.
# Загружает .xlsx файл от пользователя, проверяет его структуру
# и добавляет в очередь обработки.

#ENG
# Function download_xlsx_file
# Input: Update object and ContextTypes context.
# Returns: none.
# Downloads a .xlsx file from the user, validates its structure,
# and adds it to the processing queue.
async def download_xlsx_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Проверка доступа пользователя
    if not check_user(update.message.from_user.id):
        return
    
    user_id = update.message.from_user.id
    user_name = update.message.from_user.name
    if update.message.document:
        mime_type = update.message.document.mime_type
        original_file_name = update.message.document.file_name

        # Проверяем MIME-тип для .xlsx файлов
        if mime_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
            # Отправляем сообщение о добавлении в очередь
            position = queue.qsize() + 1  # Рассчитываем позицию нового файла в очереди
            await update.message.reply_text(
                f"Ваш файл добавлен в очередь под номером *{position}*. Пожалуйста, ожидайте.",
                parse_mode="Markdown"
            )

            # Асинхронно загружаем файл
            file_id = update.message.document.file_id
            file = await context.bot.get_file(file_id)
            prepared_file_name = f'{user_id}_{original_file_name}'
            os.makedirs('downloads', exist_ok=True)
            file_path = f'./downloads/{prepared_file_name}'

            await file.download_to_drive(file_path)

            

            columns_to_check =['Unnamed: 0', 'Unnamed: 1', 'Unnamed: 2', 'Unnamed: 3', 'Unnamed: 4', 'Unnamed: 5', 'Unnamed: 6', 'Unnamed: 7', 
                               'Unnamed: 8', 'Unnamed: 9', 'Unnamed: 10', 'Unnamed: 11', 'Unnamed: 12', 'Unnamed: 13', 'Unnamed: 14', 'Unnamed: 15', 
                               'Unnamed: 16', 'Unnamed: 17', 'Unnamed: 18', 'Unnamed: 19', 'Unnamed: 20', 'Unnamed: 21', 'Unnamed: 22', 'Unnamed: 23', 
                               'Unnamed: 24', 'Unnamed: 25', 'Unnamed: 26', 'Unnamed: 27', 'Unnamed: 28', 'Unnamed: 29', 
                               'Unnamed: 30', 'Unnamed: 31', 'Unnamed: 32', 'Unnamed: 33', 'Unnamed: 34', 'Unnamed: 35']
            
            try:
                # Загружаем файл в DataFrame для проверки
                df = pd.read_excel(file_path, engine='openpyxl')
                
                # Проверяем соответствие столбцов
                if list(df.columns) != columns_to_check:
                    # Уведомляем пользователя о несоответствии и удаляем файл
                    await update.message.reply_text(
                        "Ваш файл не является типовым и не будет обработан. Пожалуйста, отправьте файл с корректной структурой."
                    )
                    os.remove(file_path)
                    logging.info(f"Пользователь {user_name} || ID {user_id} отправил не типовой файл {original_file_name} он был удален")
                    
            except Exception as e:
                # В случае ошибки загрузки файла в DataFrame
                await update.message.reply_text(
                    "Произошла ошибка при проверке вашего файла. Пожалуйста, убедитесь, что файл в формате .xlsx и повторите попытку."
                )
                logging.error(f"Ошибка при чтении файла {file_path} от пользователя Пользователь {user_name} || ID {user_id}: {e}")
                os.remove(file_path)
                return
            
            # Добавляем файл в очередь после загрузки
            queue_positions[file_path] = (position, user_id)
            await queue.put((file_path, user_id))
        else:
            logging.info(f'Пользователь {user_name} || ID {user_id} отправил не xlsx файл: {original_file_name} с MIME-типом {mime_type}')
            await update.message.reply_text('Пожалуйста, отправьте файл в формате .xlsx.')
    else:
        logging.info(f'Пользователь {user_name} || ID {user_id} отправил текстовое сообщение {update.message.text}')

#RU
# Функция process_file_download
# На вход: объект Update и контекст ContextTypes.
# Возвращает: путь к загруженному файлу и ID пользователя.
# Загружает файл от пользователя и проверяет его формат.

#ENG
# Function process_file_download
# Input: Update object and ContextTypes context.
# Returns: file path and user ID.
# Downloads a file from the user and validates its format.
async def process_file_download(update: Update, context: ContextTypes.DEFAULT_TYPE) -> tuple:
    try:
        if update.message.document:
            user_id = update.message.from_user.id
            mime_type = update.message.document.mime_type
            original_file_name = update.message.document.file_name

            # Проверяем MIME-тип для .xlsx файлов
            if mime_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
                file_id = update.message.document.file_id
                file = await context.bot.get_file(file_id)
                
                prepared_file_name = f'{user_id}_{original_file_name}'
                
                os.makedirs('downloads', exist_ok=True)
                file_path = f'./downloads/{prepared_file_name}'
                
                await file.download_to_drive(file_path)
                return file_path, user_id
            else:
                logging.info(f'Пользователь {user_id} отправил не .xlsx файл: {original_file_name} с MIME-типом {mime_type}')
                await update.message.reply_text('Пожалуйста, отправьте файл в формате .xlsx.')
                return '', ''
        else:
            return '', ''
    except Exception as e:
        logging.error(f'Ошибка при загрузке файла: {e}')
        return '', ''

#RU
# Функция handle_file
# На вход: путь к файлу (строка).
# Возвращает: путь к сгенерированному PDF или None в случае ошибки.
# Асинхронно обрабатывает файл и создает PDF-отчет.

#ENG
# Function handle_file
# Input: file path (string).
# Returns: path to the generated PDF or None in case of an error.
# Asynchronously processes the file and generates a PDF report.
async def handle_file(file_path: str) -> str:
    try:
        # Асинхронный вызов generate_report
        pdf_path = await generate_report(file_to_prepare=file_path, template='template_2')

        if pdf_path:
            logging.info(f"Отчёт успешно сгенерирован: {pdf_path}")
            return pdf_path
        else:
            logging.error(f"Ошибка при генерации отчёта для файла {file_path}")
            return None
    except Exception as e:
        logging.error(f"Ошибка при обработке файла {file_path}: {e}")
        return None
    
#RU
# Функция get_file_name
# На вход: ключ (строка).
# Возвращает: очищенное имя файла.
# Извлекает имя файла из пути.

#ENG
# Function get_file_name
# Input: key (string).
# Returns: sanitized file name.
# Extracts the file name from the path.
def get_file_name(key):
    file_path = os.path.basename(key)
    file = file_path.replace("'./downloads/" , '')
    return file

#RU
# Функция process_queue
# На вход: контекст ContextTypes.
# Возвращает: ничего.
# Последовательно обрабатывает файлы из очереди, уведомляет пользователей
# об изменении их позиций и отправляет результаты обработки.

#ENG
# Function process_queue
# Input: ContextTypes context.
# Returns: none.
# Sequentially processes files from the queue, notifies users
# of position changes, and sends processing results.
async def process_queue(context: ContextTypes.DEFAULT_TYPE) -> None:
    while True:
        try:
            if queue.empty():
                return

            file_path, user_id = await queue.get()

            # Удаляем текущий файл из позиций и сохраняем изменения для оставшихся файлов
            queue_positions.pop(file_path, None)
            updated_positions = {}

            # Обновляем позиции всех оставшихся файлов
            for key, (pos, file_user_id) in queue_positions.items():
                new_position = pos - 1
                updated_positions[key] = (new_position, file_user_id)
                # Отправляем уведомление только владельцу файла о его новой позиции
                await context.bot.send_message(
                    chat_id=file_user_id, 
                    text=f"Ваш файл ***{get_file_name(key)}*** сместился в очереди и теперь под номером *{new_position}*.",
                    parse_mode="Markdown"
                )

            # Применяем обновления к словарю queue_positions после итерации
            queue_positions.update(updated_positions)
            file_name = file_path.replace('./downloads/', '')

            logging.info(f'Был скачен файл {file_name}')

            # Асинхронная обработка файла
            pdf_path = await handle_file(file_name)
            
            if pdf_path:
                if os.path.getsize(pdf_path) > 0:
                    # Отправляем файл пользователю, если его размер больше нуля
                    await context.bot.send_message(
                        chat_id=user_id, 
                        text=f"Ваш файл ***{get_file_name(file_path)}*** обработался.",
                        parse_mode="Markdown"
                    )
                    with open(pdf_path, 'rb') as document:
                        await context.bot.send_document(chat_id=user_id, document=document)
                    logging.info(f"Результат отправлен пользователю ID {user_id}")
                else:
                    # Если файл пустой, отправляем сообщение об ошибке
                    await context.bot.send_message(
                        chat_id=user_id, 
                        text="При обработке вашего файла произошла ошибка. Пожалуйста, попробуйте еще раз."
                    )
                    logging.error(f"Файл {pdf_path} пустой и не был отправлен пользователю {user_id}")
            
            await asyncio.to_thread(os.remove, file_path)

            queue.task_done()
        except Exception as e:
            logging.error(f"Ошибка в process_queue: {e}")

#RU
# Функция start
# На вход: объект Update и контекст ContextTypes.
# Возвращает: ничего.
# Приветствует пользователя и предлагает отправить файл .xlsx.

#ENG
# Function start
# Input: Update object and ContextTypes context.
# Returns: none.
# Greets the user and prompts them to send a .xlsx file.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Проверка доступа пользователя
    if not check_user(update.message.from_user.id):
        return

    logging.info(f'Отправлено приветственное сообщение пользователю {update.message.from_user.name} | ID: {update.message.from_user.id}')
    await update.message.reply_text('Отправьте файл .xlsx, а я подготовлю отчет по вашему файлу!')

async def description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not check_user(update.message.from_user.id):
        return
    logging.info(f'Отправлено описание бота отправлено пользователю {update.message.from_user.name} |ID: {update.message.from_user.id}')
    await update.message.reply_text('''Этот бот подготовит отчет по вашему xlsx файлу. Ваш файл должен быть типовым''')

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not check_user(update.message.from_user.id):
        return
    await update.message.reply_text(':P')

# Функция-фильтр для проверки разрешенных пользователей

def get_masked_token(api_key):
    return "<BOT_TOKEN>"

def create_token_pattern(api_key):
    # Создаем регулярное выражение для поиска и замены токена
    return re.compile(re.escape(api_key))

#RU
# Класс MaskedTokenFilter
# На вход: регулярное выражение для токена и замаскированный токен.
# Обеспечивает фильтрацию логов, заменяя реальные токены на замаскированный вариант.

#ENG
# Class MaskedTokenFilter
# Input: regular expression for the token and masked token.
# Ensures log filtering by replacing real tokens with a masked version.
class MaskedTokenFilter(logging.Filter):
    def __init__(self, token_pattern, masked_token):
        super().__init__()
        self.token_pattern = token_pattern
        self.masked_token = masked_token

    def filter(self, record):
        # Маскируем токен в record.msg
        if record.msg:
            record.msg = self.token_pattern.sub(self.masked_token, str(record.msg))

        # Приводим аргументы к строке, чтобы избежать ошибок форматирования
        if record.args:
            record.args = tuple(
                str(arg) if not isinstance(arg, (int, float)) else arg
                for arg in record.args
            )
        return True

# Настройка основного логгера и фильтра
def setup_logging(api_key):
    masked_token = get_masked_token(api_key)
    token_pattern = create_token_pattern(api_key)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.addFilter(MaskedTokenFilter(token_pattern, masked_token))

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Логирование в файл
    file_handler = logging.FileHandler('logs.txt')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logging.getLogger('telegram').setLevel(logging.ERROR)
    logging.getLogger('httpx').setLevel(logging.ERROR)
    logging.getLogger('apscheduler').setLevel(logging.ERROR)

    logging.info("Логирование настроено. Токен замаскирован.")




def main(API_KEY: str, config: ConfigParser) -> None:
    # Создаем приложение Telegram
    application = Application.builder().token(API_KEY).build()

    # Создаем JobQueue и добавляем задачу для очереди
    job_queue = application.job_queue
    job_queue.run_repeating(process_queue, interval=3, first=0)

    # Добавляем обработчики команд
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('description', description))

    # Обработчик для документов (.xlsx файлов)
    application.add_handler(MessageHandler(filters.Document.ALL, download_xlsx_file))

    # Запускаем бота
    application.run_polling()
