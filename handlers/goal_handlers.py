"""Обработчики операций с целями"""

from typing import List
from models.goal import Goal
from ui.input_handlers import select_goal, get_positive_float, get_deadline_if_valid
from utils.constants import AppConfig
from utils.decorators import handle_input_errors


@handle_input_errors
def add_goal(goals: List[Goal]) -> None:
    """Добавляет новую цель."""
    print("\n--- Добавление новой цели ---")
    
    name = input("Название цели: ").strip()
    if not name:
        print("Ошибка: название цели не может быть пустым.")
        return
    
    target_amount = get_positive_float("Итоговая сумма (руб.): ")
    if target_amount is None:
        return
    
    category = input("Категория (опционально): ").strip()
    deadline = get_deadline_if_valid()
    
    goal = Goal(name=name, target_amount=target_amount, 
                category=category, deadline=deadline)
    goals.append(goal)
    
    print(f"✓ Цель «{goal.name}» добавлена!")
    print(f"  Текущий баланс: {goal.current_balance:.2f} руб. из {goal.target_amount:.2f} руб.")


def remove_goal(goals: List[Goal]) -> None:
    """Удаляет цель из списка."""
    if not goals:
        print("Нет сохранённых целей.")
        return
    
    print("\n--- Удаление цели ---")
    goal = select_goal(goals, "Выберите цель для удаления")
    if not goal:
        print(AppConfig.MSG_CANCEL)
        return
    
    confirm = input(f"Вы уверены, что хотите удалить цель '{goal.name}'? (д/н): ").strip().lower()
    if confirm in ('д', 'да', 'yes', 'y'):
        goals.remove(goal)
        print(f"✓ Цель '{goal.name}' удалена.")
    else:
        print("Удаление отменено.")


def change_balance(goals: List[Goal]) -> None:
    """Изменяет баланс выбранной цели."""
    if not goals:
        print("Нет сохранённых целей. Сначала добавьте цель.")
        return
    
    print("\n--- Изменение баланса цели ---")
    goal = select_goal(goals, "Выберите цель для изменения баланса")
    if not goal:
        print(AppConfig.MSG_CANCEL)
        return
    
    # Показываем информацию
    print(f"\nВыбрана цель: {goal.name}")
    print(f"Баланс: {goal.current_balance:.2f}/{goal.target_amount:.2f} руб.")
    print(f"Статус: {goal.status}")
    print(f"Прогресс: {goal.get_progress_percentage():.1f}%")
    
    # Выбираем действие
    print("\nДействие:")
    print(f"{AppConfig.ACTION_DEPOSIT}. Пополнить")
    print(f"{AppConfig.ACTION_WITHDRAW}. Снять")
    print("0. Отмена")
    
    action = input("Выберите действие: ").strip()
    
    if action == "0":
        print(AppConfig.MSG_CANCEL)
        return
    
    if action not in (AppConfig.ACTION_DEPOSIT, AppConfig.ACTION_WITHDRAW):
        print("Неверный выбор действия.")
        return
    
    amount = get_positive_float("Сумма (руб.): ")
    if amount is None:
        return
    
    try:
        if action == AppConfig.ACTION_DEPOSIT:
            goal.add_funds(amount)
            print(f"\n✓ Пополнено на {amount:.2f} руб.")
        else:
            goal.withdraw_funds(amount)
            print(f"\n✓ Снято {amount:.2f} руб.")
        print(f"  Новый баланс: {goal.current_balance:.2f} руб.")
    except ValueError as e:
        print(f"\n❌ Ошибка: {e}")