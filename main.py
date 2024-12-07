#RU
# Этот скрипт обеспечивает логирование, синхронизацию конфигурационных файлов `users.ini` и `config.ini`, 
# инициализацию запуска программы и поддержку различных режимов работы, включая телеграм-бот.

#ENG
# This script provides logging, synchronization of configuration files `users.ini` and `config.ini`,
# initialization of program start, and support for various operation modes, including a Telegram bot.


from configparser import ConfigParser
import logging


#RU
# Функция init_logs
# На вход: ничего.
# Возвращает: ничего.
# Она настраивает логирование, добавляя обработчики для вывода логов в файл и консоль.

#ENG
# Function init_logs
# Input: none.
# Returns: none.
# It sets up logging, adding handlers for outputting logs to a file and the console.
def init_logs():

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)  # Устанавливаем уровень логирования

    # Обработчик для записи логов в файл
    file_handler = logging.FileHandler('logs.txt', mode='a')
    file_handler.setLevel(logging.INFO)

    # Обработчик для вывода логов в консоль
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO) 

    # Формат логов
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Добавляем обработчики к логгеру
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

#RU
# Функция sync_configs
# На вход: ничего.
# Возвращает: строку об успешной синхронизации или пустую строку при ошибке.
# Она синхронизирует пользователей из `users.ini` с параметром `Users` в `config.ini`,
# добавляя отсутствующие ID и удаляя лишние.

#ENG
# Function sync_configs
# Input: none.
# Returns: a string confirming successful synchronization or an empty string on error.
# It synchronizes users from `users.ini` with the `Users` parameter in `config.ini`,
# adding missing IDs and removing extra ones.
def sync_configs():
    logging.info("Начинаем синхронизацию users.ini и config.ini")

    try :
        # Читаем users.ini
        users_config = ConfigParser()
        users_config.read('users.ini')
        users_users = users_config['USERS']
        users_ids = list(users_users.values())
        logging.info(f'Всего есть {len(users_ids)} пользователей в users.ini')

        # Читаем config.ini
        config = ConfigParser()
        config.read('config.ini')
        config_users_str = config['PARAMS']['Users']

        # Очищаем лишние запятые в config.ini
        config_users_str = ",".join(filter(None, config_users_str.split(',')))
        config['PARAMS']['Users'] = config_users_str

        # Преобразуем строку пользователей из config.ini в список
        config_users_list = config_users_str.split(',')
        logging.info(f'В конфиге config.ini есть {len(config_users_list)} пользователей')

        # 1. Добавляем недостающие id в config.ini
        missing_ids = [user_id for user_id in users_ids if user_id not in config_users_list]
        if missing_ids:
            logging.info(f'Добавляем в config.ini пользователей: {", ".join(missing_ids)}')
            config_users_list.extend(missing_ids)

        # 2. Удаляем лишние id из config.ini
        extra_ids = [user_id for user_id in config_users_list if user_id not in users_ids]
        if extra_ids:
            logging.info(f'Удаляем из config.ini пользователей: {", ".join(extra_ids)}')
            config_users_list = [user_id for user_id in config_users_list if user_id not in extra_ids]

        # Обновляем параметр Users в config.ini
        config['PARAMS']['Users'] = ",".join(config_users_list)

        # Сохраняем изменения в config.ini
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
        logging.info("Синхронизация завершена успешно.")
        return 'Синхронизация завершена успешно'
    except Exception as e:
        logging.error(f'Возникла ошибка при синхронизации конфигов: {e}')
        return ''

#RU
# Функция get_config
# На вход: ничего.
# Возвращает: объект ConfigParser с данными из `config.ini`.
# Она вызывает sync_configs для обеспечения актуальности данных перед загрузкой.

#ENG
# Function get_config
# Input: none.
# Returns: a ConfigParser object with data from `config.ini`.
# It calls sync_configs to ensure data is up-to-date before loading.
def get_config():
    sync_configs()
    config = ConfigParser()
    config.read('config.ini')
    return config

#RU
# Функция report_generator_starter
# На вход: строка с API-ключом.
# Возвращает: ничего.
# Она инициирует запуск программы, настраивает логирование и проверяет режим работы (Телеграм-бот или ручной режим).

#ENG
# Function report_generator_starter
# Input: a string with an API key.
# Returns: none.
# It initiates program launch, sets up logging, and checks the operating mode (Telegram bot or manual mode).
def report_generator_starter(API_KEY:str):
    try:
        init_logs()
        logging.info('Новый запуск программы')
        config = get_config()
        if config:
            if config['PARAMS']['Mode'] == 'tg':
                logging.info('Выбран способ запуска: Телеграмм бот')
                logging.info('Запускаем телеграмм бота')
                from scripts.telegram_start import start_bot
                
                start_bot(config=config, API_KEY=API_KEY)


            elif config['PARAMS']['Mode'] == 'mn':
                logging.info('Выбран способ запуска: Ручной запуск')
                logging.info('Запускаем ручной код')
            else:
                pass
    except Exception as e:
        logging.error(f'Ошибка при запуске программы: {e}')\

if __name__ == '__main__':
    cfg = get_config()
    report_generator_starter(cfg['KEYS']['bot_api'])