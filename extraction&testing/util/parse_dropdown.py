def parse_hex_string_file(file_path):
    result = {}

    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or ':' not in line:
                print(f"Skipping line {line_num}: '{line}' (invalid format)")
                continue

            try:
                key, name_part = line.split(':', 1)
                key = f"0x{int(key, 16):08X}"
                value = name_part.strip()
                result[key] = value
            except ValueError as e:
                print(f"Error parsing line {line_num}: '{line}' -> {e}")

    return result

# Example usage:
if __name__ == '__main__':
    parsed_data = parse_hex_string_file('util/table.txt')

    # Optional: Save to JSON
    import json
    with open('util/item_dict.json', 'w', encoding='utf-8') as f:
        json.dump(parsed_data, f, indent=2, ensure_ascii=False)

    print("Parsed data successfully.")