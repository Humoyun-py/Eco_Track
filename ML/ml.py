import json
from difflib import SequenceMatcher

# === JSON fayldan variantlarni yuklash ===
with open("ML/eco_roots.json", "r", encoding="utf-8") as f:
    variants = json.load(f)

# === Matnni normallashtirish ===
def normalize(text: str):
    return text.lower().strip()

# === O‘xshashlikni % hisoblash ===
def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

# === Asosiy funksiya ===
def check_answer(user_answer: str):
    user_norm = normalize(user_answer)

    scores = []
    for variant in variants:
        score = similarity(user_norm, normalize(variant))
        scores.append((variant, score))

    # eng yaxshi mos kelgan javob
    best_match, best_score = max(scores, key=lambda x: x[1])

    return {
        "user_answer": user_answer,
        "best_match": best_match,
        "match_percent": round(best_score * 100, 2)
    }

# ======= TEST ========
user_input = input("Javobni kiriting: ")
result = check_answer(user_input)

print("\nNatija:")
print("Sizning javob:", result["user_answer"])
print("Eng yaqin javob:", result["best_match"])
print("O‘xshashlik foizi:", result["match_percent"], "%")
