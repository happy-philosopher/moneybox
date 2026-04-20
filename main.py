"""Главный модуль приложения"""

from storage.file_storage import load_goals, save_goals
from handlers.goal_handlers import add_goal, remove_goal, change_balance
from handlers.view_handlers import show_goal_details, show_total_progress
from handlers.filter_handlers import filter_goals_by_category, configure_notifications
from utils.constants import AppConfig


def main():
    """Основная функция приложения."""
    goals = load_goals()
    
    print("=" * 50)
    print("ДЕНЕЖНАЯ КОПИЛКА".center(50))
    print("Управление накоплениями".center(50))
    print("=" * 50)
    
    actions = {
        "1": add_goal,
        "2": change_balance,
        "3": remove_goal,
        "4": show_total_progress,
        "5": show_goal_details,
        "6": filter_goals_by_category,
        "7": configure_notifications,
    }
    
    while True:
        print("\n" + "-" * 50)
        print("ГЛАВНОЕ МЕНЮ")
        print("-" * 50)
        
        for key, description in AppConfig.MENU_ITEMS.items():
            print(f"{key}. {description}")
        
        print("-" * 50)
        choice = input("Ваш выбор: ").strip()
        
        if choice == "0":
            print("\n👋 До свидания! Спасибо за использование программы.")
            break
        
        if choice in actions:
            actions[choice](goals)
            if choice in ("1", "2", "3", "7"):
                save_goals(goals)
        else:
            print(f"❌ Ошибка: '{choice}' - неверный выбор. Пожалуйста, выберите 0-7.")


if __name__ == "__main__":
    main()