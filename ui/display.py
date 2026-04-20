"""Модуль для отображения данных"""

from typing import List
from models.goal import Goal
from utils.constants import AppConfig


def display_goals_list(goals: List[Goal], verbose: bool = False) -> bool:
    """Выводит список всех целей с номерами."""
    if not goals:
        print("Нет сохранённых целей.")
        return False
    
    print("\nСписок целей:")
    print("-" * 80)
    
    for i, goal in enumerate(goals, start=1):
        progress = goal.get_progress_percentage()
        
        # Основная информация
        status_mark = "✅" if goal.status == AppConfig.ACHIEVED_STATUS else "⏳"
        print(f"{i}. {status_mark} {goal.name}")
        print(f"   Сумма: {goal.current_balance:.2f} / {goal.target_amount:.2f} руб.")
        print(f"   Прогресс: {progress:.1f}%")
        
        # Дополнительная информация
        if verbose or AppConfig.VERBOSE_MODE:
            print(f"   Категория: {goal.category}")
            print(f"   Статус: {goal.status}")
        
        # Дедлайн
        if goal.deadline:
            print(f"   Дата завершения: {goal.deadline}")
        
        # Ожидаемая дата
        estimated_date = goal.get_estimated_completion_date()
        if estimated_date:
            print(f"   Ожидаемая дата: {estimated_date}")
        
        print("-" * 80)
    
    return True


def show_progress_bar(percentage: float, length: int = AppConfig.PROGRESS_BAR_LENGTH) -> str:
    """Создает строку прогресс-бара"""
    filled = int(length * percentage / 100)
    return "█" * filled + "░" * (length - filled)