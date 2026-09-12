from telethon import TelegramClient, events
import winsound
# import re
import time
from datetime import datetime, timedelta
from source.loading import save_to_jsonl
from source.search import *
from source.db_manager import Alert, AlertSessionManager


# 1. Дані авторизації (з my.telegram.org)
API_ID = 11111111  # Замініть на ваш цілочисельний API ID
API_HASH = '<your hash>'

# 2. Налаштування відстеження
# Можна вказати @username (рядок) або ID каналу (число int)
TARGET_CHANNEL = '@sumygo'

# Список ключових слів (пишемо в нижньому регістрі для зручності)
KEYWORDS = ['каб', 'сум', 'баліст', 'впал']

# Конфігурація підключення до MySQL
# DB_CONFIG = {
#     "host": "localhost",
#     "user": "root",
#     "password": "your_password",
#     "database": "telegram_alerts"
# }

# Ініціалізуємо менеджер сесії
# session_manager = AlertSessionManager(db_config=DB_CONFIG)
session_manager = AlertSessionManager()

# Глобальна змінна для збереження часу останньої загрози
last_danger_time = None

# Глобальна змінна кількості загроз за сесію
danger_count = 1

# Ініціалізація клієнта
client = TelegramClient('hub_app_session', API_ID, API_HASH)


@client.on(events.NewMessage(chats=TARGET_CHANNEL))
async def handle_new_message(event):
    global last_danger_time
    global danger_count

    # Назва чату
    chat_title = event.chat.title

    # Перевести в місцевий часовий пояс вашої системи
    msg_time = event.date.astimezone()

    # Відформатувати у зручний рядок (наприклад: "07.08.2026 14:30:05")
    formatted_date = msg_time.strftime("%d.%m.%Y %H:%M:%S")

    # print(f"Час відправки: {formatted_date}")

    # Отримуємо текст повідомлення
    text = event.text

    if not text:
        return

    # Чистимо текст(модуль search)
    text = clean_text(text)

    # Приводимо текст до нижнього регістру, щоб пошук не залежав від великих/малих літер
    text_lower = text.lower()

    # Шукаємо, які саме ключові слова є в тексті
    found_keywords = [kw for kw in KEYWORDS if kw in text_lower]
    # print('found keywords:', found_keywords)

    # Якщо знайшли хоча б одне слово
    if found_keywords:
        # winsound.Beep(1000, 5000)
        print(
            f"Сповіщення #{danger_count}. Час відправки: {formatted_date}")

        matched_str = ", ".join(found_keywords)
        print(f"Знайдено ключові слова: {matched_str}")

        print(text)
        # print('_'*59)

        if len(text) <= 100:
            # Формуємо текст сповіщення
            notification = (
                f"**Знайдено ключові слова:** `{matched_str}`\n"
                f"**Канал:** {chat_title if event.chat else 'Канал'}\n"
                f"---\n"
                f"{text}"
            )

            # Сповіщення надсилається у ваші "Збережені повідомлення" (Saved Messages)
            await client.send_message('me', notification)

            alert_data = {
                # Прибираємо tzinfo для класичного DATETIME в MySQL, для json - рядок
                "timestamp": msg_time.strftime("%Y-%m-%d %H:%M:%S"),
                "type": "ORDINARY",
                "chat": chat_title if event.chat else "Unknown",
                "text": text,
                "keywords": matched_str
            }
            # save_to_jsonl(alert_data)

            # 2. Створюємо об'єкт Alert і додаємо його в сесійний масив ООП
            new_alert = Alert(
                message_time=msg_time,
                alert_type="ORDINARY",
                chat_title=chat_title,
                message_text=text,
                keywords=matched_str
            )
            # session_manager.add_alert(new_alert)

            danger_count += 1

            is_danger = find_keywords(text)
            is_clear = all_clear(text)

            if is_danger:
                # Зберігаємо/оновлюємо час останньої загрози
                last_danger_time = datetime.now()

                # Переписуєм тип повідомлення
                alert_data["type"] = "DANGER"
                new_alert.alert_type = "DANGER"

                winsound.Beep(1000, 10000)
                print("⚠️ Виявлено загрозу!")

            elif is_clear:
                now = datetime.now()

                # Переписуєм тип повідомлення
                alert_data["type"] = "ALL CLEAR"
                new_alert.alert_type = "ALL CLEAR"

                # Перевіряємо, чи була загроза і чи минуло менше ніж 12 хвилин
                if last_danger_time is not None and (now - last_danger_time) <= timedelta(minutes=12):
                    print("🟢 Відбій. Не на Суми або впали. Подаємо сигнал.")

                    for _ in range(3):
                        winsound.Beep(1000, 2000)
                        # Пауза 1 секунда між сигналами
                        time.sleep(1)

                    last_danger_time = None

                else:
                    print(
                        "ℹ️ 'Відбій' отримано, але з моменту загрози минуло більше 10 хвилин (або загрози   не було). Звук вимкнено.")

            save_to_jsonl(alert_data)
            session_manager.add_alert(new_alert)

        print('-'*60)


# 3. Правильний запуск клієнта через контекстний менеджер
if __name__ == '__main__':
    print("Бот запущений, слухає нові повідомлення...")

    with client:
        client.run_until_disconnected()

    print("\n[!] Роботу програми зупинено користувачем.")
