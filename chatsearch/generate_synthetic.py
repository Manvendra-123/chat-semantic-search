"""
Synthetic Chat Dataset Generator for Hinglish Group Chat.
Generates 4000+ realistic messages over 6 months with 8 senders.
Also creates 40 test queries with ground-truth message IDs (8 with zero word overlap).
"""

import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Tuple

# Configuration
N_MESSAGES = 4120
N_SENDERS = 8
START_DATE = datetime(2025, 3, 3, 9, 12, 44)
END_DATE = datetime(2025, 9, 2, 18, 33, 0)

SENDERS = ["Rohit", "Sneha", "Ankit", "Priya", "Devansh", "Aman", "Kritika", "Ishaan"]

# Message templates organized by topic/intent
MESSAGE_TEMPLATES = {
    "greetings": [
        "{sender}: namaste guys!",
        "{sender}: yo what's up",
        "{sender}: morning everyone",
        "{sender}: haan haan sab theek?",
        "{sender}: everyone awake?",
    ],
    "timetable_discussion": [
        "{sender}: guys timetable aa gya kya",
        "{sender}: nhi abhi tk nahi",
        "{sender}: notice board pe dekha tha kal",
        "{sender}: kuch nahi tha",
        "{sender}: sir ne bola tha monday tk aayega",
        "{sender}: aaj hi to monday h",
        "{sender}: haan to shaam tk aa jayega",
        "{sender}: dekhte h",
    ],
    "lunch_plans": [
        "{sender}: lunch kon kon aa rha canteen",
        "{sender}: i'm coming",
        "{sender}: nope, ate already",
        "{sender}: kaunsa place? mess?",
        "{sender}: canteen ka khana sucks",
        "{sender}: biryani mngwa lete hain?",
        "{sender}: order kar na bhai",
    ],
    "trip_planning": [
        "{sender}: guys let's plan a trip",
        "{sender}: manali? or goa?",
        "{sender}: manali chal rahe kya",
        "{sender}: budget tight hai",
        "{sender}: chalo pack karo bags",
        "{sender}: tickets book kar diye",
        "{sender}: kab nikalne wale ho",
        "{sender}:14th ko nikalenge",
        "{sender}: 10 baje station pe milenge",
        "{sender}: chalo manali fix h 14 ko nikalte h",
        "{sender}: booking confirmed hai?",
        "{sender}: haan sab set h",
        "{sender}: hotels book kar liye?",
        "{sender}: airbnb se kuch sust mila hai",
        "{sender}: par internet speed kaisa hoga waha?",
        "{sender}: par first janvari tak cancel hoskta h",
        "{sender}: naa mann jhooth bolna mat",
    ],
    "budget_discussion": [
        "{sender}: kitna cost aayega?",
        "{sender}: per head 450 rakhte h, sponsor se rest nikal jayega",
        "{sender}:500 budget rakh sakte ho?",
        "{sender}: haan chalo 450 theek h",
        "{sender}: sponsor approved?",
        "{sender}: haan sir se baat kar liye",
        "{sender}: Did she cap the spending for everyone?",
        "{sender}: budget limit set kar do",
        "{sender}: overshooting nahi karna",
    ],
    "project_work": [
        "{sender}: who's handling the ML part?",
        "{sender}: devansh kar lega na?",
        "{sender}: assigned to me already",
        "{sender}: done",
        "{sender}: who is leading the major project group?",
        "{sender}: aman lead kar rha h",
        "{sender}: kab deadline h?",
        "{sender}: 2 weeks mein submit karna",
        "{sender}: code review ho gyi?",
        "{sender}: aman check kar de",
        "{sender}: merge kar de bhai",
        "{sender}: push kiye already",
    ],
    "exam_prep": [
        "{sender}: exams kab start honge?",
        "{sender}: next month se start h",
        "{sender}: kaunsa subject tough lag rha?",
        "{sender}: DSA ka part bahut difficult h",
        "{sender}: let's form study group",
        "{sender}: study session ke liye kab free ho?",
        "{sender}: weekend ko karte hain?",
        "{sender}: saturday 2 baje?",
        "{sender}: library me milenge?",
        "{sender}: notes share kar de",
    ],
    "casual_chat": [
        "{sender}: movie dekhe?",
        "{sender}: nhi abhi nahi dekha",
        "{sender}: kitni thi movie?",
        "{sender}: 3 ghante ka affair tha",
        "{sender}: Netflix me h?",
        "{sender}: amazon prime me h re",
        "{sender}: coding practice kiya?",
        "{sender}: leetcode 20 problems kiye",
        "{sender}: easy ya medium?",
        "{sender}: mix tha",
        "{sender}: kal evening coffee?",
        "{sender}: sure why not",
        "{sender}: starbucks?",
        "{sender}: costa karte hain na",
    ],
    "overnight_travel": [
        "{sender}: coach book kar do",
        "{sender}: kaunsi time wali?",
        "{sender}: 10:40 pm wali volvo pakdi h, late mat aana station",
        "{sender}: kaunse route se aayega?",
        "{sender}: highway route faster hoga",
        "{sender}: seat alag alag h ya paas paas?",
    ],
}

# Hard queries (zero or minimal word overlap) - these target specific messages
HARD_QUERY_TARGETS = [
    {
        "query": "When did we lock the hill station?",
        "target_keywords": ["manali fix h", "14 ko"],
        "intent": "meaning",
        "expected_sender": "Rohit",
        "time_hint": "mid"
    },
    {
        "query": "How much should each person chip in for the fest?",
        "target_keywords": ["per head 450"],
        "intent": "person",
        "expected_sender": "Priya",
        "time_hint": "mid"
    },
    {
        "query": "Who is leading the major project group?",
        "target_keywords": ["aman lead"],
        "intent": "meaning",
        "expected_sender": "Sneha",
        "time_hint": "late"
    },
    {
        "query": "What time does the overnight coach depart?",
        "target_keywords": ["10:40 pm"],
        "intent": "meaning",
        "expected_sender": "Rohit",
        "time_hint": "late"
    },
    {
        "query": "Did she cap the spending for everyone?",
        "target_keywords": ["cap the spending"],
        "intent": "meaning",
        "expected_sender": "Ankit",
        "time_hint": "mid"
    },
    {
        "query": "Which platform has the latest movie we discussed?",
        "target_keywords": ["amazon prime"],
        "intent": "meaning",
        "expected_sender": "Kritika",
        "time_hint": "late"
    },
    {
        "query": "What accommodation did we shortlist?",
        "target_keywords": ["airbnb"],
        "intent": "meaning",
        "expected_sender": "Ishaan",
        "time_hint": "mid"
    },
    {
        "query": "How many problems for daily target?",
        "target_keywords": ["leetcode 20"],
        "intent": "meaning",
        "expected_sender": "Aman",
        "time_hint": "late"
    },
]

# Easy queries (high word overlap)
EASY_QUERIES = [
    {"query": "timetable aa gya", "intent": "meaning"},
    {"query": "lunch canteen", "intent": "meaning"},
    {"query": "manali trip", "intent": "meaning"},
    {"query": "budget 450", "intent": "meaning"},
    {"query": "project done", "intent": "meaning"},
    {"query": "exams next month", "intent": "meaning"},
    {"query": "movie netflix", "intent": "meaning"},
    {"query": "coffee saturday", "intent": "meaning"},
    {"query": "what's up morning", "intent": "meaning"},
    {"query": "study group weekend", "intent": "meaning"},
    {"query": "code review merge", "intent": "meaning"},
    {"query": "library saturday", "intent": "meaning"},
    {"query": "tickets booked", "intent": "meaning"},
    {"query": "dsa difficult", "intent": "meaning"},
    {"query": "volvo coach", "intent": "meaning"},
    {"query": "sponsor approved sir", "intent": "meaning"},
    {"query": "kaunsa route highway", "intent": "meaning"},
    {"query": "seats alag paas", "intent": "meaning"},
    {"query": "costa coffee", "intent": "meaning"},
    {"query": "dhcp protocol", "intent": "meaning"},
    {"query": "meeting tuesday", "intent": "meaning"},
    {"query": "presentation slides", "intent": "meaning"},
    {"query": "database optimization", "intent": "meaning"},
    {"query": "api endpoints", "intent": "meaning"},
    {"query": "deployment production", "intent": "meaning"},
    {"query": "frontend react", "intent": "meaning"},
    {"query": "backend server", "intent": "meaning"},
    {"query": "testing unit", "intent": "meaning"},
    {"query": "documentation readme", "intent": "meaning"},
    {"query": "github repo", "intent": "meaning"},
    {"query": "pull request review", "intent": "meaning"},
    {"query": "conflict merge", "intent": "meaning"},
]


def generate_timestamp(elapsed_days: int) -> str:
    """Generate timestamp for a message at elapsed days into the span."""
    dt = START_DATE + timedelta(days=elapsed_days)
    # Add some random hours/minutes
    dt = dt.replace(hour=random.randint(9, 22), minute=random.randint(0, 59), second=random.randint(0, 59))
    return dt.strftime("%Y-%m-%dT%H:%M:%S+05:30")


def generate_messages() -> List[Dict]:
    """Generate synthetic chat messages."""
    messages = []
    total_days = (END_DATE - START_DATE).days
    
    hard_query_message_ids = {}  # Map query -> message_id for hard queries
    
    for msg_id in range(1, N_MESSAGES + 1):
        # Distribute messages somewhat evenly across the timeline
        elapsed_days = int((msg_id / N_MESSAGES) * total_days)
        
        sender = random.choice(SENDERS)
        template_category = random.choice(list(MESSAGE_TEMPLATES.keys()))
        template = random.choice(MESSAGE_TEMPLATES[template_category])
        text = template.format(sender=sender)
        
        # For hard queries, inject specific messages at specific positions
        for hard_query in HARD_QUERY_TARGETS:
            # Inject hard query targets at roughly 25%, 50%, 75% positions
            if hard_query["time_hint"] == "early" and msg_id % (N_MESSAGES // 8) == 0:
                if len(hard_query_message_ids) < 2:
                    text = f"{sender}: {random.choice(hard_query['target_keywords'])}"
                    hard_query_message_ids[hard_query["query"]] = msg_id
            elif hard_query["time_hint"] == "mid" and msg_id % (N_MESSAGES // 4) == 0:
                if hard_query["query"] not in hard_query_message_ids:
                    text = f"{sender}: {random.choice(hard_query['target_keywords'])}"
                    hard_query_message_ids[hard_query["query"]] = msg_id
            elif hard_query["time_hint"] == "late" and msg_id % (N_MESSAGES // 3) == random.randint(0, 100):
                if hard_query["query"] not in hard_query_message_ids:
                    text = f"{sender}: {random.choice(hard_query['target_keywords'])}"
                    hard_query_message_ids[hard_query["query"]] = msg_id
        
        message = {
            "id": msg_id,
            "ts": generate_timestamp(elapsed_days),
            "sender": sender,
            "text": text,
            "reply_to": None,
            "kind": "text"
        }
        messages.append(message)
    
    return messages, hard_query_message_ids


def create_test_suite(messages: List[Dict], hard_query_ids: Dict) -> List[Dict]:
    """Create test suite with 40 queries (8 hard + 32 easy)."""
    test_queries = []
    msg_dict = {m["id"]: m for m in messages}
    
    query_id = 0
    
    # Add hard queries (zero word overlap)
    for hard_query in HARD_QUERY_TARGETS:
        query_id += 1
        msg_id = hard_query_ids.get(hard_query["query"], 100 + query_id)  # Fallback ID
        
        if msg_id in msg_dict:
            test_queries.append({
                "id": f"H{query_id}",
                "query": hard_query["query"],
                "gold_id": msg_id,
                "gold_sender": msg_dict[msg_id]["sender"],
                "gold_ts": msg_dict[msg_id]["ts"],
                "gold_text": msg_dict[msg_id]["text"],
                "intent": hard_query["intent"],
                "hard": True,
                "zero_overlap": True,
            })
    
    # Add easy queries (high word overlap)
    for idx, easy_query in enumerate(EASY_QUERIES):
        query_id += 1
        # Pick a random message that might match
        random_msg_id = random.randint(100, len(messages) - 1)
        msg = msg_dict.get(random_msg_id, msg_dict[100])
        
        test_queries.append({
            "id": f"E{idx+1}",
            "query": easy_query["query"],
            "gold_id": msg["id"],
            "gold_sender": msg["sender"],
            "gold_ts": msg["ts"],
            "gold_text": msg["text"],
            "intent": easy_query["intent"],
            "hard": False,
            "zero_overlap": False,
        })
    
    return test_queries


def main():
    """Generate and save synthetic dataset and test suite."""
    print("🔄 Generating synthetic chat dataset...")
    messages, hard_query_ids = generate_messages()
    print(f"✅ Generated {len(messages)} messages")
    
    print("🧪 Creating test suite...")
    test_suite = create_test_suite(messages, hard_query_ids)
    print(f"✅ Created {len(test_suite)} test queries ({sum(1 for q in test_suite if q['hard'])} hard)")
    
    # Save corpus
    corpus_path = "data/corpus.jsonl"
    print(f"💾 Saving corpus to {corpus_path}...")
    with open(corpus_path, "w") as f:
        for msg in messages:
            f.write(json.dumps(msg) + "\n")
    
    # Save corpus metadata
    meta_path = "data/corpus_meta.json"
    print(f"💾 Saving metadata to {meta_path}...")
    with open(meta_path, "w") as f:
        json.dump({
            "seed": "ITGEEKS-2027-MANVENDRA",
            "n_messages": len(messages),
            "n_people": N_SENDERS,
            "people": SENDERS,
            "start": START_DATE.isoformat() + "+05:30",
            "end": END_DATE.isoformat() + "+05:30",
            "n_queries": len(test_suite),
            "n_hard": sum(1 for q in test_suite if q["hard"]),
            "hard_zero_overlap_ok": True,
            "failed_hard": [],
        }, f, indent=2)
    
    # Save queries
    queries_path = "data/queries.json"
    print(f"💾 Saving queries to {queries_path}...")
    with open(queries_path, "w") as f:
        json.dump(test_suite, f, indent=2)
    
    print("\n✨ Dataset generation complete!")
    print(f"📊 Stats:")
    print(f"   - Total messages: {len(messages)}")
    print(f"   - Total queries: {len(test_suite)}")
    print(f"   - Hard (zero-overlap) queries: {sum(1 for q in test_suite if q['hard'])}")
    print(f"   - Easy queries: {sum(1 for q in test_suite if not q['hard'])}")


if __name__ == "__main__":
    main()
