# handlers/__init__.py
from handlers.goal_handlers import add_goal, remove_goal, change_balance
from handlers.view_handlers import show_goal_details, show_total_progress
from handlers.filter_handlers import filter_goals_by_category, configure_notifications

__all__ = [
    'add_goal', 'remove_goal', 'change_balance',
    'show_goal_details', 'show_total_progress',
    'filter_goals_by_category', 'configure_notifications'
]