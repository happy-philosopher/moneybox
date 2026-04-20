"""Конфигурация и константы приложения"""

class AppConfig:
    """Глобальные настройки приложения"""
    
    # Файлы
    DATA_FILE = "goals.json"
    DATE_FORMAT = "%d-%m-%Y"
    
    # Статусы
    DEFAULT_CATEGORY = "Без категории"
    ACTIVE_STATUS = "Активна"
    ACHIEVED_STATUS = "Достигнута"
    
    # Уведомления
    DEFAULT_NOTIFICATION_PERCENTAGES = [25, 50, 75]
    DEADLINE_ALERT_DAYS = 7
    DEADLINE_ALERT_THRESHOLD = 80
    RECENT_TRANSACTIONS_LIMIT = 3
    
    # UI
    PROGRESS_BAR_LENGTH = 20
    VERBOSE_MODE = True
    
    # Сообщения
    MSG_CANCEL = "Действие отменено."
    MSG_GOAL_ACHIEVED = "🎉 Поздравляем! Цель «{name}» достигнута!"
    MSG_DEADLINE_ALERT = "⚠️ Внимание: До срока завершения цели «{name}» осталось {days} дней, а выполнено только {progress:.1f}%!"
    MSG_PROGRESS_NOTIFICATION = "🔔 Уведомление: Цель '{name}' достигла {threshold}% выполнения!"
    
    # Действия
    ACTION_DEPOSIT = "1"
    ACTION_WITHDRAW = "2"
    OPERATION_DEPOSIT = "Пополнение"
    OPERATION_WITHDRAW = "Снятие"
    
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