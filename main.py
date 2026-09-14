
from telethon import TelegramClient, events
import winsound
import asyncio
import time
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from source.db_manager import Alert, AlertSessionManager
from source.search import *  # функції пошуку ключових слів і обробки тексту
from source.loading import save_to_jsonl

# 1. Дані авторизації
load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

# 2. Налаштування відстеження
# Можна вказати @username (рядок) або ID каналу (число int)
TARGET_CHANNEL = '@sumygo'

# Список ключових слів (пишемо в нижньому регістрі для зручності)
KEYWORDS = ['каб', 'сум', 'баліст', 'ракет', 'реактив', 'впал', 'впав']

# Конфігурація підключення до MySQL
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": os.getenv("DB_PAROL"),
    "database": "telegram_bot_db",
    "charset": "utf8mb4",       # Для кирилиці
    "use_unicode": True
}

# Ініціалізуємо менеджер сесії
session_manager = AlertSessionManager(db_config=DB_CONFIG)

# Глобальна змінна для збереження часу останньої загрози
last_danger_time = None

# Ініціалізація клієнта
client = TelegramClient('dev_app_session', API_ID, API_HASH)


@client.on(events.NewMessage(chats=TARGET_CHANNEL))
async def handle_new_message(event):
    global last_danger_time

    try:
        # Назва чату
        chat_title = event.chat.title if event.chat else "Unknown"

        # # 2. Перевести в місцевий часовий пояс
        msg_time = event.date.astimezone()

        # # 3. Відформатувати у зручний рядок
        formatted_date = msg_time.strftime("%d.%m.%Y %H:%M:%S")

        # Отримуємо текст повідомлення
        text = event.text

        if not text:
            print('no text')
            return

        # Чистимо текст(модуль search)
        text = clean_text(text)

        # Приводимо текст до нижнього регістру, щоб пошук не залежав від великих/малих літер
        text_lower = text.lower()

        # Шукаємо, які саме ключові слова є в тексті
        found_keywords = [kw for kw in KEYWORDS if kw in text_lower]

    except Exception as e:
        # Сюди потраплять помилки обробки конкретного повідомлення
        print(f"Помилка під час обробки повідомлення: {e}")

    # Якщо знайшли хоча б одне слово
    if found_keywords:
        # Збільшуємо лічильник одразу при вході
        session_manager.d_count += 1

        print(
            f"Сповіщення #{session_manager.d_count}. Час відправки: {formatted_date}")

        matched_str = ", ".join(found_keywords)
        print(f"Знайдено ключові слова: {matched_str}")

        text_lenth = len(text)

        # Якщо повідомлення длиннне - навряд, що це сповіщення про загрозу
        if text_lenth > 100:
            print(f"Довгий текст... {text_lenth} символів")
            print('_'*60)
            return

        print(text)

        # Формуємо текст сповіщення
        notification = (
            f"**Знайдено ключові слова:** `{matched_str}`\n"
            f"**Канал:** {chat_title}\n"
            f"---\n"
            f"{text}"
        )

        # Сповіщення надсилається у "Збережені повідомлення" (Saved Messages)
        await client.send_message('me', notification)

        # Створюємо словник для JASON
        alert_data = {
            "timestamp": msg_time.strftime("%Y-%m-%d %H:%M:%S"),
            "type": "ORDINARY",
            "chat": chat_title,
            "text": text,
            "keywords": matched_str
        }
        # save_to_jsonl(alert_data)

        # 2. Створюємо об'єкт Alert і додаємо його в сесійний масив ООП
        new_alert = Alert(
            message_time=msg_time,
            alert_type=1,
            chat_title=chat_title,
            message_text=text,
            keywords=matched_str
        )
        # session_manager.add_alert(new_alert)

        # Перевірка умов підвищеної небезпекм та відбою
        is_danger = find_keywords(text)
        is_clear = all_clear(text)

        if is_danger:
            # Зберігаємо/оновлюємо час останньої загрози
            last_danger_time = datetime.now()

            # Переписуєм тип повідомлення
            is_kab = check_kab(text)

            if is_kab:
                alert_data["type"] = "HIGH DANGER"
                new_alert.alert_type = 3
                asyncio.create_task(asyncio.to_thread(
                    winsound.Beep, 1000, 10000))  # асінх. звуковий сигнал
            else:
                alert_data["type"] = "DANGER"
                new_alert.alert_type = 2
                asyncio.create_task(asyncio.to_thread(
                    winsound.Beep, 1000, 3000))  # асінх. звуковий сигнал

            # winsound.Beep(1000, 10000)
            print("⚠️ Виявлено загрозу!")

        elif is_clear:                          # Відбій тривоги
            now = datetime.now()

            # Переписуєм тип повідомлення
            alert_data["type"] = "ALL-CLEAR"
            new_alert.alert_type = 4

            # Перевіряємо, чи була загроза і чи минуло менше ніж 10 хвилин (КАБи долітають за 3-5 хвилин)
            if last_danger_time is not None and (now - last_danger_time) <= timedelta(minutes=10):
                print("🟢 Відбій. Не на Суми або впали. Подаємо сигнал.")

                # for _ in range(3):
                #     winsound.Beep(800, 2000)
                #     time.sleep(1)             # Пауза 1 секунда між сигналами

                # Асінхронна функція Для серії звуків відбою:
                async def play_clear_sound():
                    for _ in range(3):
                        winsound.Beep(800, 2000)
                        # саме asyncio.sleep, а не time.sleep!
                        await asyncio.sleep(1)

                asyncio.create_task(play_clear_sound())

                # Скидуєм таймер
                last_danger_time = None

            else:
                print(
                    "'Відбій' отримано, але з моменту загрози минуло більше 10 хвилин (або загрози не було). Звук вимкнено.")

        save_to_jsonl(alert_data)
        session_manager.add_alert(new_alert)

        print('-'*60)


if __name__ == '__main__':
    print(datetime.now(), " Бот запущений, слухає нові повідомлення...")

    try:
        with client:
            client.run_until_disconnected()

    except Exception as e:
        # Сюди потраплять лише реальні помилки (наприклад, втрата мережі чи збій API)
        print(f"\n[!] Критична помилка під час роботи бота: {e}")

    finally:
        # Цей блок ВИКОНАЄТЬСЯ ЗАВЖДИ: при Ctrl+C, при закритті вікна або при помилці
        print("\n[!] Збереження сесії в базу даних...")
        try:
            empty_storage_flag = session_manager.save_session_to_db()
            if empty_storage_flag != 0:
                print("✅ Дані успішно збережено в БД.")
        except Exception as db_err:
            print(f"❌ Не вдалося зберегти дані в БД: {db_err}")

        print("[!] Роботу програми завершено.")
