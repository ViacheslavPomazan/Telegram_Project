from telethon import TelegramClient, events
import winsound
import re
import time
from datetime import datetime, timedelta

# 1. Дані авторизації (з my.telegram.org)
API_ID = 1111111  # Замініть на ваш цілочисельний API ID
API_HASH = '<your hash>'

# 2. Налаштування відстеження
# Можна вказати @username (рядок) або ID каналу (число int)
TARGET_CHANNEL = '@sumygo'

# Список ключових слів (пишемо в нижньому регістрі для зручності)
KEYWORDS = ['каб', 'сум', 'баліст']

# Глобальна змінна для збереження часу останньої загрози
last_danger_time = None

# 1.синхронна функція пошуку


def not_sumy(text):
    if not text:
        return False
    # pattern = r'не\s+на\s+Сум(?:и|ах|ам)?'
    pattern = r'\bне\s+(?:на\s+)?Сум(?:и|ах|ам)?\b'
    condition = bool(re.search(pattern, text, re.I))

    return condition


def all_clear(text):
    if not text:
        return False
    # pattern = r'не\s+на\s+Сум(?:и|ах|ам)?'
    pattern1 = r'\bне\s+(?:на\s+)?Сум(?:и|ах|ам)?\b'
    condition1 = bool(re.search(pattern1, text, re.I))

    pattern2 = r'\b(впали|впав|впала|впало)\b'
    condition2 = bool(re.search(pattern2, text, re.I))

    return condition1 or condition2


def find_keywords(text):
    not_sum = not_sumy(text)

    if not text or not_sum:
        return False

    kab = r'\bКАБ(?:и|ів|ами|ах|ам|ом)?\b'
    sumy = r'\bСум(?:и|ам|ами|ах)?\b'
    ballistic = r'\bбаліст\w*'

    # Використовуємо re.IGNORECASE (re.I), щоб не зважати на великі/малі літери
    condition_1 = bool(re.search(kab, text, re.I)
                       and re.search(sumy, text, re.I))
    condition_2 = bool(re.search(ballistic, text, re.I)
                       and re.search(sumy, text, re.I))

    return condition_1 or condition_2


# Ініціалізація клієнта
client = TelegramClient('session_name', API_ID, API_HASH)


@client.on(events.NewMessage(chats=TARGET_CHANNEL))
async def handle_new_message(event):
    global last_danger_time

    # # 2. Перевести в місцевий часовий пояс вашої системи
    msg_time = event.date.astimezone()

    # # 3. Відформатувати у зручний рядок (наприклад: "07.08.2026 14:30:05")
    formatted_date = msg_time.strftime("%d.%m.%Y %H:%M:%S")

    # print(f"Час відправки: {formatted_date}")

    # Отримуємо текст повідомлення
    text = event.text
    # print(text)
    if not text:
        return

    # Приводимо текст до нижнього регістру, щоб пошук не залежав від великих/малих літер
    text_lower = text.lower()

    # Шукаємо, які саме ключові слова є в тексті
    found_keywords = [kw for kw in KEYWORDS if kw in text_lower]
    # print('found keywords:', found_keywords)

    # Якщо знайшли хоча б одне слово
    if found_keywords:
        # winsound.Beep(1000, 5000)
        print(f"Час відправки: {formatted_date}")

        matched_str = ", ".join(found_keywords)
        print(f"Знайдено ключові слова: {matched_str}")

        print(text)
        # print('_'*59)

        # Формуємо текст сповіщення
        notification = (
            f"**Знайдено ключові слова:** `{matched_str}`\n"
            f"**Канал:** {event.chat.title if event.chat else 'Канал'}\n"
            f"---\n"
            f"{text}"
        )

        # Сповіщення надсилається у ваші "Збережені повідомлення" (Saved Messages)
        await client.send_message('me', notification)

        is_danger = find_keywords(text)
        is_clear = all_clear(text)

        if is_danger:
            # Зберігаємо/оновлюємо час останньої загрози
            last_danger_time = datetime.now()

            winsound.Beep(1000, 10000)
            print("⚠️ Виявлено загрозу!")

        elif is_clear:
            now = datetime.now()

            # Перевіряємо, чи була загроза і чи минуло менше ніж 12 хвилин
            if last_danger_time is not None and (now - last_danger_time) <= timedelta(minutes=12):
                print("🟢 Відбій. Не на Суми або впали. Подаємо сигнал.")

                for _ in range(3):
                    winsound.Beep(1000, 2000)
                    time.sleep(1)             # Пауза 1 секунда між сигналами

                last_danger_time = None

            else:
                print(
                    "ℹ️ 'Відбій' отримано, але з моменту загрози минуло більше 10 хвилин (або загрози   не було). Звук вимкнено.")

        print('-'*60)


# 3. Правильний запуск клієнта через контекстний менеджер
if __name__ == '__main__':
    print("Бот запущений, слухає нові повідомлення...")
    try:
        with client:
            client.run_until_disconnected()
    except KeyboardInterrupt:
        print("\n[!] Роботу програми зупинено користувачем.")
