import json

with open('database/boss_table.json', 'r', encoding='utf-8') as f:
    lookup = json.load(f)

sorted_data = []

lookup = sorted(lookup, key = lambda x: (x['is_dlc'], x['region'], x['name']))

i = 10000
for entry in lookup:
    entry['boss_id'] = i
    sorted_data.append(entry)
    i += 1

with open('database/final_bosses.json', 'w', encoding='utf-8') as f:
    json.dump(sorted_data, f, indent=2)

