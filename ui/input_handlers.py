"""Модуль для обработки пользовательского ввода"""

import re
from typing import Optional, List
from models.goal import Goal
from ui.display import display_goals_list


def select_goal(goals: List[Goal], prompt: str = "Выберите номер цели") -> Optional[Goal]:
    """Универсальная функция выбора цели"""
    if not goals:
        print("Нет сохранённых целей.")
        return None
    
    if not display_goals_list(goals):
        return None
    
    while True:
        try:
            choice = input(f"\n{prompt} (0 — отмена): ").strip()
            if choice == "0":
                return None
            
            index = int(choice) - 1
            if 0 <= index < len(goals):
                return goals[index]
            
            print(f"Ошибка: введите число от 1 до {len(goals)} или 0 для отмены.")
        except ValueError:
            print("Ошибка: введите корректное число.")


def get_positive_float(prompt: str) -> Optional[float]:
    """Вспомогательная функция для ввода положительного числа"""
    while True:
        try:
            value = float(input(prompt))
            if value <= 0:
                print("Сумма должна быть больше нуля.")
                continue
            return value
        except ValueError:
            print("Пожалуйста, введите число.")
        except KeyboardInterrupt:
            print("\nОперация отменена.")
            return None


def get_deadline_if_valid() -> Optional[str]:
    """Вспомогательная функция для ввода даты"""
    # Обновлённый шаблон с группами захвата для разбора компонентов даты
    date_pattern = r'^(0[1-9]|[12][0-9]|3[01])([-./])(0[1-9]|1[0-2])\2(\d{2}|\d{4})$'
    deadline = input("Дата завершения (ДД.ММ.ГГГГ опционально): ").strip()

    if deadline:
        match = re.fullmatch(date_pattern, deadline)
        if match:
            day, separator, month, year = match.groups()

            # Преобразуем двухзначный год в четырёхзначный (все даты после 2000 года)
            if len(year) == 2:
                year = f"20{year}"
            else:
                year = year  # Уже четырёхзначный

            # Форматируем в ДД-ММ-ГГГГ
            formatted_date = f"{day}-{month}-{year}"
            return formatted_date
        else:
            print("Неверный формат даты. Дата не будет установлена.")
    return None
