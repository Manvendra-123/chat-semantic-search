import sys

with open("chatsearch/retrieve.py", "r") as f:
    content = f.read()

content = content.replace("seen_centers: set[int] = set()", "seen_message_ids: set[int] = set()")
content = content.replace("""    for pid in ranked:
        p = index.passages[pid]
        if p.center_id in seen_centers:
            continue
        seen_centers.add(p.center_id)
        why = []""", """    for pid in ranked:
        p = index.passages[pid]
        why = []""")

with open("chatsearch/retrieve.py", "w") as f:
    f.write(content)
