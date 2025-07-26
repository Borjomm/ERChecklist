#TESTING FOR ID 76101
#BYTE_OFFSET = 0xcbe
#BIT = 2


import json

with open('graces.json', 'r', encoding='utf-8') as f:
    str_dict = json.load(f)

with open('util/event_map.json', 'r', encoding='utf-8') as f:
    event_map = json.load(f)

graces_list = []
for id, string in str_dict.items():
    entry_dict = event_map[id]
    entry_dict['id'] = id
    entry_dict['name'] = string
    graces_list.append(entry_dict)

with open('util/graces_map.json', 'w', encoding='utf-8') as f:
    json.dump(graces_list, f, indent=2)



