
# import mysql.connector
from datetime import datetime
# from typing import List, Optional


class Alert:
    """Клас для представлення окремого сповіщення."""

    def __init__(self, message_time: datetime, alert_type: str, chat_title: str, message_text: str, keywords: str | None = None):
        self.message_time = message_time
        self.alert_type = alert_type
        self.chat_title = chat_title
        self.message_text = message_text
        self.keywords = keywords

    def to_tuple(self) -> tuple:
        """Перетворює об'єкт у кортеж для передачі в MySQL query."""
        return (
            # Для сумісності з DATETIME в MySQL
            self.message_time.replace(tzinfo=None),
            self.alert_type,
            self.chat_title,
            self.message_text,
            self.keywords
        )

    def __repr__(self) -> str:
        time_str = self.message_time.strftime("%H:%M:%S")
        return f"Alert({self.alert_type} | {self.chat_title} | {time_str} | Text: '{self.message_text[:10]}...')"


class AlertSessionManager:
    """Клас для накопичення сповіщень протягом сесії та їх збереження в БД."""

    def __init__(self, db_config: dict | None = None):
        self.db_config = db_config
        # Масив (список) для об'єктів сесії
        self.session_storage: list[Alert] = []

    def add_alert(self, alert: Alert) -> None:
        """Додає об'єкт Alert до поточного масиву сесії."""
        self.session_storage.append(alert)
        print(
            f"📦 Сповіщення додано в сесію. Всього в пам'яті: {len(self.session_storage)}")


# my_alert = Alert(datetime.now(), "DANGER", "Канал 1", "Текст тривоги")
# print(my_alert)
