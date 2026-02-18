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

    def to_dict(self):
        """Преобразует объект в словарь для сохранения в JSON."""
        return {
            "name": self.name,
            "target_amount": self.target_amount,
            "current_balance": self.current_balance,
            "category": self.category,
            "status": self.status,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data):
        """Создаёт объект Goal из словаря (например, из JSON)."""
        goal = cls(
            name=data["name"],
            target_amount=data["target_amount"],
            category=data["category"]
        )
        goal.current_balance = data["current_balance"]
        goal.status = data["status"]
        goal.created_at = data["created_at"]
        return goal


def load_goals(filename="goals.json"):
    """Загружает цели из JSON‑файла."""
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
    """Сохраняет цели в JSON‑файл."""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump([goal.to_dict() for goal in goals], f, ensure_ascii=False, indent=4)
    except IOError as e:
        print(f"Ошибка при записи в файл {filename}: {e}")


def add_goal(goals):
    """Добавляет новую цель через консольный ввод."""
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

        # Создаём цель
        goal = Goal(name=name, target_amount=target_amount, category=category)
        goals.append(goal)
        print(
            f"Цель «{goal.name}» добавлена!"
            f"Текущий баланс: {goal.current_balance:.2f} руб. из {goal.target_amount:.2f} руб.")

    except ValueError as e:
        print(f"Ошибка: {e}")
    except KeyboardInterrupt:
        print("\nОперация отменена пользователем.")


def main():
    """Основная функция приложения."""
    filename = "goals.json"
    goals = load_goals(filename)

    print("Денежная копилка — управление накоплениями")
    print("=" * 40)

    while True:
        print("\nМеню:")
        print("1. Добавить цель")
        print("2. Выйти")

        choice = input("Выберите действие (1-2): ").strip()

        if choice == "1":
            add_goal(goals)
            save_goals(goals, filename)  # Сохраняем после каждого добавления
        elif choice == "2":
            print("До свидания!")
            break
        else:
            print("Неверный выбор. Попробуйте снова.")


if __name__ == "__main__":
    main()
