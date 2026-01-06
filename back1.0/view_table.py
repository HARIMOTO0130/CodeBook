import json

with open('table_structures.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("authtoken_token表结构:")
print(json.dumps(data['authtoken_token'], ensure_ascii=False, indent=2))
