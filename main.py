# Приложение "Денежная копилка"
# Кодер: Михаил Качаргин


import json
import os
from datetime import datetime


class Goal:
    """Класс, описывающий цель накопления."""
    def __init__(self, name, target_amount, category=None):
        """
        Инициализация цели.
        :param name: Название цели (строка)
        :param target_amount: итоговая сумма (float или int)
        :param category: категория (строка, опционально)
        """
        if not name or not name.strip():
            raise ValueError("Название цели не может быть пустым.")
        if target_amount <= 0:
            raise ValueError("Итоговая сумма должна быть больше нуля.")
        self.name = name.strip()
        self.target_amount = float(target_amount)
        self.current_balance = 0.0
        self.category = category.strip() if category else "Без категории"
        self.status = "Активна"  # Возможные: "Активна", "Достигнута", "Отменена"
        self.created_at = datetime.now().isoformat()
        self.history = []  # История изменений баланса

    def to_dict(self):
        """Преобразует объект в словарь для сохранения в JSON."""
        return {
            "name": self.name,
            "target_amount": self.target_amount,
            "current_balance": self.current_balance,
            "category": self.category,
            "status": self.status,
            "created_at": self.created_at,
            "history": self.history
        }

    @classmethod
    def from_dict(cls, data):
        """Создаёт объект Goal из словаря."""
        goal = cls(
            name=data["name"],
            target_amount=data["target_amount"],
            category=data["category"]
        )
        goal.current_balance = data["current_balance"]
        goal.status = data["status"]
        goal.created_at = data["created_at"]
        goal.history = data.get("history", [])
        return goal

    def add_funds(self, amount):
        """Пополняет баланс. Проверяет, чтобы не превысить целевую сумму."""
        if amount <= 0:
            raise ValueError("Сумма пополнения должна быть положительной.")
        if self.current_balance + amount > self.target_amount:
            excess = (self.current_balance + amount) - self.target_amount
            raise ValueError(f"Нельзя превысить целевую сумму. Избыток: {excess:.2f} руб.")
        self.current_balance += amount
        self._log_transaction("Пополнение", amount)
        # Обновляем статус, если цель достигнута
        if self.current_balance >= self.target_amount:
            self.status = "Достигнута"

    def withdraw_funds(self, amount):
        """Снимает средства с баланса. Проверяет, чтобы не уйти в минус."""
        if amount <= 0:
            raise ValueError("Сумма снятия должна быть положительной.")
        if self.current_balance - amount < 0:
            raise ValueError("Недостаточно средств на балансе.")
        self.current_balance -= amount
        self._log_transaction("Снятие", amount)

    def _log_transaction(self, operation, amount):
        """Добавляет запись в историю изменений."""
        self.history.append({
            "operation": operation,
            "amount": amount,
            "balance_after": self.current_balance,
            "timestamp": datetime.now().isoformat()
        })


def load_goals(filename="goals.json"):
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


def save_goals(goals, filename="goals.json"):
    """Сохраняет цели в JSON-файл."""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump([goal.to_dict() for goal in goals], f, ensure_ascii=False, indent=4)
    except IOError as e:
        print(f"Ошибка при записи в файл {filename}: {e}")


def find_goal_by_name(goals, name):
    """Находит цель по названию (точное совпадение)."""
    for goal in goals:
        if goal.name.lower() == name.lower():
            return goal
    return None


def add_goal(goals):
    """Добавляет новую цель."""
    print("\n--- Добавление новой цели ---")
    try:
        name = input("Название цели: ").strip()
        if not name:
            print("Ошибка: название цели не может быть пустым.")
            return
        while True:
            try:
                target_amount = float(input("Итоговая сумма (руб.): "))
                if target_amount <= 0:
                    print("Сумма должна быть больше нуля.")
                    continue
                break
            except ValueError:
                print("Пожалуйста, введите число.")
        category = input("Категория (опционально): ").strip()
        goal = Goal(name=name, target_amount=target_amount, category=category)
        goals.append(goal)
        print(f"Цель «{goal.name}» добавлена!")
        print(f"Текущий баланс: {goal.current_balance:.2f} руб. из {goal.target_amount:.2f} руб.")
    except ValueError as e:
        print(f"Ошибка: {e}")
    except KeyboardInterrupt:
        print("\nОперация отменена пользователем.")


def change_balance(goals):
    """Изменяет баланс выбранной цели (пополнение или снятие)."""
    if not goals:
        print("Нет сохранённых целей. Сначала добавьте цель.")
        return
    print("\n--- Изменение баланса цели ---")
    name = input("Введите название цели: ").strip()
    goal = find_goal_by_name(goals, name)
    if not goal:
        print("Цель не найдена.")
        return
    print(f"Баланс: {goal.current_balance:.2f}/{goal.target_amount:.2f} руб. Статус: {goal.status}")
    while True:
        action = input("Действие (1 — пополнить, 2 — снять, 0 — отмена): ").strip()
        if action == "0":
            print("Действие отменено.")
            return
        if action in ("1", "2"):
            break
        print("Введите 1, 2 или 0.")
    while True:
        try:
            amount = float(input("Сумма (руб.): "))
            if amount <= 0:
                print("Сумма должна быть положительной.")
                continue
            break
        except ValueError:
            print("Введите число.")
    try:
        if action == "1":
            goal.add_funds(amount)
            print(f"Пополнено на {amount:.2f} руб. Новый баланс: {goal.current_balance:.2f} руб.")
            if goal.status == "Достигнута":
                print("Цель достигнута!")
        else:
            goal.withdraw_funds(amount)
            print(f"Снято {amount:.2f} руб. Новый баланс: {goal.current_balance:.2f} руб.")
    except ValueError as e:
        print(f"Ошибка: {e}")


def main():
    """Основная функция приложения."""
    filename = "goals.json"
    goals = load_goals(filename)
    print("Денежная копилка — управление накоплениями")
    print("=" * 42)
    while True:
        print("\nМеню:")
        print("1. Добавить цель")
        print("2. Изменить баланс цели")
        print("3. Выйти")
        choice = input("Выберите действие (1–3): ").strip()
        if choice == "1":
            add_goal(goals)
            save_goals(goals, filename)  # Сохраняем после каждого добавления
        elif choice == "2":
            change_balance(goals)
            save_goals(goals, filename)
        elif choice == "3":
            print("До свидания!")
            break
        else:
            print("Неверный выбор. Попробуйте снова.")


if __name__ == "__main__":
    main()
