import json


def save_to_jsonl(data_dict):
    with open("alerts_log.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(data_dict, ensure_ascii=False) + "\n")


# Приклад використання:
alert_data = {
    "timestamp": event.date.astimezone().strftime("%Y-%m-%d %H:%M:%S"),
    "type": "DANGER",
    "chat": event.chat.title if event.chat else "Unknown",
    "text": event.text
}
save_to_jsonl(alert_data)
