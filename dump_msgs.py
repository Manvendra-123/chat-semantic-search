import re
with open("chatsearch/build_corpus.py") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if '("Sneha"' in line or '("Rohit"' in line or '("Priya"' in line or '("Devansh"' in line or '("Aman"' in line or '("Ankit"' in line or '("Kritika"' in line or '("Ishaan"' in line:
        if '("Sneha", "hum log saath kar rahe h - me, priya, kritika")' in line:
            pass # ignore
        print(f"{i}: {line.strip()}")
