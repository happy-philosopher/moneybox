"""Обработчики просмотра информации"""

from typing import List
from datetime import datetime
from models.goal import Goal
from ui.input_handlers import select_goal
from ui.display import show_progress_bar
from utils.constants import AppConfig


def show_goal_details(goals: List[Goal]) -> None:
    """Показывает подробную информацию по выбранной цели."""
    if not goals:
        print("Нет сохранённых целей.")
        return
    
    print("\n--- Подробная информация о цели ---")
    goal = select_goal(goals, "Выберите цель для просмотра деталей")
    if not goal:
        print(AppConfig.MSG_CANCEL)
        return
    
    progress = goal.get_progress_percentage()
    progress_bar = show_progress_bar(progress)
    
    print(f"\n{'='*50}")
    print(f"ЦЕЛЬ: {goal.name}")
    print(f"{'='*50}")
    print(f"📊 Итоговая сумма:  {goal.target_amount:.2f} руб.")
    print(f"💰 Текущий баланс:  {goal.current_balance:.2f} руб.")
    print(f"📈 Прогресс:        {progress:.1f}% {progress_bar}")
    print(f"🏷️ Категория:       {goal.category}")
    print(f"📌 Статус:          {goal.status}")
    
    if goal.deadline:
        print(f"⏰ Дата завершения: {goal.deadline}")
        goal.check_deadline_alert()
    
    estimated_date = goal.get_estimated_completion_date()
    if estimated_date:
        print(f"🔮 Ожидаемая дата:  {estimated_date}")
    
    print(f"🔔 Уведомления:     {goal.notification_percentages}%")
    
    # История операций
    if goal.history:
        print(f"\n📜 ИСТОРИЯ ОПЕРАЦИЙ:")
        print("-" * 50)
        for i, record in enumerate(goal.history, start=1):
            timestamp = datetime.fromisoformat(record["timestamp"]).strftime("%d.%m.%Y %H:%M")
            operation_symbol = "➕" if record["operation"] == AppConfig.OPERATION_DEPOSIT else "➖"
            print(f"{i:2}. {operation_symbol} {record['operation']}: {record['amount']:8.2f} руб. "
                  f"→ Баланс: {record['balance_after']:8.2f} руб. ({timestamp})")
    else:
        print("\n📜 История операций пуста.")
    
    print(f"{'='*50}")


def show_total_progress(goals: List[Goal]) -> None:
    """Показывает общий прогресс по всем целям."""
    if not goals:
        print("Нет сохранённых целей.")
        return
    
    total_target = sum(goal.target_amount for goal in goals)
    total_current = sum(goal.current_balance for goal in goals)
    
    if total_target == 0:
        overall_progress = 0
    else:
        overall_progress = (total_current / total_target) * 100
    
    active_goals = [g for g in goals if g.status == AppConfig.ACTIVE_STATUS]
    completed_goals = [g for g in goals if g.status == AppConfig.ACHIEVED_STATUS]
    
    print("\n" + "=" * 50)
    print("ОБЩИЙ ПРОГРЕСС".center(50))
    print("=" * 50)
    print(f"📊 Всего целей:      {len(goals)}")
    print(f"✅ Выполнено:        {len(completed_goals)}")
    print(f"⏳  Активных:         {len(active_goals)}")
    print("-" * 50)
    print(f"💰 Накоплено:        {total_current:10.2f} руб.")
    print(f"🎯 Целевая сумма:    {total_target:10.2f} руб.")
    print(f"📈 Общий прогресс:   {overall_progress:6.1f}%")
    
    # Визуальный прогресс-бар
    if total_target > 0:
        bar = show_progress_bar(overall_progress, 30)
        print(f"[{bar}]")
    
    print("=" * 50)
    
    # Разбивка по категориям
    if goals:
        categories = {}
        for goal in goals:
            if goal.category not in categories:
                categories[goal.category] = {"target": 0, "current": 0, "count": 0}
            categories[goal.category]["target"] += goal.target_amount
            categories[goal.category]["current"] += goal.current_balance
            categories[goal.category]["count"] += 1
        
        if len(categories) > 1:
            print("\n📊 РАЗБИВКА ПО КАТЕГОРИЯМ:")
            print("-" * 50)
            for category, data in sorted(categories.items()):
                if data["target"] > 0:
                    cat_progress = (data["current"] / data["target"]) * 100
                    cat_bar = show_progress_bar(cat_progress, 20)
                    print(f"{category:15} | {data['current']:8.2f}/{data['target']:8.2f} руб. "
                          f"({cat_progress:5.1f}%) {cat_bar}")