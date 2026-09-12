import sys

with open("chatsearch/build_corpus.py", "r") as f:
    content = f.read()

# restore original july_intern
wrong = """            ("Aman", "major project groups freeze krne h, kaun kis ke saath?"),
            ("Sneha", "hum log saath kar rahe h - me, priya, kritika"),
            ("Rohit", "mera ankit aur ishaan ke saath"),
            ("Aman", "kisi ko attendance aur report sambhalne ko bolo"),
            ("Sneha", "priya handle karegi, she is good with docs"),
            ("Priya", "done"),
        ],
        tag_on={4: "project_lead"},"""
correct = """            ("Ankit", "cgpa cutoff?"),
            ("Priya", "6.5"),
            ("Devansh", "mai in"),
            ("Ishaan", "mai bhi"),
            ("Rohit", "cover letter chahiye kya"),
            ("Priya", "optional"),
            ("Kritika", "referral kisi ke pass"),
            ("Aman", "nahi"),
        ],
        tag_on={5: "july_intern"},"""
content = content.replace(wrong, correct)

# fix the actual project_lead
content = content.replace("tag_on={5: \"project_lead\"}", "tag_on={4: \"project_lead\"}")

with open("chatsearch/build_corpus.py", "w") as f:
    f.write(content)
