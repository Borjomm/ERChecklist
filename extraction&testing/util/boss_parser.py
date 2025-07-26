import json

grace_list = []

with open('util/graces.txt', 'r', encoding='utf-8') as f:
    lines = f.read().splitlines()

for line_num, line in enumerate(lines):
    try:
        grace_id, grace_str = line.split(':', maxsplit=1)
    except ValueError as e:
        raise ValueError(f"Error in line {line_num}: {line}. {e}")
    grace_data = {
        "byte_offset": int(grace_id) // 8,
        "bit": int(grace_id) % 8,
        "name": grace_str
    }
    grace_list.append(grace_data)

with open('util/graces.json', 'w', encoding='utf-8') as f:
    json.dump(grace_list, f, indent=2)
