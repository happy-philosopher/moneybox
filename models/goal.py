"""Модель данных для цели накопления"""

from datetime import datetime, timedelta
from utils.constants import AppConfig


class Goal:
    """Класс, описывающий цель накопления."""
    
    def __init__(self, name, target_amount, category=None, deadline=None):
        """Инициализация цели."""
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
        """Преобразует объект в словарь для сохранения."""
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
        """Пополняет баланс."""
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
        """Снимает средства."""
        if amount <= 0:
            raise ValueError("Сумма снятия должна быть положительной.")
        if self.current_balance - amount < 0:
            raise ValueError("Недостаточно средств на балансе.")
        
        self.current_balance -= amount
        self._log_transaction(AppConfig.OPERATION_WITHDRAW, amount)
    
    def _log_transaction(self, operation, amount):
        """Добавляет запись в историю."""
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
        """Проверяет необходимость уведомления о прогрессе."""
        old_percentage = (old_balance / self.target_amount) * 100 if self.target_amount > 0 else 0
        new_percentage = self.get_progress_percentage()
        
        for threshold in sorted(self.notification_percentages):
            if old_percentage < threshold <= new_percentage:
                print(AppConfig.MSG_PROGRESS_NOTIFICATION.format(
                    name=self.name, threshold=threshold
                ))
    
    def set_deadline(self, deadline_str):
        """Устанавливает дату завершения."""
        try:
            datetime.strptime(deadline_str, AppConfig.DATE_FORMAT)
            self.deadline = deadline_str
        except ValueError:
            raise ValueError(f"Дата должна быть в формате {AppConfig.DATE_FORMAT}")
    
    def get_estimated_completion_date(self):
        """Вычисляет предполагаемую дату завершения."""
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
        """Проверяет приближение срока."""
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