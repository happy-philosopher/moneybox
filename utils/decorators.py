"""Декораторы для обработки ошибок"""

from functools import wraps
from typing import Callable, Any


def handle_input_errors(func: Callable) -> Callable:
    """Декоратор для обработки ошибок ввода"""
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            print(f"❌ Ошибка ввода: {e}")
        except KeyboardInterrupt:
            print("\n⚠️ Операция отменена пользователем.")
        except Exception as e:
            print(f"❌ Неожиданная ошибка: {e}")
        return None
    return wrapper
