# Приложение "Денежная копилка", версия 1.0
# Кодер: Михаил Качаргин

import json
import os
from datetime import datetime, timedelta


class Goal:
    """Класс, описывающий цель накопления."""

    def __init__(self, name, target_amount, category=None, deadline=None):
        """
        Инициализация цели.
        :param name: Название цели (строка)
        :param target_amount: итоговая сумма (float или int)
        :param category: категория (строка, опционально)
        :param deadline: дата завершения (строка в формате DD-MM-YYYY, опционально)
        """
        if not name or not name.strip():
            raise ValueError("Название цели не может быть пустым.")
        if target_amount <= 0:
            raise ValueError("Итоговая сумма должна быть больше нуля.")
        self.name = name.strip()
        self.target_amount = float(target_amount)
        self.current_balance = 0.0
        self.category = category.strip() if category else "Без категории"
        self.status = "Активна"
        self.created_at = datetime.now().isoformat()
        self.deadline = deadline
        self.history = []
        self.notification_percentages = [25, 50, 75]  # Проценты для уведомлений

    def to_dict(self):
        """Преобразует объект в словарь для сохранения в JSON."""
        return {
            "name": self.name,
            "target_amount": self.target_amount,
            "current_balance": self.current_balance,
            "category": self.category,
            "status": self.status,
            "created_at": self.created_at,
            "deadline": self.deadline,
            "history": self.history,
            "notification_percentages": self.notification_percentages
        }

    @classmethod
    def from_dict(cls, data):
        """Создаёт объект Goal из словаря."""
        goal = cls(
            name=data["name"],
            target_amount=data["target_amount"],
            category=data["category"],
            deadline=data.get("deadline")
        )
        goal.current_balance = data["current_balance"]
        goal.status = data["status"]
        goal.created_at = data["created_at"]
        goal.history = data.get("history", [])
        goal.notification_percentages = data.get("notification_percentages", [25, 50, 75])
        return goal

    def add_funds(self, amount):
        """Пополняет баланс. Проверяет, чтобы не превысить целевую сумму."""
        if amount <= 0:
            raise ValueError("Сумма пополнения должна быть положительной.")
        if self.current_balance + amount > self.target_amount:
            excess = (self.current_balance + amount) - self.target_amount
            raise ValueError(f"Нельзя превысить целевую сумму. Избыток: {excess:.2f} руб.")
        old_balance = self.current_balance
        self.current_balance += amount
        self._log_transaction("Пополнение", amount)
        # Проверяем достижение цели
        if self.current_balance >= self.target_amount:
            self.status = "Достигнута"
            print(f"🎉 Поздравляем! Цель «{self.name}» достигнута!")
        # Проверяем уведомления о прогрессе
        self._check_progress_notifications(old_balance)

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

    def get_progress_percentage(self):
        """Возвращает процент выполнения цели."""
        if self.target_amount == 0:
            return 0
        return min((self.current_balance / self.target_amount) * 100, 100)

    def _check_progress_notifications(self, old_balance):
        """Проверяет, нужно ли отправить уведомление о прогрессе."""
        old_percentage = (old_balance / self.target_amount) * 100 if self.target_amount > 0 else 0
        new_percentage = self.get_progress_percentage()
        for threshold in sorted(self.notification_percentages):
            if old_percentage < threshold <= new_percentage:
                print(f"🔔 Уведомление: Цель '{self.name}' достигла {threshold}% выполнения!")

    def set_deadline(self, deadline_str):
        """Устанавливает дату завершения цели."""
        try:
            datetime.strptime(deadline_str, "%d-%m-%Y")
            self.deadline = deadline_str
        except ValueError:
            raise ValueError("Дата должна быть в формате ДД-ММ-ГГГГ")

    def get_estimated_completion_date(self):
        """Вычисляет предполагаемую дату завершения на основе истории пополнений."""
        if len(self.history) < 2:
            return None
        # Берём последние 3 пополнения для расчёта среднего темпа
        recent_transactions = [t for t in self.history if t["operation"] == "Пополнение"][-3:]
        if len(recent_transactions) < 2:
            return None
        # Рассчитываем средний темп пополнения
        total_amount = sum(t["amount"] for t in recent_transactions)
        first_date = datetime.fromisoformat(recent_transactions[0]["timestamp"])
        last_date = datetime.fromisoformat(recent_transactions[-1]["timestamp"])
        days_diff = (last_date - first_date).days
        if days_diff == 0:
            return None
        average_daily_amount = total_amount / days_diff
        remaining_amount = self.target_amount - self.current_balance
        if average_daily_amount <= 0 or remaining_amount <= 0:
            return None
        days_needed = remaining_amount / average_daily_amount
        estimated_date = datetime.now() + timedelta(days=days_needed)
        return estimated_date.strftime("%d-%m-%Y")

    def check_deadline_alert(self):
        """Проверяет, приближается ли срок завершения."""
        if not self.deadline or self.status == "Достигнута":
            return
        deadline_date = datetime.strptime(self.deadline, "%d-%m-%Y")
        today = datetime.now().date()
        days_left = (deadline_date.date() - today).days
        if 0 < days_left <= 7:
            progress = self.get_progress_percentage()
            if progress < 80:
                print(f"⚠️ Внимание: До срока завершения цели «{self.name} осталось {days_left} дней, а выполнено только {progress:.1f}%!")


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


def display_goals_list(goals):
    """Выводит список всех целей с номерами."""
    if not goals:
        print("Нет сохранённых целей.")
        return False
    print("\nСписок целей:")
    print("-" * 80)
    for i, goal in enumerate(goals, start=1):
        progress = goal.get_progress_percentage()
        print(f"{i}. {goal.name}")
        print(f"   Сумма: {goal.current_balance:.2f} / {goal.target_amount:.2f} руб.")
        # print(f"   Прогресс: {progress:.1f}%")
        # print(f"   Категория: {goal.category}")
        # print(f"   Статус: {goal.status}")
        # Показываем дату завершения, если установлена
        if goal.deadline:
            print(f"   Дата завершения: {goal.deadline}")
            # Проверяем напоминание о дедлайне
            goal.check_deadline_alert()
        # Показываем предполагаемую дату завершения
        estimated_date = goal.get_estimated_completion_date()
        if estimated_date:
            print(f"   Ожидаемая дата завершения: {estimated_date}")
        print("-" * 80)
    return True


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
        # Добавляем возможность установить дату завершения
        deadline = input("Дата завершения (ДД-ММ-ГГГГ, опционально): ").strip()
        if deadline:
            try:
                datetime.strptime(deadline, "%d-%m-%Y")
            except ValueError:
                print("Неверный формат даты. Дата не будет установлена.")
                deadline = None
        goal = Goal(name=name, target_amount=target_amount, category=category, deadline=deadline)
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
    # Выводим все цели с номерами
    if not display_goals_list(goals):
        return
    # Выбираем цель по номеру
    while True:
        try:
            choice = input("\nВыберите номер цели (0 — отмена): ").strip()
            if choice == "0":
                print("Действие отменено.")
                return
            index = int(choice) - 1
            if 0 <= index < len(goals):
                goal = goals[index]
                break
            else:
                print(f"Ошибка: введите число от 1 до {len(goals)} или 0 для отмены.")
        except ValueError:
            print("Ошибка: введите корректное число.")
    # Показываем информацию о выбранной цели
    print(f"\nВыбрана цель: {goal.name}")
    print(f"Баланс: {goal.current_balance:.2f}/{goal.target_amount:.2f} руб. Статус: {goal.status}")
    print(f"Прогресс: {goal.get_progress_percentage():.1f}%")
    # Выбираем действие
    while True:
        action = input("\nДействие (1 — пополнить, 2 — снять, 0 — отмена): ").strip()
        if action == "0":
            print("Действие отменено.")
            return
        if action in ("1", "2"):
            break
        print("Введите 1, 2 или 0.")
    # Вводим сумму
    while True:
        try:
            amount = float(input("Сумма (руб.): "))
            if amount <= 0:
                print("Сумма должна быть положительной.")
                continue
            break
        except ValueError:
            print("Введите число.")
    # Выполняем операцию
    try:
        if action == "1":
            goal.add_funds(amount)
            print(f"\nПополнено на {amount:.2f} руб. Новый баланс: {goal.current_balance:.2f} руб.")
            if goal.status == "Достигнута":
                print("Поздравляем! Цель достигнута!")
        else:
            goal.withdraw_funds(amount)
            print(f"\nСнято {amount:.2f} руб. Новый баланс: {goal.current_balance:.2f} руб.")
    except ValueError as e:
        print(f"\nОшибка: {e}")


def remove_goal(goals):
    """Удаляет цель из списка."""
    if not goals:
        print("Нет сохранённых целей.")
        return
    print("\n--- Удаление цели ---")
    if not display_goals_list(goals):
        return
    while True:
        try:
            choice = input("\nВыберите номер цели для удаления (0 — отмена): ").strip()
            if choice == "0":
                print("Действие отменено.")
                return
            index = int(choice) - 1
            if 0 <= index < len(goals):
                removed_goal = goals.pop(index)
                print(f"Цель '{removed_goal.name}' удалена.")
                break
            else:
                print(f"Ошибка: введите число от 1 до {len(goals)} или 0 для отмены.")
        except ValueError:
            print("Ошибка: введите корректное число.")


def show_total_progress(goals):
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
    active_goals = [g for g in goals if g.status == "Активна"]
    completed_goals = len(goals) - len(active_goals)
    print("\n--- Общий прогресс ---")
    print(f"Всего целей: {len(goals)}")
    print(f"Выполнено целей: {completed_goals}")
    print(f"Активных целей: {len(active_goals)}")
    print(f"Общая сумма накоплений: {total_current:.2f} руб. из {total_target:.2f} руб.")
    print(f"Общий прогресс: {overall_progress:.1f}%")
    print("- " * 30)


def set_notification_percentages(goal):
    """Устанавливает проценты для уведомлений о прогрессе."""
    print(f"\n--- Настройка уведомлений для цели '{goal.name}' ---")
    print("Текущие проценты для уведомлений:", goal.notification_percentages)
    try:
        percents_input = input("Введите проценты через запятую (например: 25,50,75): ").strip()
        if not percents_input:
            print("Настройка отменена.")
            return
        # Разбираем ввод и преобразуем в числа
        percentages = [int(p.strip()) for p in percents_input.split(",")]
        # Фильтруем некорректные значения: должны быть в диапазоне 1–99%
        valid_percentages = [p for p in percentages if 1 <= p < 100]
        if valid_percentages:
            goal.notification_percentages = sorted(valid_percentages)
            print(f"Уведомления настроены для: {goal.notification_percentages}%")
        else:
            print("Некорректные проценты. Должны быть числами от 1 до 99.")
    except ValueError:
        print("Ошибка: введите целые числа через запятую (например: 25,50,75)")
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")


def show_goal_details(goals):
    """Показывает подробную информацию по выбранной цели."""
    if not goals:
        print("Нет сохранённых целей.")
        return
    print("\n--- Подробная информация о цели ---")
    if not display_goals_list(goals):
        return
    while True:
        try:
            choice = input("\nВыберите номер цели для просмотра деталей (0 — отмена): ").strip()
            if choice == "0":
                print("Действие отменено.")
                return
            index = int(choice) - 1
            if 0 <= index < len(goals):
                goal = goals[index]
                break
            else:
                print(f"Ошибка: введите число от 1 до {len(goals)} или 0 для отмены.")
        except ValueError:
            print("Ошибка: введите корректное число.")
    progress = goal.get_progress_percentage()
    print(f"\n=== Детали цели: {goal.name} ===")
    print(f"Итоговая сумма: {goal.target_amount:.2f} руб.")
    print(f"Текущий баланс: {goal.current_balance:.2f} руб.")
    print(f"Прогресс: {progress:.1f}%")
    print(f"Категория: {goal.category}")
    print(f"Статус: {goal.status}")
    if goal.deadline:
        print(f"Дата завершения: {goal.deadline}")
        goal.check_deadline_alert()  # Проверяем напоминание о дедлайне
    estimated_date = goal.get_estimated_completion_date()
    if estimated_date:
        print(f"Ожидаемая дата завершения: {estimated_date}")
    print(f"Проценты для уведомлений: {goal.notification_percentages}%")
    # Показываем историю операций
    if goal.history:
        print("\nИстория операций:")
        for i, record in enumerate(goal.history, start=1):
            timestamp = datetime.fromisoformat(record["timestamp"]).strftime("%d.%m.%Y %H:%M")
            print(f"{i}. {record['operation']}: {record['amount']:.2f} руб. "
                  f"→ Баланс: {record['balance_after']:.2f} руб. ({timestamp})")
    else:
        print("История операций пуста.")
    print("=" * 50)


def filter_goals_by_category(goals):
    """Фильтрует цели по категории."""
    if not goals:
        print("Нет сохранённых целей.")
        return
    print("\n--- Фильтрация по категориям ---")
    # Собираем все уникальные категории
    categories = set(goal.category for goal in goals)
    if not categories:
        print("Категории не найдены.")
        return
    print("Доступные категории:")
    for i, category in enumerate(sorted(categories), start=1):
        print(f"{i}. {category}")
    try:
        choice = input(f"\nВыберите номер категории (1-{len(categories)}): ").strip()
        if choice.isdigit():
            category_list = sorted(categories)
            index = int(choice) - 1
            if 0 <= index < len(category_list):
                selected_category = category_list[index]
            else:
                print("Неверный номер категории.")
                return
        # Фильтруем цели по выбранной категории
        filtered_goals = [goal for goal in goals if goal.category == selected_category]
        if not filtered_goals:
            print(f"Целей в категории '{selected_category}' не найдено.")
            return
        print(f"\nЦели в категории '{selected_category}': ")
        print("-" * 60)
        for goal in filtered_goals:
            progress = goal.get_progress_percentage()
            print(f"- {goal.name}: {goal.current_balance:.2f}/{goal.target_amount:.2f} руб. ({progress:.1f}%)")
    except Exception as e:
        print(f"Ошибка при фильтрации: {e}")


def main():
    """Основная функция приложения."""
    filename = "goals.json"
    goals = load_goals(filename)
    print("Денежная копилка — управление накоплениями")
    print("=" * 50)
    while True:
        print("\nМеню:")
        print("1. Добавить цель")
        print("2. Изменить баланс цели")
        print("3. Удалить цель")
        print("4. Показать общий прогресс")
        print("5. Показать подробную информацию о цели")
        print("6. Фильтровать цели по категории")
        print("7. Настроить уведомления для цели")
        print("0. Выйти")
        choice = input("Выберите действие (0–7): ").strip()
        match choice:
            case "1":
                add_goal(goals)
                save_goals(goals, filename)
            case "2":
                change_balance(goals)
                save_goals(goals, filename)
            case "3":
                remove_goal(goals)
                save_goals(goals, filename)
            case "4":
                show_total_progress(goals)
            case "5":
                show_goal_details(goals)
            case "6":
                filter_goals_by_category(goals)
            case "7":
                if not goals:
                    print("Нет сохранённых целей.")
                    continue
                if not display_goals_list(goals):
                    continue
                while True:
                    try:
                        choice_num = input("\nВыберите номер цели для настройки уведомлений (0 — отмена): ").strip()
                        if choice_num == "0":
                            break
                        index = int(choice_num) - 1
                        if 0 <= index < len(goals):
                            set_notification_percentages(goals[index])
                            save_goals(goals, filename)  # Сохраняем после успешного изменения
                            break  # Выходим из цикла после успешной настройки
                        else:
                            print(f"Неверный номер цели. Введите число от 1 до {len(goals)} или 0 для отмены.")
                    except ValueError:
                        print("Ошибка: введите число.")
            case "0":
                print("До свидания!")
                break
            case _:
                print("Неверный выбор. Попробуйте снова.")


if __name__ == "__main__":
    main()
