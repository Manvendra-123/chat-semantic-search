import random
import json

NAMES = ["Rohit", "Sneha", "Ankit", "Devansh", "Aman", "Priya", "Kritika", "Ishaan", "sir", "HOD", "guard", "bhaiya"]
TIMES = ["subah", "shaam ko", "raat ko", "dopahar me", "kal", "aaj", "2 baje", "4 baje", "next week", "monday", "friday"]
NUMBERS = ["2", "3", "4", "5", "10", "15", "20", "50", "100", "500"]
LOCATIONS = ["canteen", "library", "hostel", "lab", "auditorium", "ground", "gym", "mess", "main gate", "department", "parking"]
SUBJECTS = ["dbms", "os", "cn", "dsa", "maths", "physics", "chemistry"]

BASE_SENTENCES = [
    "bhai {name} ko bolna ki {time} tak aa jaye.",
    "kal {time} koi class h kya?",
    "maine {number} baje ka alarm lagaya tha, miss ho gaya.",
    "kisi ke paas {subject} ke notes hain kya?",
    "mujhe {time} {location} me milna.",
    "mera bag {location} me reh gaya tha.",
    "aaj {location} ki light nahi aa rahi.",
    "{name} ne bola tha ki wo {time} aayega.",
    "bhai {number} pages ka printout nikalna hai.",
    "mujhe lag raha hai {subject} me back aayegi.",
    "kya {name} aaj class aaya tha?",
    "wifi {location} me bilkul nahi chal raha.",
    "bhookh lagi hai, {location} chalein?",
    "assignment {time} tak submit karna hai.",
    "yeh {subject} ka syllabus kab khatam hoga.",
    "sir ne {time} attendance li thi kya?",
    "bhai mere paas sirf {number} rupe bache hain.",
    "kal se {subject} padhna shuru karunga.",
    "kisi ne mera charger dekha kya {location} me?",
    "abhi {time} ho gaya aur neend aa rahi hai.",
    "kal {name} ka birthday hai na?",
    "mujhe kal {time} ghar nikalna hai.",
    "aaj {time} baarish ho rahi thi.",
    "kya kisi ne {subject} ki assignment complete ki?",
    "mujhe {number} din ki chhutti chahiye.",
    "{name} kahan hai yaar, call nahi utha raha.",
    "aaj {location} me bahut bheed thi.",
    "bhai {subject} ka practical file ban gaya?",
    "mujhe {time} utha dena please.",
    "is baar {subject} ka paper bahut tough tha.",
    "kal se roz {time} uthunga.",
    "bhai {number} minute me pahuch raha hu.",
    "{name} ne mujhe message kiya tha {time}.",
    "kya aaj {subject} ki class cancel ho gayi?",
    "mujhe lagta hai {name} ko pata hoga.",
    "aaj {time} thodi thand lag rahi hai.",
    "kisi ko pata hai {location} kab khulega?",
    "mujhe is semester {number} subjects clear karne hain.",
    "{name} se notes le lena {time}.",
    "mujhe lagta hai kal {time} test hai.",
    "yeh {subject} samajh nahi aa raha.",
    "bhai {location} aaja, wait kar raha hu.",
    "kya aaj {time} kuch plan hai?",
    "mujhe apne marks dekhe {number} din ho gaye.",
    "{name} ko bol dena ki main late hounga.",
    "aaj {time} thoda jaldi free ho jaunga.",
    "kisi ne {name} ko dekha kya aaj?",
    "mujhe {location} jana hai {time}.",
    "bhai {number} log aa rahe hain.",
    "yeh {subject} ka assignment kal {time} dena hai."
]

def generate_bank():
    bank = set()
    rng = random.Random(42)

    while len(bank) < 450:
        template = rng.choice(BASE_SENTENCES)
        sentence = template
        if "{name}" in sentence:
            sentence = sentence.replace("{name}", rng.choice(NAMES))
        if "{time}" in sentence:
            sentence = sentence.replace("{time}", rng.choice(TIMES))
        if "{number}" in sentence:
            sentence = sentence.replace("{number}", rng.choice(NUMBERS))
        if "{location}" in sentence:
            sentence = sentence.replace("{location}", rng.choice(LOCATIONS))
        if "{subject}" in sentence:
            sentence = sentence.replace("{subject}", rng.choice(SUBJECTS))
        bank.add(sentence)

    return list(bank)

if __name__ == "__main__":
    sentences = generate_bank()
    print(f"Generated {len(sentences)} unique sentences.")
    print("-" * 50)
    for s in random.Random(7).sample(sentences, 30):
        print(s)
