import json
import sys

sys.stdout.reconfigure(encoding="utf-8")


def read_from_jsonl():

    with open("alerts_log.jsonl", "r", encoding="utf-8") as f:
        for l in f:
            yield json.loads(l)


for mess in read_from_jsonl():
    print(mess['timestamp'], len(mess['text'])
          if len(mess['text']) > 100 else '')

    # alert_line = read_from_jsonl()
    # print(repr(alert_line['timestamp']))
