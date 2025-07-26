import json
import struct

def parse_null_terminated_strings(binary_data: bytes, start_offset = 0x14001ab00, encoding='utf-8') -> dict[str, str]:
    parsed_dict = {}
    current_string_bytes = bytearray()

    just_passed_null = False
    entry_offset = start_offset
    for byte_val in binary_data:
        if byte_val == 0:
            if len(current_string_bytes) > 0:

                parsed_dict[hex(entry_offset)] = current_string_bytes.decode(encoding)
                current_string_bytes.clear() 
            just_passed_null = True
        else: 
            if just_passed_null:
                entry_offset = start_offset
            current_string_bytes.append(byte_val)
            just_passed_null = False
        start_offset += 1


    if len(current_string_bytes) > 0:
        parsed_dict[hex(entry_offset)] = current_string_bytes.decode(encoding)

    return parsed_dict

def parse_bytes_to_boss_items(binary_data: bytes, reference_dict: dict) -> list[dict]:
    final_list: list[dict] = []
    pointer = 0x00
    binary_len = len(binary_data)
    while pointer < binary_len:
        byte_offset, bit_offset = struct.unpack_from("<QB", binary_data, pointer)
        str_pointer = struct.unpack_from("<Q", binary_data, pointer+0x10)[0]
        is_remembrance, is_dlc = struct.unpack_from("<BB", binary_data, pointer+0x19)
        final_list.append({
            "byte_offset": hex(byte_offset),
            "bit": bit_offset,
            "name": reference_dict[hex(str_pointer)],
            "remembrance": bool(is_remembrance),
            "is_dlc": bool(is_dlc)
        })
        pointer += 0x20
    return final_list

with open('test_env/DATA_FIELD.bin', 'rb') as f:
    data = f.read()
dictionary = parse_null_terminated_strings(data)

with open('test_env/STRUCTS.bin', 'rb') as f:
    data = f.read()
info_list = parse_bytes_to_boss_items(data, dictionary)
with open('util/boss_data.json', 'w', encoding = "utf-8") as f:
    json.dump(info_list, f, indent=2)