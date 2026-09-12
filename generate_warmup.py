import json
import random

with open("data/corpus.jsonl", "r") as f:
    messages = [json.loads(line) for line in f if line.strip()]

template_msgs = [m for m in messages if len(m["text"].split()) >= 4 and m["text"] != "<media>"]

random.seed(123)
selected = random.sample(template_msgs, 60)

for i, m in enumerate(selected):
    print(f'"{m["text"]}",')
