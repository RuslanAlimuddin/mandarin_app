import json

words = ["以", "现代", "大众", "大学", "美德", "比", "率", "红",
         "上", "新", "加", "哈", "单", "保", "签", "佛", "扬", "头条"]

with open("data/app_words.json", encoding="utf-8") as f:
    data = json.load(f)

# sesuaikan struktur loop ini kalau app_words.json berupa dict bukan list
entries = [e for e in data if e.get("simplified") in words]

with open("18_words_extract.json", "w", encoding="utf-8") as f:
    json.dump(entries, f, ensure_ascii=False, indent=2)

print(f"Ditemukan {len(entries)} dari {len(words)} kata")