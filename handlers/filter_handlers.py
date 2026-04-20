"""Обработчики фильтрации"""

from typing import List
from ui import select_goal
from models.goal import Goal
from utils.constants import AppConfig


def filter_goals_by_category(goals: List[Goal]) -> None:
    """Фильтрует цели по категории."""
    if not goals:
        print("Нет сохранённых целей.")
        return
    
    print("\n--- Фильтрация по категориям ---")
    
    # Собираем уникальные категории
    categories = sorted(set(goal.category for goal in goals))
    
    if not categories:
        print("Категории не найдены.")
        return
    
    print("Доступные категории:")
    for i, category in enumerate(categories, start=1):
        count = sum(1 for goal in goals if goal.category == category)
        print(f"{i}. {category} ({count} целей)")
    
    try:
        choice = input(f"\nВыберите номер категории (1-{len(categories)}): ").strip()
        if not choice.isdigit():
            print("Неверный ввод.")
            return
        
        index = int(choice) - 1
        if not (0 <= index < len(categories)):
            print("Неверный номер категории.")
            return
        
        selected_category = categories[index]
        
        # Фильтруем цели
        filtered_goals = [goal for goal in goals if goal.category == selected_category]
        
        if not filtered_goals:
            print(f"Целей в категории '{selected_category}' не найдено.")
            return
        
        print(f"\n=== ЦЕЛИ В КАТЕГОРИИ '{selected_category.upper()}' ===")
        print("-" * 60)
        
        total_target = sum(goal.target_amount for goal in filtered_goals)
        total_current = sum(goal.current_balance for goal in filtered_goals)
        
        for goal in filtered_goals:
            progress = goal.get_progress_percentage()
            status_mark = "✅" if goal.status == AppConfig.ACHIEVED_STATUS else "⏳"
            print(f"{status_mark} {goal.name}")
            print(f"   {goal.current_balance:.2f} / {goal.target_amount:.2f} руб. ({progress:.1f}%)")
        
        if total_target > 0:
            overall_progress = (total_current / total_target) * 100
            print("-" * 60)
            print(f"📊 ИТОГО ПО КАТЕГОРИИ:")
            print(f"   {total_current:.2f} / {total_target:.2f} руб. ({overall_progress:.1f}%)")
        
    except Exception as e:
        print(f"Ошибка при фильтрации: {e}")


def configure_notifications(goals: List[Goal]) -> None:
    """Настраивает уведомления для выбранной цели."""
    if not goals:
        print("Нет сохранённых целей.")
        return
    
    goal = select_goal(goals, "Выберите цель для настройки уведомлений")
    if not goal:
        print(AppConfig.MSG_CANCEL)
        return
    
    set_notification_percentages(goal)


def set_notification_percentages(goal: Goal) -> None:
    """Устанавливает проценты для уведомлений."""
    print(f"\n--- Настройка уведомлений для цели '{goal.name}' ---")
    print(f"Текущие проценты: {goal.notification_percentages}")
    
    try:
        percents_input = input("Введите проценты через запятую (например: 25,50,75): ").strip()
        if not percents_input:
            print(AppConfig.MSG_CANCEL)
            return
        
        percentages = []
        for p in percents_input.split(","):
            p_clean = p.strip()
            if p_clean:
                try:
                    percent = int(p_clean)
                    if 1 <= percent < 100:
                        percentages.append(percent)
                    else:
                        print(f"⚠️ Значение {percent} вне диапазона 1-99, пропущено.")
                except ValueError:
                    print(f"⚠️ '{p_clean}' не является числом, пропущено.")
        
        if percentages:
            goal.notification_percentages = sorted(set(percentages))
            print(f"✓ Уведомления настроены для: {goal.notification_percentages}%")
        else:
            print("❌ Некорректные проценты. Должны быть числами от 1 до 99.")
    
    except Exception as e:
        print(f"Ошибка: {e}")
