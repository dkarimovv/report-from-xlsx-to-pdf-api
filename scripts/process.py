#RU
# Этот скрипт предоставляет функции для обработки файлов, генерации отчетов в формате PDF
# и взаимодействия с шаблонами HTML. Использует асинхронное программирование для работы
# с браузером Playwright и генерации PDF.

#ENG
# This script provides functions for file processing, generating PDF reports,
# and interacting with HTML templates. It uses asynchronous programming to work
# with the Playwright browser and PDF generation.
import os
import asyncio
import secrets
import string
import warnings
import platform
import logging

import pandas as pd
import requests as re

import re as r

from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from concurrent.futures import ThreadPoolExecutor
from playwright.async_api import async_playwright
from PyPDF2 import PdfMerger



from .graphs import create_pie_chart
from .commands import get_downloaded_file, get_local_file, get_downloaded_file_api

#PS Заглушка
def current_time():
    pass

#RU
# Функция sanitize_filename
# На вход: имя файла (строка).
# Возвращает: строку, в которой недопустимые символы заменены на '_'.
# Обеспечивает безопасность имен файлов.

#ENG
# Function sanitize_filename
# Input: file name (string).
# Returns: a string where invalid characters are replaced with '_'.
# Ensures file name safet
def sanitize_filename(filename: str) -> str:
    # Заменяет недопустимые символы для файлов на '_'
    return r.sub(r'[<>:"/\\|?*]', '_', filename)


#RU
# Функция process_inputs
# На вход: параметры для обработки файлов, шаблонов и периода.
# Возвращает: выбранные файлы, шаблон и обработанный период.
# Обрабатывает пользовательский ввод для выбора соответствующих данных.

#ENG
# Function process_inputs
# Input: parameters for processing files, templates, and periods.
# Returns: selected files, template, and processed period.
# Handles user input for selecting appropriate data.
def process_inputs(file_responce , template_responce, period_responce ):
    # Process files input
    all_files = [f for f in os.listdir() if f.endswith('.xlsx') or f.endswith('.xls')]
    file_responce = int(file_responce)
    if file_responce == 0:
        file_to_work = all_files
    else:
        file_to_work = all_files[file_responce-1]
    
    
#     # Process templates
    all_htmls = [f for f in os.listdir('./templates') if f.endswith('.html')]
    all_templates = []
    for i in all_htmls:
        if 'template' in i:
            all_templates.append(i)
    template_responce = int(template_responce)
    if template_responce == 0:
        print('Error was choosed wrong template')
    else:
        template_to_work = all_templates[template_responce-1]

    # Process period 
    period_to_work = ''
    if len(period_responce) == 1:
        period_to_work = period_lcs(period_responce)
    else:
        if ',' in period_responce:
            args = period_responce.split(' ')
            for arg in args:
                period_to_work += f'{period_lcs(arg)}?'
            period_to_work = period_to_work[:-1] # ?????? ??? ?? ? ?? ? ? ? ?
        elif ' ' in period_responce:
            args = period_responce.split(' ')
            for arg in args:
                period_to_work += f'{period_lcs(arg)}?'
            period_to_work = period_to_work[:-1]

    return file_to_work , template_to_work , period_to_work

#RU
# Функция period_lcs
# На вход: параметр периода (строка).
# Возвращает: строку, соответствующую кварталу, месяцу или году.
# Определяет период на основе пользовательского ввода.

#ENG
# Function period_lcs
# Input: period parameter (string).
# Returns: a string representing a quarter, month, or year.
# Determines the period based on user input.
def period_lcs(period_responce):
    quarts ={
        ('one') : '08 09 10',
        ('two') : '11 12 01',
        ('three') : '02 03 04',
        ('four') : '05 06 07'
    }
    
    match period_responce:
        case '1':
            # Current month
            return current_time()['month']
        case '2':
            curm  = current_time()['month']
            if curm != '10' and curm != '01':
                pastm = f'{int(curm)//10}{(int(curm)%10)-1}'
            else:
                if curm == '10':
                    pastm = '09'
                else:
                    pastm = '12'
            return pastm
        case '3':
            curm  = current_time()['month']
            if curm in quarts['one']:
                return str(quarts['one'])
            elif curm in quarts['two']:
                return str(quarts['two'])
            elif curm in quarts['three']:
                return str(quarts['three'])
            elif curm in quarts['four']:
                return str(quarts['four'])
            else:
                print('Error. Data not in quarters')
            return []
        case '4':
            curm  = current_time()['month']
            if curm in quarts['one']:
                return str(quarts['four'])
            elif curm in quarts['two']:
                return str(quarts['one'])
            elif curm in quarts['three']:
                return str(quarts['two'])
            elif curm in quarts['four']:
                return str(quarts['three'])
            else:
                print('Error. Data not in quarters')
            return []
        case '5':
            return str(current_time()['year'])
        
#RU
# Функция generate_report
# На вход: путь к файлу, шаблон, период и флаг API.
# Возвращает: путь к сгенерированному PDF-отчету.
# Выполняет обработку данных, фильтрацию, создание графиков и генерацию PDF-файлов.

#ENG
# Function generate_report
# Input: file path, template, period, and API flag.
# Returns: path to the generated PDF report.
# Performs data processing, filtering, graph creation, and PDF generation.
async def generate_report(file_to_prepare: str, template=1, period='', api=False):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    if api:
        # Формируем путь для API вызова
        file_to_prepare = get_downloaded_file_api(file_to_prepare)
        logging.info(f"Путь для API вызова: {file_to_prepare}")
    else:
        # Для обычного вызова
        file_to_prepare = get_downloaded_file(file_to_prepare)
        logging.info(f"Локальный путь: {file_to_prepare}")

    if not os.path.exists(file_to_prepare):
        raise FileNotFoundError(f"Файл не найден: {file_to_prepare}")

    file_name = prepare_table(file_to_prepare, api=api)

    # Загружаем данные из Excel файла
    df = pd.read_excel(file_name, engine='openpyxl')

    if len(df.columns) != 0:
        logging.info(f'Открыли полученный файл {file_name}')
    else:
        logging.error(f'Не смогли получить доступ к файлу {file_name}')
        raise FileNotFoundError(f"Файл пустой или повреждён: {file_name}")

    # Приводим названия к единому виду в столбцах COLUMN1 и COLUMN1.1
    replacements = {
        '''
        Replacements
        '''
    }

    df['COLUMN1'] = df['COLUMN1'].replace(replacements, regex=True)
    df['COLUMN1.1'] = df['COLUMN1.1.1'].replace(replacements, regex=True)

    # Преобразование столбца с датой операции к типу datetime
    df['COLUMN5'] = pd.to_datetime(df['COLUMN5'], errors='coerce')

    # Фильтрация данных по периоду
    filtered_df = df.copy()

    # Period handler // Не используется
    # if '?' in period:
    #     periods = period.split('?')
    #     for p in periods:
    #         if len(p) == 2:  # Проверяем только по месяцу
    #             target_month = int(p)
    #             filtered_df = pd.concat([filtered_df, df[df['COLUMN5'].dt.month == target_month]])
    #         elif len(p) == 8:  # Проверяем по кварталу (перечень месяцев)
    #             target_months = [int(m) for m in p.split()]
    #             filtered_df = pd.concat([filtered_df, df[df['COLUMN5'].dt.month.isin(target_months)]])
    #         elif len(p) == 4:  # Проверяем по году
    #             target_year = int(p)
    #             filtered_df = pd.concat([filtered_df, df[df['COLUMN5'].dt.year == target_year]])
    #         else:
    #             print("Неверный формат периода. Ожидается длина 2, 8 или 4.")
    #             return
    # else:
    #     if len(period) == 2:  # Проверяем только по месяцу
    #         target_month = int(period)
    #         filtered_df = df[df['COLUMN5'].dt.month == target_month]
    #     elif len(period) == 8:  # Проверяем по кварталу (перечень месяцев)
    #         target_months = [int(m) for m in period.split()]
    #         filtered_df = df[df['COLUMN5'].dt.month.isin(target_months)]
    #     elif len(period) == 4:  # Проверяем по году
    #         target_year = int(period)
    #         filtered_df = df[df['COLUMN5'].dt.year == target_year]
    #     else:
    #         print("Неверный формат периода. Ожидается длина 2, 8 или 4.")
    #         return

    # Проверка на пустой DataFrame после фильтрации
    # if filtered_df.empty:
    #     print("Нет данных для заданного периода.")
    #     os.remove(file_name)
    #     return

    # Проверка на пустые значения в колонке "COLUMN1.1"

    empty_column = filtered_df[filtered_df['COLUMN1.1'].isna()]
    if not empty_column.empty:
        print(f"Есть строки с пустыми наименованиями:\n{empty_column}")

    # Проверка COLUMN2 на длину
    filtered_df['COLUMN2'] = filtered_df['COLUMN2'].astype(str)
    incorrect_inn_kpo = filtered_df[~filtered_df['COLUMN2'].str.len().isin([9, 12])]
    if not incorrect_inn_kpo.empty:
        print(f"Есть строки с некорректным COLUMN2:\n{incorrect_inn_kpo}")

    filtered_df = filtered_df[filtered_df['COLUMN3'] > 0]

    if filtered_df.empty:
        print("Нет данных для компаний с ненулевыми дебетами.")
        os.remove(file_name)
        return

    # Группировка данных и расчет сумм
    report = filtered_df.groupby(['COLUMN1.1', 'COLUMN2']).agg({
        'COLUMN5': 'first',  # Можно заменить на 'min' для получения первой даты
        'COLUMN3': lambda x: round(x.sum(), 2),
        'COLUMN4': '<br><br>'.join
    }).reset_index()
    
    # Проверка, чтобы убедиться, что есть данные для названия компании
    if not filtered_df['COLUMN1'].empty:
        column1 = filtered_df['COLUMN1'].iloc[0]
    else:
        column1 = "Unknown"
    column2 = []
    column3 = report['COLUMN1.1'].unique().tolist()

    for _, row in report.iterrows():
        column2.append({
            'date': row['COLUMN5'].strftime('%Y-%m-%d'),
            'column1': row['COLUMN1.1'],
            'company_inn': row['COLUMN2'],
            'debit': row['COLUMN3'],
            'payment_description': row['COLUMN4']
        })

    # Сохраняем в новый Excel файл
    today_date = datetime.now().strftime("%Y%m%d")
    output_file_name = sanitize_filename(f'Отчет_{column1}_{today_date}_{create_password()}')

    # Вспомогательная асинхронная функция для генерации PDF
    async def generate_pdfs():
        pdf_path = await templates_handler('template_2.html', column1, column2, column3, output_file_name)
        intermediary_output_file = f'companies_{output_file_name}'
        intermediary_pdf_path = await templates_handler('test.html', column1, [], column3, intermediary_output_file)
        graph_output_file = f'graph_{output_file_name}'
        graph_pdf_path = await templates_handler('graph.html', column1, column2, column3, graph_output_file)
        return pdf_path, intermediary_pdf_path, graph_pdf_path

    # Запускаем асинхронную функцию и получаем пути к файлам
    pdf_path, intermediary_pdf_path, graph_pdf_path = await generate_pdfs()

    if api:
        pdf_path = get_downloaded_file(pdf_path)
        intermediary_pdf_path = get_downloaded_file(intermediary_pdf_path)
        graph_pdf_path = get_downloaded_file(graph_pdf_path)
    else:
        pdf_path = get_local_file(pdf_path)
        intermediary_pdf_path = get_local_file(intermediary_pdf_path)
        graph_pdf_path = get_local_file(graph_pdf_path)

    merge_pdf(pdf_path, intermediary_pdf_path, graph_pdf_path)

    os.remove(file_name)
    logging.info(f"Генерация отчета завершена: {pdf_path}")
    return pdf_path

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

executor = ThreadPoolExecutor()



#RU
# Функция templates_handler
# На вход: тип шаблона, название компании, транзакции, список компаний и имя выходного файла.
# Возвращает: путь к сгенерированному PDF-файлу.
# Рендерит HTML на основе шаблона и преобразует его в PDF.

#ENG
# Function templates_handler
# Input: template type, company name, column2, list of companies, and output file name.
# Returns: path to the generated PDF file.
# Renders HTML based on a template and converts it to PDF.
async def templates_handler(template_type: str, column1: str, column2: list, column3: list, output_file_name: str):
    try:
        logging.info(f'Рендерим темплейт с полученными данными')
        templates_path = os.path.join(BASE_DIR, './templates')
        env = Environment(loader=FileSystemLoader(templates_path))
        template = env.get_template(template_type)

        # Создаем данные для графика в формате JSON
        graph_data = create_pie_chart(column2)

        # Рендерим HTML контент на основе шаблона
        rendered_content = template.render(
            column1=column1,
            column2=column2,
            column3=column3,
            graph_data=graph_data
        )

        html_output_path = get_local_file(f'{output_file_name}.html')
        if 'html' in template_type:
            with open(html_output_path, 'w', encoding='utf-8') as f:
                f.write(rendered_content)

        # Создаем директорию reports с использованием BASE_DIR
        reports_path = os.path.join(BASE_DIR, '../reports')
        os.makedirs(reports_path, exist_ok=True)

        pdf_output_path = os.path.join(reports_path, f"{output_file_name}.pdf")

        # Асинхронный вызов render_pdf через await
        await render_pdf(rendered_content, pdf_output_path)

        # Удаляем временный HTML файл
        os.remove(html_output_path)

        return pdf_output_path

    except Exception as e:
        logging.error(f'Возникла ошибка при попытке зарендерить шаблон с полученными данными: {e}')
        pass

def get_chrome_path():
    system = platform.system()
    if system == "Windows":
        return "C:/Program Files/Google/Chrome/Application/chrome.exe"
    elif system == "Darwin":  # MacOS
        return "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    elif system == "Linux":
        return "/usr/bin/google-chrome"
    else:
        raise EnvironmentError("Не удалось найти совместимый браузер для вашей ОС")

#RU
# Функция render_pdf
# На вход: HTML-контент и путь для сохранения PDF.
# Возвращает: ничего.
# Использует Playwright для преобразования HTML в PDF.

#ENG
# Function render_pdf
# Input: HTML content and output PDF path.
# Returns: none.
# Uses Playwright to convert HTML to PDF.
async def render_pdf(html_content: str, output_pdf_path: str):
    async with async_playwright() as p:
        # Запуск браузера в headless-режиме
        browser = await p.chromium.launch(
            headless=True,
            executable_path=get_chrome_path(),  # Убедитесь, что get_chrome_path() возвращает корректный путь
            args=["--no-sandbox", "--disable-gpu"]
        )
        page = await browser.new_page()
        
        # Устанавливаем HTML-контент
        await page.set_content(html_content)
        
        # Небольшая пауза, если требуется для загрузки динамического контента
        await asyncio.sleep(4)
        
        # Сохранение страницы как PDF
        await page.pdf(path=output_pdf_path, format="A4", print_background=True, landscape=True)
        
        await browser.close()

#RU
# Функция prepare_table
# На вход: имя файла (строка) и флаг API.
# Возвращает: имя обработанного файла.
# Удаляет ненужные строки и столбцы, очищает данные и сохраняет их в новый файл.

#ENG
# Function prepare_table
# Input: file name (string) and API flag.
# Returns: name of the processed file.
# Removes unnecessary rows and columns, cleans the data, and saves it to a new file.
def prepare_table(file_name : str, api=False) -> str:
    file_name_only = os.path.basename(file_name)
    if api:
        file_path = get_downloaded_file_api(file_name_only)
    else:
        file_path = get_downloaded_file(file_name_only)

    # Извлекаем только имя файла
    

    # Формируем путь для сохранения обработанного файла
    output_path = f'prepared_{file_name_only}'
    
    logging.getLogger('telegram').setLevel(logging.ERROR)  # Логирование телеграм-бота
    logging.getLogger('apscheduler').setLevel(logging.ERROR)
    
    warnings.simplefilter("ignore", UserWarning)
    # Чтение таблицы
    df = pd.read_excel(file_path, header=None)

    df = df.drop(df.index[13])

    # 1. Удаление первых 7 столбцов
    df = df.iloc[:, 11:]

    # 2. Удаление первых 9 строчек
    df = df.iloc[10:, :]

    df.columns = df.iloc[0] 
    df = df.drop(df.index[0])
    df = df.drop(df.index[1])

    df = df.drop(df.columns[8:10], axis=1)

    df = df.dropna(how='all')
    # Сохранение в новый файл
    df.to_excel(output_path, index=False)
    logging.info(f"Таблица успешно обработана и называется {output_path}")

    return output_path

#RU
# Функция merge_pdf
# На вход: пути к файлам таблицы, компаний и графиков.
# Возвращает: ничего.
# Объединяет несколько PDF-файлов в один отчет и удаляет временные файлы.

#ENG
# Function merge_pdf
# Input: paths to table, company, and graph files.
# Returns: none.
# Merges multiple PDF files into one report and deletes temporary files.
def merge_pdf(file_table, file_companies, file_graphs):
    merger = PdfMerger()

    title_list = get_local_file('title-page.pdf')

    # Проверяем, существует ли title-page.pdf
    merger.append(title_list)
    merger.append(file_table)
    merger.append(file_companies)
    merger.append(file_graphs)

    merger.write(file_table)
    merger.close()

    os.remove(file_companies)
    os.remove(file_graphs)
    
#RU
# Функция create_password
# На вход: ничего.
# Возвращает: случайно сгенерированный пароль длиной 5 символов.
# Используется для генерации уникальных имен файлов.

#ENG
# Function create_password
# Input: none.
# Returns: a randomly generated 5-character password.
# Used for generating unique file names.
def create_password() -> str:
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(5))
    return password