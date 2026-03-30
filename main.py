# Приложение "Денежная копилка", версия 1.1.0
# Кодер: Михаил Качаргин


import json
import os
from datetime import datetime, timedelta


# Константы приложения
class AppConfig:
    """Конфигурация приложения"""
    DATA_FILE = "goals.json"
    DATE_FORMAT = "%d-%m-%Y"
    DEFAULT_CATEGORY = "Без категории"
    ACTIVE_STATUS = "Активна"
    ACHIEVED_STATUS = "Достигнута"
    DEFAULT_NOTIFICATION_PERCENTAGES = [25, 50, 75]
    DEADLINE_ALERT_DAYS = 7
    DEADLINE_ALERT_THRESHOLD = 80  # процент выполнения для предупреждения
    RECENT_TRANSACTIONS_LIMIT = 3
    PROGRESS_BAR_LENGTH = 20

    # Сообщения
    MSG_CANCEL = "Действие отменено."
    MSG_GOAL_ACHIEVED = "🎉 Поздравляем! Цель «{name}» достигнута!"
    MSG_DEADLINE_ALERT = "⚠️ Внимание: До срока завершения цели «{name}» осталось {days} дней, а выполнено только {progress:.1f}%!"
    MSG_PROGRESS_NOTIFICATION = "🔔 Уведомление: Цель '{name}' достигла {threshold}% выполнения!"

    # Меню
    MENU_ITEMS = {
        "1": "Добавить цель",
        "2": "Изменить баланс цели",
        "3": "Удалить цель",
        "4": "Показать общий прогресс",
        "5": "Показать подробную информацию о цели",
        "6": "Фильтровать цели по категории",
        "7": "Настроить уведомления для цели",
        "0": "Выйти"
    }

    # Действия с балансом
    ACTION_DEPOSIT = "1"
    ACTION_WITHDRAW = "2"
    OPERATION_DEPOSIT = "Пополнение"
    OPERATION_WITHDRAW = "Снятие"

    # Остальные константы
    VERBOSE_MODE = False  # Режим подробного вывода списка целей


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
        self.category = category.strip() if category else AppConfig.DEFAULT_CATEGORY
        self.status = AppConfig.ACTIVE_STATUS
        self.created_at = datetime.now().isoformat()
        self.deadline = deadline
        self.history = []
        self.notification_percentages = AppConfig.DEFAULT_NOTIFICATION_PERCENTAGES.copy()

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
        goal.notification_percentages = data.get(
            "notification_percentages",
            AppConfig.DEFAULT_NOTIFICATION_PERCENTAGES.copy()
        )
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
        self._log_transaction(AppConfig.OPERATION_DEPOSIT, amount)

        if self.current_balance >= self.target_amount:
            self.status = AppConfig.ACHIEVED_STATUS
            print(AppConfig.MSG_GOAL_ACHIEVED.format(name=self.name))

        self._check_progress_notifications(old_balance)

    def withdraw_funds(self, amount):
        """Снимает средства с баланса. Проверяет, чтобы не уйти в минус."""
        if amount <= 0:
            raise ValueError("Сумма снятия должна быть положительной.")
        if self.current_balance - amount < 0:
            raise ValueError("Недостаточно средств на балансе.")

        self.current_balance -= amount
        self._log_transaction(AppConfig.OPERATION_WITHDRAW, amount)

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
                print(AppConfig.MSG_PROGRESS_NOTIFICATION.format(
                    name=self.name, threshold=threshold
                ))

    def set_deadline(self, deadline_str):
        """Устанавливает дату завершения цели."""
        try:
            datetime.strptime(deadline_str, AppConfig.DATE_FORMAT)
            self.deadline = deadline_str
        except ValueError:
            raise ValueError(f"Дата должна быть в формате {AppConfig.DATE_FORMAT}")

    def get_estimated_completion_date(self):
        """Вычисляет предполагаемую дату завершения на основе истории пополнений."""
        if len(self.history) < 2:
            return None

        recent_transactions = [
            t for t in self.history
            if t["operation"] == AppConfig.OPERATION_DEPOSIT
        ][-AppConfig.RECENT_TRANSACTIONS_LIMIT:]

        if len(recent_transactions) < 2:
            return None

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
        return estimated_date.strftime(AppConfig.DATE_FORMAT)

    def check_deadline_alert(self):
        """Проверяет, приближается ли срок завершения."""
        if not self.deadline or self.status == AppConfig.ACHIEVED_STATUS:
            return

        deadline_date = datetime.strptime(self.deadline, AppConfig.DATE_FORMAT)
        days_left = (deadline_date.date() - datetime.now().date()).days

        if 0 < days_left <= AppConfig.DEADLINE_ALERT_DAYS:
            progress = self.get_progress_percentage()
            if progress < AppConfig.DEADLINE_ALERT_THRESHOLD:
                print(AppConfig.MSG_DEADLINE_ALERT.format(
                    name=self.name, days=days_left, progress=progress
                ))


def load_goals(filename=AppConfig.DATA_FILE):
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


def save_goals(goals, filename=AppConfig.DATA_FILE):
    """Сохраняет цели в JSON-файл."""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump([goal.to_dict() for goal in goals], f, ensure_ascii=False, indent=4)
    except IOError as e:
        print(f"Ошибка при записи в файл {filename}: {e}")


def handle_input_errors(func):
    """Декоратор для обработки ошибок ввода"""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            print(f"Ошибка ввода: {e}")
        except KeyboardInterrupt:
            print("\nОперация отменена пользователем.")
        except Exception as e:
            print(f"Неожиданная ошибка: {e}")
        return None

    return wrapper


def select_goal(goals, prompt="Выберите номер цели"):
    """Универсальная функция выбора цели"""
    if not goals:
        print("Нет сохранённых целей.")
        return None

    display_goals_list(goals)

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


def display_goals_list(goals):
    """Выводит список всех целей с номерами."""
    if not goals:
        print("Нет сохранённых целей.")
        return False

    print("\nСписок целей:")
    print("-" * 50)

    for i, goal in enumerate(goals, start=1):
        progress = goal.get_progress_percentage()

        # Основная информация
        print(f"{i}. {goal.name} / категория: {goal.category}")
        print(f"   Сумма: {goal.current_balance:.2f} / {goal.target_amount:.2f} руб.")

        # Дополнительная информация (можно управлять флагом verbose)
        if AppConfig.VERBOSE_MODE:  # Добавьте эту константу
            print(f"   Прогресс: {progress:.1f}%")
            print(f"   Статус: {goal.status}")

            # Дедлайн
            if goal.deadline:
                print(f"   Дата завершения: {goal.deadline}")
                goal.check_deadline_alert()

            # Ожидаемая дата
            estimated_date = goal.get_estimated_completion_date()
            if estimated_date:
                print(f"   Ожидаемая дата завершения: {estimated_date}")

        print("-" * 50)

    return True


@handle_input_errors
def add_goal(goals):
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

    print(f"Цель «{goal.name}» добавлена!")
    print(f"Текущий баланс: {goal.current_balance:.2f} руб. из {goal.target_amount:.2f} руб.")


def get_positive_float(prompt):
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


def get_deadline_if_valid():
    """Вспомогательная функция для ввода даты"""
    deadline = input(f"Дата завершения ({AppConfig.DATE_FORMAT}, опционально): ").strip()
    if deadline:
        try:
            datetime.strptime(deadline, AppConfig.DATE_FORMAT)
            return deadline
        except ValueError:
            print("Неверный формат даты. Дата не будет установлена.")
    return None


def configure_notifications(goals):
    """Настраивает уведомления для выбранной цели."""
    if not goals:
        print("Нет сохранённых целей.")
        return

    goal = select_goal(goals, "Выберите цель для настройки уведомлений")
    if not goal:
        print(AppConfig.MSG_CANCEL)
        return

    set_notification_percentages(goal)


def set_notification_percentages(goal):
    """Устанавливает проценты для уведомлений о прогрессе."""
    print(f"\n--- Настройка уведомлений для цели '{goal.name}' ---")
    print(f"Текущие проценты для уведомлений: {goal.notification_percentages}")

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
                        print(f"Предупреждение: значение {percent} вне диапазона 1-99, пропущено.")
                except ValueError:
                    print(f"Предупреждение: '{p_clean}' не является целым числом, пропущено.")

        if percentages:
            goal.notification_percentages = sorted(set(percentages))  # Убираем дубликаты
            print(f"Уведомления настроены для: {goal.notification_percentages}%")
        else:
            print("Некорректные проценты. Должны быть числами от 1 до 99.")

    except Exception as e:
        print(f"Неожиданная ошибка: {e}")


def show_goal_details(goals):
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

    print(f"\n=== Детали цели: {goal.name} ===")
    print(f"Итоговая сумма: {goal.target_amount:.2f} руб.")
    print(f"Текущий баланс: {goal.current_balance:.2f} руб.")
    print(f"Прогресс: {progress:.1f}%")
    print(f"Категория: {goal.category}")
    print(f"Статус: {goal.status}")

    if goal.deadline:
        print(f"Дата завершения: {goal.deadline}")
        goal.check_deadline_alert()

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
        print("\nИстория операций пуста.")

    print("=" * 80)


def change_balance(goals):
    """Изменяет баланс выбранной цели (пополнение или снятие)."""
    if not goals:
        print("Нет сохранённых целей. Сначала добавьте цель.")
        return

    print("\n--- Изменение баланса цели ---")
    goal = select_goal(goals, "Выберите цель для изменения баланса")
    if not goal:
        print(AppConfig.MSG_CANCEL)
        return

    # Показываем информацию о выбранной цели
    print(f"\nВыбрана цель: {goal.name}")
    print(f"Баланс: {goal.current_balance:.2f}/{goal.target_amount:.2f} руб. Статус: {goal.status}")
    print(f"Прогресс: {goal.get_progress_percentage():.1f}%")

    # Выбираем действие
    action = input(f"\nДействие ({AppConfig.ACTION_DEPOSIT} — пополнить, {AppConfig.ACTION_WITHDRAW} — снять, 0 — отмена): ").strip()

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
            print(f"\nПополнено на {amount:.2f} руб. Новый баланс: {goal.current_balance:.2f} руб.")
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
    goal = select_goal(goals, "Выберите цель для удаления")
    if not goal:
        print(AppConfig.MSG_CANCEL)
        return

    # Подтверждение удаления
    confirm = input(f"Вы уверены, что хотите удалить цель '{goal.name}'? (д/н): ").strip().lower()
    if confirm in ('д', 'да', 'yes', 'y'):
        goals.remove(goal)
        print(f"Цель '{goal.name}' удалена.")
    else:
        print("Удаление отменено.")


def filter_goals_by_category(goals):
    """Фильтрует цели по категории."""
    if not goals:
        print("Нет сохранённых целей.")
        return

    print("\n--- Фильтрация по категориям ---")

    # Собираем все уникальные категории
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

        # Фильтруем цели по выбранной категории
        filtered_goals = [goal for goal in goals if goal.category == selected_category]

        if not filtered_goals:
            print(f"Целей в категории '{selected_category}' не найдено.")
            return

        print(f"\n=== Цели в категории '{selected_category}' ===")
        print("-" * 60)

        total_target = sum(goal.target_amount for goal in filtered_goals)
        total_current = sum(goal.current_balance for goal in filtered_goals)

        for goal in filtered_goals:
            progress = goal.get_progress_percentage()
            status_mark = "✅" if goal.status == AppConfig.ACHIEVED_STATUS else "⏳"
            print(
                f"{status_mark} {goal.name}: {goal.current_balance:.2f}/{goal.target_amount:.2f} руб. ({progress:.1f}%)")

        if total_target > 0:
            overall_progress = (total_current / total_target) * 100
            print("-" * 60)
            print(f"Итого по категории: {total_current:.2f}/{total_target:.2f} руб. ({overall_progress:.1f}%)")

    except Exception as e:
        print(f"Ошибка при фильтрации: {e}")


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

    active_goals = [g for g in goals if g.status == AppConfig.ACTIVE_STATUS]
    completed_goals = [g for g in goals if g.status == AppConfig.ACHIEVED_STATUS]

    print("\n" + "=" * 50)
    print("ОБЩИЙ ПРОГРЕСС")
    print("=" * 50)
    print(f"Всего целей: {len(goals)}")
    print(f"  ✅ Выполнено: {len(completed_goals)}")
    print(f"  ⏳ Активных: {len(active_goals)}")
    print("-" * 50)
    print(f"Общая сумма накоплений: {total_current:.2f} руб.")
    print(f"Целевая сумма: {total_target:.2f} руб.")
    print(f"Общий прогресс: {overall_progress:.1f}%")

    # Визуальный прогресс-бар
    if total_target > 0:
        bar_length = 30
        filled = int(bar_length * overall_progress / 100)
        bar = "█" * filled + "░" * (bar_length - filled)
        print(f"[{bar}] {overall_progress:.1f}%")

    print("=" * 50)

    # Дополнительная информация по категориям
    if goals:
        categories = {}
        for goal in goals:
            if goal.category not in categories:
                categories[goal.category] = {"target": 0, "current": 0, "count": 0}
            categories[goal.category]["target"] += goal.target_amount
            categories[goal.category]["current"] += goal.current_balance
            categories[goal.category]["count"] += 1

        if len(categories) > 1:  # Показываем разбивку по категориям, если их несколько
            print("\nРазбивка по категориям:")
            for category, data in sorted(categories.items()):
                if data["target"] > 0:
                    cat_progress = (data["current"] / data["target"]) * 100
                    print(f"  {category}: {data['current']:.2f}/{data['target']:.2f} руб. ({cat_progress:.1f}%)")


def main():
    """Основная функция приложения."""
    goals = load_goals()

    print("=" * 50)
    print("       ДЕНЕЖНАЯ КОПИЛКА")
    print("    Управление накоплениями")
    print("=" * 50)

    # Словарь действий
    actions = {
        "1": add_goal,                  # Добавить цель
        "2": change_balance,            # Изменить баланс цели
        "3": remove_goal,               # Удалить цель
        "4": show_total_progress,       # Показать общий прогресс
        "5": show_goal_details,         # Показать подробную информацию о цели
        "6": filter_goals_by_category,  # Фильтровать цели по категории
        "7": configure_notifications,   # Настроить уведомления для цели
    }

    while True:
        print("\n" + "-" * 50)
        print("ГЛАВНОЕ МЕНЮ")
        print("-" * 50)

        for key, description in AppConfig.MENU_ITEMS.items():
            print(f"{key}. {description}")

        print("-" * 50)
        choice = input("Ваш выбор: ").strip()

        if choice == "0":               # Выйти
            print("\nДо свидания! Спасибо за использование программы.")
            break

        if choice in actions:
            actions[choice](goals)
            # Сохраняем изменения после действий, которые их вносят
            if choice in ("1", "2", "3", "7"):  # Действия, изменяющие данные
                save_goals(goals)
        else:
            print(f"Ошибка: '{choice}' - неверный выбор. Пожалуйста, выберите 0-7.")



if __name__ == "__main__":
    main()
