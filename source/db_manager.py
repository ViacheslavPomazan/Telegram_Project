
import mysql.connector
from datetime import datetime


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
            self.message_text,
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
        self.d_count: int = 0

    def add_alert(self, alert: Alert) -> None:
        """Додає об'єкт Alert до поточного масиву сесії."""
        self.session_storage.append(alert)
        print(
            f"📦 Сповіщення додано в сесію. Всього в пам'яті: {len(self.session_storage)}")

    def save_session_to_db(self) -> None:
        """Пакетний експорт накопичених даних у MySQL (Batch Insert)."""
        if not self.session_storage:
            print("ℹ️ Сесія порожня. Немає даних для запису в БД.")
            return 0

        # query = """
        #     INSERT INTO alerts (message_time, alert_type, chat_title, message_text, keywords)
        #     VALUES (%s, %s, %s, %s, %s)
        # """

        query = """
            INSERT INTO alerts (
                message_time, 
                alert_id, 
                chat_id, 
                template_id, 
                message__text, 
                keywords
            )
            VALUES (
                %s, 
                %s, 
                DefineChannel(%s), 
                DefineTemplate(%s), 
                IF(DefineTemplate(%s) IS NULL, %s, NULL), 
                %s
            )
        """

        # Перетворюємо список об'єктів Alert на список кортежів для SQL
        data_to_insert = [alert.to_tuple() for alert in self.session_storage]

        try:
            print(
                f"🔄 Починаємо запис {len(data_to_insert)} записів у MySQL...")
            connection = mysql.connector.connect(**self.db_config)
            cursor = connection.cursor()

            # executemany виконує один пакетний запит замість серії окремих
            cursor.executemany(query, data_to_insert)
            connection.commit()

            print(f"✅ Успішно збережено {cursor.rowcount} записів у MySQL!")

            # cursor.close()
            # connection.close()

            # Очищаємо сесійний масив після успішного збереження
            self.session_storage.clear()

        except mysql.connector.Error as err:
            if connection:
                connection.rollback()

            print(f"❌ Помилка при збереженні в MySQL: {err}")
            # Прокід інформує викликаючий код (main) про невдачу
            raise

        finally:
            # Ресурси закриваються ЗАВЖДИ
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()
