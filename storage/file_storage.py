"""Модуль для работы с файловым хранилищем"""

import json
import os
from typing import List
from models.goal import Goal
from utils.constants import AppConfig


def load_goals(filename: str = AppConfig.DATA_FILE) -> List[Goal]:
    """Загружает цели из JSON-файла."""
    if not os.path.exists(filename):
        return []
    
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [Goal.from_dict(item) for item in data]
    except (json.JSONDecodeError, IOError) as e:
        print(f"Ошибка при чтении файла {filename}: {e}")
        return []


def save_goals(goals: List[Goal], filename: str = AppConfig.DATA_FILE) -> bool:
    """Сохраняет цели в JSON-файл."""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump([goal.to_dict() for goal in goals], f, 
                     ensure_ascii=False, indent=4)
        return True
    except IOError as e:
        print(f"Ошибка при записи в файл {filename}: {e}")
        return False
