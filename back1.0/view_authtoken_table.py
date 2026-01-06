import json

with open('table_structures.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

authtoken_table = data.get('authtoken_token', {})
print(json.dumps(authtoken_table, indent=2, ensure_ascii=False))