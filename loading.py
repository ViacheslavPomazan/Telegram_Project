import json


def save_to_jsonl(data_dict):
    with open("alerts_log.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(data_dict, ensure_ascii=False) + "\n")
