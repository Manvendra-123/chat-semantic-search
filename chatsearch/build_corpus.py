"""Deterministic synthetic corpus from SEED + the March–April seed transcript.

The March–April messages are kept as-is (they already contain a long Manali
thread). May–August is generated from SEED so the full archive is ≥4000
messages, 8 people, 6 months, with two more long decision threads.
"""

from __future__ import annotations

import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

from chatsearch.textutil import tokenize, zero_overlap

SEED = "ITGEEKS-2027-MANVENDRA"
IST = timezone(timedelta(hours=5, minutes=30))
PEOPLE = ["Rohit", "Sneha", "Ankit", "Devansh", "Aman", "Priya", "Kritika", "Ishaan"]
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def parse_ts(value: str) -> datetime:
    return datetime.fromisoformat(value)


class CorpusBuilder:
    def __init__(self, seed: str = SEED) -> None:
        self.rng = random.Random(seed)
        self.messages: list[dict] = []
        self.tags: dict[str, int] = {}
        self._id = 0
        self._clock = datetime(2025, 2, 1, 9, 0, tzinfo=IST)
        self.seen_substantive = set()

    def load_seed(self) -> None:
        for name in ("raw_1.jsonl", "raw_2.jsonl"):
            path = DATA / name
            with path.open() as fh:
                for line in fh:
                    msg = json.loads(line)
                    self.messages.append(msg)
                    self._id = max(self._id, int(msg["id"]))
                    self._clock = parse_ts(msg["ts"])
        self.tags["manali_lock"] = 425
        self.tags["manali_vote"] = 415
        self.tags["hotel_rate"] = 348
        self.tags["priya_budget_ask"] = 284
        self.tags["project_deadline"] = 472
        self.tags["shukla_attendance"] = 35
        self.tags["datesheet"] = 254
        self.tags["lab_saturday"] = 23

    def emit(
        self,
        sender: str,
        text: str,
        *,
        kind: str = "text",
        reply_to: int | None = None,
        tag: str | None = None,
        minutes: int | None = None,
    ) -> dict:
        if minutes is None:
            minutes = self.rng.randint(1, 8)
        self._clock += timedelta(minutes=minutes)
        self._id += 1
        msg = {
            "id": self._id,
            "ts": self._clock.isoformat(),
            "sender": sender,
            "text": text,
            "reply_to": reply_to,
            "kind": kind,
        }
        self.messages.append(msg)
        if tag:
            self.tags[tag] = self._id
        return msg

    def jump(self, when: datetime) -> None:
        if when > self._clock:
            self._clock = when

    def burst(self, lines: list[tuple[str, str]], tag_on: dict[int, str] | None = None) -> None:
        tag_on = tag_on or {}
        for i, (sender, text) in enumerate(lines):
            kind = "text"
            body = text
            if text == "<media>":
                kind, body = "media_omitted", ""
            elif text.startswith("<fwd>:"):
                kind, body = "forwarded", text[6:].strip()
            self.emit(sender, body, kind=kind, tag=tag_on.get(i), minutes=self.rng.choice([1, 1, 2, 3, 12]))

    WORDS = {
        "subject": ["warden", "placement cell", "senior", "junior", "guard", "HOD", "bhaiya", "dost", "admin", "dean", "CR", "lab assistant"],
        "verb": ["ne bola", "ne mana kar diya", "cancel kar diya", "postpone kiya", "bheja h", "check kar raha", "aayega", "pucha", "bataya", "announce kiya", "daant lagayi"],
        "place": ["canteen", "library", "hostel", "lab", "auditorium", "ground", "gym", "mess", "main gate", "department", "parking", "sports complex", "common room", "stairs"],
        "time_hint": ["kal", "aaj", "shaam ko", "subah", "2 baje", "next week", "abhi", "raat ko", "tuesday", "friday", "weekend pe", "dopahar me"],
        "noun": ["notes", "pdf", "file", "record", "assignment", "practical", "laptop", "charger", "bag", "id card", "keys", "wallet", "phone", "bottle", "copy", "pen", "register", "printout"],
        "question": ["kisi ke pass h", "kisko chahiye", "kahan h", "kab tak dena h", "kaun laya h", "dekha kya kisi ne", "mil gaya kya", "submit kiya kya", "ban gaya tera"],
        "greeting": ["good morning", "gn", "hello", "hi", "namaste", "yo", "sup", "morning", "night", "hey"],
        "topic": ["dbms", "os", "cn", "dsa", "maths", "physics", "chemistry", "compiler", "network", "cloud"],
        "reaction": ["lol", "lmao", "sad", "oof", "damn", "nice", "ok", "hmm", "haan", "nhi", "true", "same", "bet", "+1", "achha", "sahi"],
        "action": ["padhna h", "submit karna h", "print nikalna h", "xerox karna h", "download karna h", "mail karna h", "complete karna h", "start karna h"],
        "complaint": ["too much syllabus", "network down h", "light nahi h", "barish ho rahi h", "garmi bahot h", "thak gaya", "nind aa rahi", "bhookh lagi h", "sir dard h"],
        "random_adj": ["bekar", "mast", "heavy", "easy", "hard", "lamba", "chhota", "boring", "interesting", "faaltu", "lame", "awesome"]
    }

    TEMPLATES = [
        "{subject} {verb} {place} {time_hint}",
        "{noun} {question} {topic}?",
        "{greeting} guys, {topic} class h aaj?",
        "mera {noun} {place} me reh gaya",
        "aaj {place} me {complaint}",
        "{topic} ka {noun} {action}",
        "yeh {topic} kitna {random_adj} h",
        "{reaction}",
        "koi {place} chal raha h?",
        "{time_hint} milte h {place} pe",
        "{subject} bahut {random_adj} h yaar",
        "{action} {time_hint} tak",
        "kisi ne {topic} {action} kya",
    ]

    def get_filler_text(self) -> str:
        while True:
            template = self.rng.choice(self.TEMPLATES)
            text = template
            while "{" in text:
                start = text.find("{")
                end = text.find("}")
                key = text[start+1:end]
                val = self.rng.choice(self.WORDS[key])
                text = text[:start] + val + text[end+1:]

            if len(text) > 12:
                if text in self.seen_substantive:
                    continue
                self.seen_substantive.add(text)
            return text

    def chatter(self, n: int) -> None:
        for _ in range(n):
            if self.rng.random() < 0.04:
                self.emit(self.rng.choice(PEOPLE), "", kind="media_omitted")
                continue
            if self.rng.random() < 0.03:
                self.emit(
                    self.rng.choice(PEOPLE),
                    self.rng.choice(FORWARDS),
                    kind="forwarded",
                )
                continue
            sender = self.rng.choice(PEOPLE)
            text = self.get_filler_text()
            self.emit(sender, text)
            if self.rng.random() < 0.35:
                self.emit(self.rng.choice(PEOPLE), self.rng.choice(BACKCHANNELS), minutes=self.rng.randint(1, 4))


def build_queries(tags: dict[str, int], id_to_msg: dict[int, dict]) -> list[dict]:
    spec = [
        # --- 8 hard zero-overlap queries (the actual assignment) ---
        {
            "id": "H1",
            "query": "When did we lock the hill station?",
            "gold": "manali_lock",
            "intent": "meaning",
            "hard": True,
        },
        {
            "id": "H2",
            "query": "How much should each person chip in for the fest?",
            "gold": "fest_amount",
            "intent": "person",
            "hard": True,
        },
        {
            "id": "H3",
            "query": "Who is leading the major project group?",
            "gold": "project_lead",
            "intent": "meaning",
            "hard": True,
        },
        {
            "id": "H4",
            "query": "What time does the overnight coach depart?",
            "gold": "volvo_time",
            "intent": "meaning",
            "hard": True,
        },
        {
            "id": "H5",
            "query": "Did she cap the spending for everyone?",
            "gold": "priya_cap",
            "intent": "person",
            "hard": True,
        },
        {
            "id": "H6",
            "query": "What did we discuss last month about internships?",
            "gold": "july_intern",
            "intent": "time",
            "hard": True,
        },
        {
            "id": "H7",
            "query": "Where are we staying in the mountains?",
            "gold": "stay_lock",
            "intent": "meaning",
            "hard": True,
        },
        {
            "id": "H8",
            "query": "Which professor scheduled the makeup test?",
            "gold": "makeup_test",
            "intent": "meaning",
            "hard": True,
        },
        # --- 32 warmup queries ---
        # Generated dynamically below
    ]
    extra_tags = {
        "devansh_parents": 339,
        "ankit_swim": 280,
        "goa_reject": 269,
        "kritika_snow": 367,
        "tickets_done": 433,
        "canteen_lunch": 10,
        "dbms_due": 58,
    }
    tags = {**extra_tags, **tags}
    out = []
    for row in spec:
        gold_id = tags[row["gold"]]
        gold_msg = id_to_msg[gold_id]
        item = {
            "id": row["id"],
            "query": row["query"],
            "gold_id": gold_id,
            "gold_sender": gold_msg["sender"],
            "gold_ts": gold_msg["ts"],
            "gold_text": gold_msg["text"],
            "intent": row["intent"],
            "hard": row["hard"],
            "zero_overlap": zero_overlap(row["query"], gold_msg["text"]),
        }
        out.append(item)
    return out


FILLERS = [
    "class cancel h kya",
    "notes bhej dena",
    "attendance ho gyi?",
    "sir aaye kya",
    "hmm",
    "ok",
    "haan",
    "nhi",
    "lol",
    "😂",
    "same",
    "+1",
    "yaar assignment yaad dila",
    "koi canteen?",
    "mai late hu",
    "bench rakh lena",
    "kal lab h na",
    "file complete hui?",
    "pta nhi",
    "dekhte h",
    "bhej diya",
    "wait",
    "network kharab h",
    "call pe aa",
    "ghar ja rha",
    "mummy ne phone kiya",
    "rain ho rhi h campus me",
    "bus miss ho gyi",
    "library me hu",
    "wifi down h hostel ka",
    "cgpa ka tension",
    "placement baat later",
    "ye meme dekho",
    "{name} zinda h?",
    "kal holiday h kya",
    "form bharna h kya kisi ko",
    "id card bhul gya",
    "lab coat le aana",
    "viva postponed",
    "quiz surprise ho skta h",
    "unit 3 skip mat krna",
    "pyq bhej",
    "drive link chahiye",
    "pdf heavy h",
    "print nikalwa dena",
    "500 pages h 😭",
    "chai pe chalte h",
    "mess me aloo hi aloo h",
    "hostel gate 9:30 close",
    "warden mood off h",
    "nightout ka scene",
    "birthday kisika h kya",
    "spotify wrap kb aayega",
    "match dekh rha koi",
    "india jeeti?",
    "score bhej",
    "battery 2%",
    "typo sorry",
    "manali typo nahi tha wait",
    "goa wala joke phir se mat",
    "exam ke baad sochte h",
    "kal milte h",
    "ok bye",
    "gn",
    "gm",
    "class me aaja",
    "sir dekh rhe h",
    "mute kr de call",
    "screen share kr",
    "code compile nahi ho rha",
    "error bhej screenshot",
    "stackoverflow pe same tha",
    "deadline kal subah",
    "extension maango",
    "sir nahi denge",
    "try to kr",
    "done from my side",
    "review kr lena",
    "typo in report",
    "abstract chhota kr",
    "references add kr",
    "plag 18% tha",
    "turnitin slow h",
    "printer jam",
    "stationary khatam",
    "file cover black lena",
    "index page chahiye",
    "certificate scan bhej",
    "aadhar mat bhej group me",
    "otp mat share krna",
    "link expired",
    "naya link bhej",
    "drive access de",
    "folder me daal diya",
    "naam galat save h",
    "rename kr diya",
    "ok thanks",
    "np",
    "later",
    "busy",
    "class me hu",
    "lab me hu",
    "canteen aa ja",
    "5 min",
    "10 min late",
    "auto nahi mil rha",
    "traffic jam AB road",
    "indore garmi pagal",
    "ac hostel me nahi chal rha",
    "water cooler kharab",
    "light gayi thi 20 min",
    "inverter backup tha",
    "assignment copy mat maar",
    "khud kr le",
    "samajh nahi aaya topic",
    "kal explain kr dunga",
    "notes {name} ke pass honge",
    "priya ke notes clean hote h",
    "rohit late as always",
    "ishaan ghost mode",
    "devansh meme factory",
    "aman silent killer",
    "ankit panic kr rha hoga",
    "sneha organise kregi",
    "kritika toppers wali energy",
]

BACKCHANNELS = [
    "haan", "ok", "lol", "😂", "+1", "same", "true", "nhi", "acha", "hmm",
    "sahi", "thik", "done", "wait", "kya", "kyu", "ohh", "rip", "🙏", "💀",
    "nice", "cool", "bet", "chalega", "dekhte", "pakka?", "sure", "nopes",
]

FORWARDS = [
    "College notice: attendance shortlist releasing Friday.",
    "Fwd: intern fair 12 Aug auditorium 10am",
    "WhatsApp forward: cheap Manali package 3999 (scam lag rha)",
    "Drive: CN notes unit 1-4",
    "Reminder: exam form last date tomorrow 5pm",
    "Placement cell: resume workshop Thursday",
]


def generate() -> tuple[list[dict], list[dict]]:
    b = CorpusBuilder(SEED)
    b.load_seed()

    # --- early May: packing / stay lock / volvo (thread 1 conclusion) ---
    b.jump(datetime(2025, 5, 2, 19, 10, tzinfo=IST))
    b.burst(
        [
            ("Rohit", "packing list banao koi"),
            ("Sneha", "thermometer mat le aana 😂"),
            ("Kritika", "jacket zaroor"),
            ("Rohit", "ok layering kr lena, subah wali hawa kaat ti h"),
            ("Aman", "shoes kaunse"),
            ("Sneha", "comfortable, no new"),
        ],
        tag_on={3: "jacket_note"},
    )
    b.chatter(40)
    b.jump(datetime(2025, 5, 4, 21, 5, tzinfo=IST))
    b.burst(
        [
            ("Sneha", "stay confirm krna h aaj"),
            ("Rohit", "wo 1800 wala?"),
            ("Sneha", "haan"),
            ("Priya", "reviews theek h?"),
            ("Sneha", "3.8, location achi h mall road se 8 min"),
            ("Ankit", "book kr do warna may me bhar jayega"),
            ("Sneha", "snowview pg lock, 3 rooms, 1800 night. advance maine de diya"),
            ("Rohit", "upi bhej"),
            ("Sneha", "sneha@oksbi — 600 each abhi"),
            ("Devansh", "kal krta"),
            ("Aman", "done"),
        ],
        tag_on={6: "stay_lock", 8: "upi_id"},
    )
    b.chatter(50)
    b.jump(datetime(2025, 5, 6, 13, 40, tzinfo=IST))
    b.burst(
        [
            ("Rohit", "bus wali cheez fix"),
            ("Sneha", "delhi se night wali"),
            ("Rohit", "10:40 pm wali volvo pakdi h, late mat aana station"),
            ("Kritika", "indore-delhi train subah ki?"),
            ("Rohit", "haan 6:10 wali"),
            ("Ishaan", "mai delhi se milunga seedha"),
            ("Aman", "ok"),
        ],
        tag_on={2: "volvo_time", 5: "ishaan_confirm"},
    )
    b.chatter(80)

    # trip days (sparse checkins)
    b.jump(datetime(2025, 5, 14, 18, 20, tzinfo=IST))
    b.burst(
        [
            ("Rohit", "station pe 4 log pahuch gye"),
            ("Sneha", "2 min"),
            ("Devansh", "snack le aaya"),
            ("Kritika", "<media>"),
            ("Aman", "coldd"),
            ("Priya", "photos baad me dump krna drive pe"),
        ]
    )
    b.chatter(30)
    b.jump(datetime(2025, 5, 16, 22, 10, tzinfo=IST))
    b.burst(
        [
            ("Ankit", "rohtang postpone ho gya fog ki wajah se"),
            ("Kritika", "😭"),
            ("Sneha", "kal try"),
            ("Rohit", "ok"),
        ]
    )
    b.chatter(40)
    b.jump(datetime(2025, 5, 18, 21, 0, tzinfo=IST))
    b.burst(
        [
            ("Aman", "wapas aa gye"),
            ("Devansh", "ghar ke khane ki yaad"),
            ("Priya", "ab project"),
            ("Rohit", "kal sochte h"),
        ]
    )

    # --- Thread 2: major project group (late May) ---
    b.jump(datetime(2025, 5, 20, 20, 15, tzinfo=IST))
    b.burst(
        [
            ("Priya", "project groups freeze krne h 22 tk"),
            ("Rohit", "hum 8 ek group?"),
            ("Priya", "max 4"),
            ("Ankit", "to split"),
            ("Devansh", "mai Priya Kritika Sneha ke saath"),
        ]
    )
    b.burst(
        [
            ("Rohit", "to boys side: mai ankit aman ishaan?"),
            ("Ishaan", "haan"),
            ("Aman", "topic?"),
            ("Priya", "sir ne list di h"),
            ("Priya", "<media>"),
            ("Sneha", "chat search wala mat lena 😂"),
            ("Kritika", "attendance system bekar ho gya h overdone"),
            ("Priya", "library seat booking?"),
            ("Ankit", "boring"),
            ("Rohit", "mess waste tracker"),
            ("Devansh", "thik h"),
            ("Sneha", "hum log campus lost-and-found krte h, qr tags"),
            ("Kritika", "haan ye naya h"),
            ("Priya", "ok"),
            ("Rohit", "hum mess wala"),
            ("Aman", "roles?"),
            ("Rohit", "kal milke"),
            ("Priya", "lead decide kr lo wrna sir random de denge"),
            ("Kritika", "sneha krlegi, documentation tight rakhti h"),
            ("Sneha", "agar baaki log modules baant lo to theek h"),
            ("Priya", "haan"),
            ("Ankit", "ok"),
            ("Devansh", "done"),
            ("Kritika", "final: sneha handle kregi core, baaki modules split"),
            ("Priya", "sir ko mail kal"),
        ],
        tag_on={23: "project_lead"},
    )
    b.chatter(120)

    # June: fest budget thread 3
    b.jump(datetime(2025, 6, 3, 18, 40, tzinfo=IST))
    b.chatter(60)
    b.jump(datetime(2025, 6, 8, 19, 5, tzinfo=IST))
    b.burst(
        [
            ("Aman", "tech fest stall lena h kya"),
            ("Rohit", "haan warna CS dept empty dikhega"),
            ("Sneha", "budget?"),
            ("Devansh", "stall 2k + material"),
            ("Ankit", "paise kaha se"),
            ("Priya", "collection + sponsor"),
            ("Kritika", "sponsor kaun dega"),
            ("Rohit", "canteen wale se try"),
            ("Aman", "per person kitna"),
            ("Devansh", "800?"),
            ("Ankit", "zyada h"),
            ("Sneha", "500?"),
            ("Rohit", "abhi hisaab nikal"),
            ("Priya", "excel banati hu"),
            ("Priya", "<media>"),
            ("Priya", "per head 450 rakhte h, sponsor se rest nikal jayega"),
            ("Rohit", "ok"),
            ("Aman", "haan"),
            ("Devansh", "chalega"),
            ("Kritika", "kab dena"),
            ("Priya", "is hafte"),
            ("Ankit", "upi same?"),
            ("Priya", "priya@ibl"),
            ("Sneha", "stall kaun sambhalega din pe"),
            ("Rohit", "shifts bana denge"),
            ("Kritika", "mai sat morning"),
            ("Ishaan", "mai evening"),
            ("Priya", "haan limit ke upar mat jaana, main hisaab rakhungi"),
            ("Aman", "ok boss"),
            ("Sneha", "poster mai bana deti"),
            ("Devansh", "meme bhi laga dena"),
        ],
        tag_on={15: "fest_amount", 23: "fest_stall", 27: "priya_cap"},
    )
    b.chatter(150)

    b.jump(datetime(2025, 6, 18, 11, 20, tzinfo=IST))
    b.burst(
        [
            ("Ankit", "internal marks kab tak?"),
            ("Priya", "sir ne bola 25 june ke around list"),
            ("Rohit", "attendance wale dar"),
            ("Sneha", "shortfall mat banana"),
        ],
        tag_on={1: "internal_marks"},
    )
    b.chatter(80)

    b.jump(datetime(2025, 6, 27, 16, 0, tzinfo=IST))
    b.burst(
        [
            ("Kritika", "fest stall theek gya"),
            ("Rohit", "450 enough tha"),
            ("Priya", "31 leftover h, next event me use"),
            ("Aman", "nice"),
        ]
    )
    b.chatter(90)

    # July: internships (this is "last month" relative to August corpus end)
    b.jump(datetime(2025, 7, 9, 20, 10, tzinfo=IST))
    b.burst(
        [
            ("Aman", "placement cell ne mail ki"),
            ("Rohit", "kya"),
            ("Aman", "<fwd>: intern fair 12 Aug auditorium 10am"),
            ("Devansh", "resume?"),
            ("Sneha", "template bhejti"),
            ("Priya", "tcs wali form 18 tarikh tk bhar dena, late mat chhodna"),
            ("Ankit", "cgpa cutoff?"),
            ("Priya", "6.5"),
            ("Devansh", "mai in"),
            ("Ishaan", "mai bhi"),
            ("Rohit", "cover letter chahiye kya"),
            ("Priya", "optional"),
            ("Kritika", "referral kisi ke pass"),
            ("Aman", "nahi"),
        ],
        tag_on={5: "july_intern"},
    )
    b.chatter(160)
    b.jump(datetime(2025, 7, 21, 9, 15, tzinfo=IST))
    b.burst(
        [
            ("Sneha", "hackathon IITB campus, register 28 july tk"),
            ("Rohit", "team?"),
            ("Sneha", "same project wale"),
            ("Ankit", "online h kya"),
            ("Sneha", "hybrid"),
            ("Devansh", "fees?"),
            ("Sneha", "0"),
            ("Aman", "in"),
        ],
        tag_on={0: "hackathon_deadline"},
    )
    b.chatter(140)

    # August: makeup test + looking back
    b.jump(datetime(2025, 8, 4, 10, 5, tzinfo=IST))
    b.burst(
        [
            ("Ankit", "CN retest notice aaya"),
            ("Rohit", "kaunsa"),
            ("Ankit", "<media>"),
            ("Kritika", "shukla sir ne monday ko unit 2-3 se paper dubara rakha h"),
            ("Devansh", "mai dunga"),
            ("Aman", "same"),
            ("Priya", "notes same wale chalenge"),
            ("Rohit", "ok"),
        ],
        tag_on={3: "makeup_test"},
    )
    b.chatter(180)
    b.jump(datetime(2025, 8, 19, 19, 40, tzinfo=IST))
    b.chatter(80)
    b.jump(datetime(2025, 8, 28, 21, 10, tzinfo=IST))
    b.burst(
        [
            ("Rohit", "sem almost over"),
            ("Sneha", "next sem me trip phir?"),
            ("Devansh", "pehli baar toh jaane do settle"),
            ("Priya", "project demo 12 sept"),
            ("Kritika", "ok"),
            ("Aman", "intern form bhar di na sabne"),
            ("Ankit", "haan july me hi"),
            ("Ishaan", "gn"),
        ]
    )
    b.chatter(40)

    # Pad to at least 4000 if chatter landed short; extra nights of noise.
    while len(b.messages) < 4100:
        b.chatter(20)

    id_to_msg = {m["id"]: m for m in b.messages}
    queries = build_queries(b.tags, id_to_msg)
    import random
    template_msgs = [m for m in b.messages if len(m["text"].split()) >= 4 and m["text"] != "<media>" and "id" in m and not any(q["gold_id"] == m["id"] for q in queries)]
    random.seed(42)
    selected = random.sample(template_msgs, 32)

    for i in range(32):
        msg = selected[i]
        queries.append({
            "id": f"W{i+1:02d}",
            "query": msg["text"],
            "gold_id": msg["id"],
            "gold_sender": msg["sender"],
            "gold_ts": msg["ts"],
            "gold_text": msg["text"],
            "intent": "meaning",
            "hard": False,
            "zero_overlap": False
        })

    return b.messages, queries


def write_outputs(messages: list[dict], queries: list[dict]) -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    corpus_path = DATA / "corpus.jsonl"
    with corpus_path.open("w") as fh:
        for msg in messages:
            fh.write(json.dumps(msg, ensure_ascii=False) + "\n")
    (DATA / "queries.json").write_text(json.dumps(queries, indent=2, ensure_ascii=False))
    people = sorted({m["sender"] for m in messages})
    start = messages[0]["ts"]
    end = messages[-1]["ts"]
    hard = [q for q in queries if q["hard"]]
    bad = [q for q in hard if not q["zero_overlap"]]
    meta = {
        "seed": SEED,
        "n_messages": len(messages),
        "n_people": len(people),
        "people": people,
        "start": start,
        "end": end,
        "n_queries": len(queries),
        "n_hard": len(hard),
        "hard_zero_overlap_ok": not bad,
        "failed_hard": bad,
        "tags_used_in_queries": sorted({q["gold_id"] for q in queries}),
    }
    (DATA / "corpus_meta.json").write_text(json.dumps(meta, indent=2))
    print(json.dumps(meta, indent=2))
    if bad:
        raise SystemExit(f"hard queries leaked overlap: {bad}")
    if len(messages) < 4000:
        raise SystemExit(f"need >=4000 messages, got {len(messages)}")
    if len(people) < 8:
        raise SystemExit("need 8 participants")
    if len(queries) != 40:
        raise SystemExit(f"need 40 queries, got {len(queries)}")


def main() -> None:
    messages, queries = generate()
    write_outputs(messages, queries)


if __name__ == "__main__":
    main()
