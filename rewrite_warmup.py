import re

WARMUP_QUERIES = [
    ("sports complex me raat ko kisne mana kiya tha?", "lab assistant ne mana kar diya sports complex raat ko", "person"),
    ("kisko lab me bhookh lag rahi thi?", "aaj lab me bhookh lagi h", "meaning"),
    ("os class ke baare me kya pucha tha", "yo guys, os class h aaj?", "meaning"),
    ("maths ki keys mil gayi kya", "keys mil gaya kya maths?", "meaning"),
    ("raat ko stairs ke liye junior ne kya kaha", "junior ne bola stairs raat ko", "person"),
    ("boys team me kon kon the", "to boys side: mai ankit aman ishaan?", "person"),
    ("rishikesh sasta tha ya mehenga", "rishikesh sasta h thoda", "meaning"),
    ("kab tak start karne ko bola tha", "start karna h kal tak", "time"),
    ("physics practical ka kya karna tha", "physics ka practical download karna h", "meaning"),
    ("HOD ne shaam ko stairs pe kya pucha", "HOD pucha stairs shaam ko", "person"),
    ("gym me kiska charger chhoot gaya tha", "mera charger gym me reh gaya", "person"),
    ("senior ne library aane ka time kya diya", "senior ne bola library 2 baje", "time"),
    ("network file ke liye pucha kiske paas h", "file kisi ke pass h network?", "meaning"),
    ("department me placement cell ne kis time bulaya", "placement cell bataya department shaam ko", "time"),
    ("raat ko sports complex chalne ka plan", "raat ko milte h sports complex pe", "time"),
    ("auditorium ka postpone kisne kiya tha subah", "guard postpone kiya auditorium subah", "person"),
    ("cn file complete karni thi uske baare me", "cn ka file complete karna h", "meaning"),
    ("physics ka kya start karna hai", "physics ka practical start karna h", "meaning"),
    ("chemistry class ke liye kisne bola tha raat ko", "night guys, chemistry class h aaj?", "meaning"),
    ("dean ko chhota kisne bola", "dean bahut chhota h yaar", "person"),
    ("lunch ke liye canteen kon aa raha hai", "lunch kon kon aa rha canteen", "meaning"),
    ("lab dopahar me senior aayega ye kab bola tha", "senior aayega lab dopahar me", "person"),
    ("abhi library milne ka kya time hua tha", "abhi milte h library pe", "time"),
    ("placement cell ne kya bheja hai friday lab ke liye", "placement cell bheja h lab friday", "time"),
    ("lab pe aaj aane ka plan kab banaya", "aaj milte h lab pe", "time"),
    ("group me kon sirf dekhta hai", "wo group me sirf dekhta h", "meaning"),
    ("maths ka print kya nikalna hai phone ka", "maths ka phone print nikalna h", "meaning"),
    ("bhaiya ne mess 2 baje se kyun mana kiya", "bhaiya ne mana kar diya mess 2 baje", "time"),
    ("phone canteen me kiska reh gaya tha", "mera phone canteen me reh gaya", "meaning"),
    ("vote nahi h ye kab bola tha", "ye koi vote nhi h", "meaning"),
    ("physics mast hai ye baat thi", "yeh physics kitna mast h", "meaning"),
    ("gym shaam ko aane ke liye bola", "shaam ko milte h gym pe", "time")
]

# Total: 15 meaning, 8 person, 9 time.
# Verify counts:
counts = {"meaning": 0, "person": 0, "time": 0}
for _, _, i in WARMUP_QUERIES:
    counts[i] += 1
print("Counts:", counts)

with open("chatsearch/build_corpus.py", "r") as f:
    content = f.read()

# I will replace lines 668-685 with a hardcoded loop.
import textwrap

new_code = """
    # Warmup queries (Hand-authored realistic search intent)
    WARMUP = [
        ("sports complex me raat ko kisne mana kiya tha?", "lab assistant ne mana kar diya sports complex raat ko", "person"),
        ("kisko lab me bhookh lag rahi thi?", "aaj lab me bhookh lagi h", "meaning"),
        ("os class ke baare me kya pucha tha", "yo guys, os class h aaj?", "meaning"),
        ("maths ki keys mil gayi kya", "keys mil gaya kya maths?", "meaning"),
        ("raat ko stairs ke liye junior ne kya kaha", "junior ne bola stairs raat ko", "person"),
        ("boys team me kon kon the", "to boys side: mai ankit aman ishaan?", "person"),
        ("rishikesh sasta tha ya mehenga", "rishikesh sasta h thoda", "meaning"),
        ("kab tak start karne ko bola tha", "start karna h kal tak", "time"),
        ("physics practical ka kya karna tha", "physics ka practical download karna h", "meaning"),
        ("HOD ne shaam ko stairs pe kya pucha", "HOD pucha stairs shaam ko", "person"),
        ("gym me kiska charger chhoot gaya tha", "mera charger gym me reh gaya", "person"),
        ("senior ne library aane ka time kya diya", "senior ne bola library 2 baje", "time"),
        ("network file ke liye pucha kiske paas h", "file kisi ke pass h network?", "meaning"),
        ("department me placement cell ne kis time bulaya", "placement cell bataya department shaam ko", "time"),
        ("raat ko sports complex chalne ka plan", "raat ko milte h sports complex pe", "time"),
        ("auditorium ka postpone kisne kiya tha subah", "guard postpone kiya auditorium subah", "person"),
        ("cn file complete karni thi uske baare me", "cn ka file complete karna h", "meaning"),
        ("physics ka kya start karna hai", "physics ka practical start karna h", "meaning"),
        ("chemistry class ke liye kisne bola tha raat ko", "night guys, chemistry class h aaj?", "meaning"),
        ("dean ko chhota kisne bola", "dean bahut chhota h yaar", "person"),
        ("lunch ke liye canteen kon aa raha hai", "lunch kon kon aa rha canteen", "meaning"),
        ("lab dopahar me senior aayega ye kab bola tha", "senior aayega lab dopahar me", "person"),
        ("abhi library milne ka kya time hua tha", "abhi milte h library pe", "time"),
        ("placement cell ne kya bheja hai friday lab ke liye", "placement cell bheja h lab friday", "time"),
        ("lab pe aaj aane ka plan kab banaya", "aaj milte h lab pe", "time"),
        ("group me kon sirf dekhta hai", "wo group me sirf dekhta h", "meaning"),
        ("maths ka print kya nikalna hai phone ka", "maths ka phone print nikalna h", "meaning"),
        ("bhaiya ne mess 2 baje se kyun mana kiya", "bhaiya ne mana kar diya mess 2 baje", "time"),
        ("phone canteen me kiska reh gaya tha", "mera phone canteen me reh gaya", "meaning"),
        ("vote nahi h ye kab bola tha", "ye koi vote nhi h", "meaning"),
        ("physics mast hai ye baat thi", "yeh physics kitna mast h", "meaning"),
        ("gym shaam ko aane ke liye bola", "shaam ko milte h gym pe", "time")
    ]

    text_to_msg = {m["text"]: m for m in b.messages}

    for i, (q_text, expected_text, intent) in enumerate(WARMUP):
        msg = text_to_msg.get(expected_text)
        if not msg:
            print(f"WARNING: WARMUP MSG NOT FOUND: {expected_text}")
            continue
        queries.append({
            "id": f"W{i+1:02d}",
            "query": q_text,
            "gold_id": msg["id"],
            "gold_sender": msg["sender"],
            "gold_ts": msg["ts"],
            "gold_text": msg["text"],
            "intent": intent,
            "hard": False,
            "zero_overlap": False
        })
"""

# The chunk to replace is from `import random` to `zero_overlap": False\n        })`
start_idx = content.find("    import random")
end_idx = content.find("        })\n", start_idx) + 11

if start_idx != -1 and end_idx != -1:
    new_content = content[:start_idx] + new_code + content[end_idx:]
    with open("chatsearch/build_corpus.py", "w") as f:
        f.write(new_content)
    print("Replaced successfully!")
else:
    print("Could not find replacement block.")
