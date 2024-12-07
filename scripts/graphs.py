#RU
# Этот скрипт реализует создание пирогового графика с использованием библиотеки Plotly.
# Основная задача — визуализировать данные о транзакциях компаний,
# группируя малозначительные компании в категорию "Остальные компании".

#ENG
# This script implements pie chart creation using the Plotly library.
# The main task is to visualize company transaction data,
# grouping insignificant column1 into the "Other column1" category.
import plotly.graph_objs as go
import logging

#RU
# Функция create_pie_chart
# На вход: список данных о компаниях и транзакциях (all_info) и порог для фильтрации (threshold).
# Возвращает: словарь с данными для пирогового графика.
# Она фильтрует компании по порогу, группирует малозначительные компании
# и создаёт визуализацию с общей суммой транзакций.

#ENG
# Function create_pie_chart
# Input: list of company and transaction data (all_info) and a filtering threshold (threshold).
# Returns: a dictionary with data for the pie chart.
# It filters column1 by the threshold, groups insignificant column1,
# and creates a visualization with the total transaction amount.
def create_pie_chart(all_info: list, threshold: float = 0.01) -> dict:
    column3 = []
    column4 = []

    # Собираем данные о компаниях и транзакциях
    for i in all_info:
        column3.append(i['column1'])
        column4.append(i['column2'])

    # Обработка ошибок в данных транзакций
    if not column4 or any(t is None or not isinstance(t, (int, float)) for t in column4):
        logging.info("Некорректные данные транзакций, подставляем заглушки.")
        column4 = [1] * len(column3)
    
    # Обработка ошибок в данных компаний
    if not column3 or any(c is None or not isinstance(c, str) for c in column3):
        logging.info("Некорректные данные компаний, подставляем заглушки.")
        column3 = [f"Company {i}" for i in range(len(column4))]


    # Проверка на соответствие длины списков
    if len(column4) != len(column3):
        logging.info("Несоответствие длин списков транзакций и компаний. Обрезаем до минимальной длины.")
        min_length = min(len(column4), len(column3))
        column4 = column4[:min_length]
        column3 = column3[:min_length]
    
    # Рассчитываем общий объем транзакций
    total_column4 = sum(column4)
    
    # Новые списки для обновленных данных
    filtered_column1 = []
    filtered_column4 = []
    other_sum = 0

    # Фильтрация компаний по порогу и объединение малых компаний
    for company, transaction in zip(column3, column4):
        share = transaction / total_column4
        if share >= threshold:  # Если доля компании больше порога, оставляем её
            filtered_column1.append(company)
            filtered_column4.append(transaction)
        else:  # Иначе добавляем сумму транзакции к "Остальным компаниям"
            other_sum += transaction
    
    # Добавляем категорию "Остальные компании", если есть компании ниже порога
    if other_sum > 0:
        filtered_column1.append("Остальные компании")
        filtered_column4.append(other_sum)
    
    # Создаем пироговый график с использованием plotly
    pie = go.Figure(
        data=[go.Pie(labels=filtered_column1, values=filtered_column4, hole=0.3)]
    )
    
    # Добавляем аннотацию с общей суммой транзакций
    pie.update_layout(
        title_text=f"Общая сумма: {total_column4:.1f} ₽",
        title_font_size=18,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )

    return pie.to_dict()
