from telethon import TelegramClient, events

# Дані отримуються на сайті my.telegram.org
api_id = 1234567  
api_hash = 'ваш_api_hash'

client = TelegramClient('session_name', api_id, api_hash)

# Слухач подій: реагує лише на нові повідомлення у конкретному каналі
@client.on(events.NewMessage(chats='назва_або_id_каналу'))
async def my_event_handler(event):
    # Отримуємо текст нового повідомлення
    text = event.text
    print(text)
    # Тут ваш код для обробки (запис в БД, пересилання тощо)

#Запуск клієнта
client.start()
client.run_until_disconnected()
