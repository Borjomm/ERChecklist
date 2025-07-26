import struct
import json

# =============================================================================
# --- CONFIGURATION (User Input) ---
# =============================================================================
# IMPORTANT: Provide the path to your save file and the exact character name.
SAVE_FILE_PATH = 'after.sl2' # Example: 'borjom.sl2', 'oneshot.sl2', 'sanya.sl2'
CHARACTER_NAME = 'Oneshot'     # Example: 'Borjom', 'Oneshot', 'Sanya&co'
CHARACTER_SLOT = 0            # Character slot (0-9)

# =============================================================================
# --- CONSTANTS (Based ONLY on your hex analysis and observations) ---
# =============================================================================
# Standard save file offsets and block sizes.
SAVE_HEADER_SIZE = 0x300
SLOT_SIZE = 0x280000 # Each character slot is 2.62 MB
SLOT_CHECKSUM_SIZE = 0x10 # The 16-byte checksum before each slot

# GA_ITEMS map structure.
GAITEM_MAP_OFFSET = 0x20 # Starts 0x20 bytes into the character data block
GAITEM_MAP_COUNT = 0x1400 # 5120 entries

# The magic offset YOU discovered: from the END of ga_items to the START of the character name.
# This implies that the 'PlayerGameData' struct starts at ga_items_end_offset - 4,
# and the name is 0x98 bytes into PlayerGameData. 0x98 - 4 = 0x94.
OFFSET_GAITEMS_END_TO_CHARACTER_NAME = 0x94 # 148 bytes

# The magic offset you discovered: from the START of the character name
# to the START of the main inventory list.
OFFSET_FROM_NAME_TO_INVENTORY_LIST = 0x314 # 0x314 bytes
#Total offset - 0x3a8 bytes


HELD_COMMON_ITEMS_CAPACITY = 2688
HELD_KEY_ITEMS_CAPACITY = 384     # 384 items

# =============================================================================
# --- RAW DATA DUMPER (Implementing your exact test instructions) ---
# =============================================================================

def dump_definitive_raw_data(save_file_path: str, character_name: str, profile_index: int):
    """
    Performs the definitive raw data dump based on the precise offsets
    discovered through your hex analysis.
    """
    print(f"\n--- Initiating Definitive Raw Data Dump for '{character_name}' in '{save_file_path}' ---")
    
    try:
        with open(save_file_path, 'rb') as f:
            save_data = f.read()
    except FileNotFoundError:
        print(f"ERROR: Save file not found at '{save_file_path}'.")
        return

    # 1. Locate character data block's start
    slot_start_absolute = SAVE_HEADER_SIZE + (profile_index * (SLOT_SIZE + SLOT_CHECKSUM_SIZE))
    character_data_start_absolute = slot_start_absolute + SLOT_CHECKSUM_SIZE
    
    # 2. Calculate the end of the `ga_items` map (Point A)
    current_offset_in_gaitems = character_data_start_absolute + GAITEM_MAP_OFFSET
    inventory_dict = {}
    for i in range(GAITEM_MAP_COUNT):
        entry_start_offset = current_offset_in_gaitems # Store start for unpack_from
        try:
            _handle, item_id = struct.unpack_from('<II', save_data, entry_start_offset) # Read from entry_start_offset
            
            bytes_to_skip = 8 # Default size for gaitem_handle + item_id

            # Determine additional bytes to skip based on category
            # This logic must correctly *advance* the current_offset_in_gaitems pointer
            # whether you store the data or not.
            category = item_id & 0xF0000000
            weapon = category == 0x00000000
            armor = category == 0x10000000
            
            if weapon:
                bytes_to_skip += 13 # Additional fields: unk2, unk3, aow_gaitem_handle, unk5
            elif armor:
                bytes_to_skip += 8  # Additional fields: unk2, unk3

            # --- CRITICAL CHANGE HERE ---
            # Only add to dictionary if it's a "real" item (not 0 or FFFFFFFF)
            if item_id != 0 and item_id != 0xFFFFFFFF:
                entry_data = {"gaitem_handle": hex(_handle), "item_id": hex(item_id)}
                
                # Read additional fields *relative to entry_start_offset*
                if armor or weapon:
                    unk_2 = struct.unpack("<I", save_data[entry_start_offset+8:entry_start_offset+12])[0]
                    unk_3 = struct.unpack("<I", save_data[entry_start_offset+12:entry_start_offset+16])[0]
                    entry_data["unk2"] = hex(unk_2)
                    entry_data["unk3"] = hex(unk_3)
                if weapon:
                    aow_gaitem_handle = struct.unpack("<I", save_data[entry_start_offset+16:entry_start_offset+20])[0]
                    unk_5 = struct.unpack("<B", save_data[entry_start_offset+20:entry_start_offset+21])[0]
                    entry_data["aow_gaitem_handle"] = hex(aow_gaitem_handle)
                    entry_data["unk5"] = hex(unk_5)
                
                # Store the parsed meaningful entry
                inventory_dict[i] = entry_data

            # ALWAYS advance the offset by the correct number of bytes for the current entry's type
            current_offset_in_gaitems += bytes_to_skip

        except struct.error as e:
            print(f"WARNING: Struct unpacking error at GA_ITEMS entry {i} (offset {hex(entry_start_offset)}): {e}. Stopping GA_ITEMS parsing.")
            break
        except IndexError:
            print(f"WARNING: Reached end of save data prematurely while parsing GA_ITEMS map at entry {i}.")
            break
            
    ga_items_end_offset = current_offset_in_gaitems
    print(f"\nCalculated end of ga_items map (Point A): {hex(ga_items_end_offset)}")

    # 3. Calculate expected character name offset and dump 32 bytes RAW (hex and UTF-16)
    expected_char_name_start_absolute = ga_items_end_offset + OFFSET_GAITEMS_END_TO_CHARACTER_NAME
    
    print(f"\n--- Dumping 32 bytes RAW at offset {hex(expected_char_name_start_absolute)} (ga_items_end_offset + 0x94) ---")
    try:
        raw_bytes_char_name_area = save_data[expected_char_name_start_absolute : expected_char_name_start_absolute + 32]
        print(f"RAW HEX: {raw_bytes_char_name_area.hex(' ')}")
        try:
            # Attempt to decode as UTF-16-LE
            decoded_string = raw_bytes_char_name_area.decode('utf-16-le').split('\x00')[0]
            print(f"UTF-16 String (first part): '{decoded_string}'")
        except UnicodeDecodeError:
            print(f"UTF-16 String: (Cannot decode this segment as UTF-16)")
    except IndexError:
        print(f"ERROR: Cannot read 32 bytes at offset {hex(expected_char_name_start_absolute)}. Out of bounds.")

    # 4. Find the character name's actual start offset via search (for the next jump)
    name_pattern_bytes = character_name.encode('utf-16-le')
    slot_data_for_search = save_data[character_data_start_absolute : character_data_start_absolute + SLOT_SIZE]
    
    name_offset_relative_to_character_data_start = slot_data_for_search.find(name_pattern_bytes)
    if name_offset_relative_to_character_data_start == -1:
        print(f"\nERROR: Character name '{character_name}' not found in save slot {profile_index} (for actual jump).")
        return
    character_name_absolute_start_offset = character_data_start_absolute + name_offset_relative_to_character_data_start
    print(f"\nFound actual character name at absolute offset: {hex(character_name_absolute_start_offset)}")

    # 5. Calculate the start of the inventory (character_name_absolute_start_offset + 788)
    held_inventory_start_absolute = character_name_absolute_start_offset + OFFSET_FROM_NAME_TO_INVENTORY_LIST
    print(f"\nCalculated start of inventory (EquipInventoryData): {hex(held_inventory_start_absolute)}")

    # 6. Dump the first 3 entries of 12 bytes RAW from the inventory start
    print(f"\n--- Dumping first 3 entries (12 bytes each) RAW from inventory start ({hex(held_inventory_start_absolute)}) ---")
    current_inventory_dump_offset = held_inventory_start_absolute
    
    for i in range(HELD_COMMON_ITEMS_CAPACITY): # Dump 3 entries of 12 bytes
        try:
            entry_bytes = save_data[current_inventory_dump_offset : current_inventory_dump_offset + 12]
            id_int = struct.unpack("<I", entry_bytes[0:4])[0]
            quantity_int = struct.unpack("<I", entry_bytes[4:8])[0]

            if id_int != 0:
                inventory_dict[i+GAITEM_MAP_COUNT] = {
                    "common_id": hex(id_int),  # Still display as hex if you want
                    "number": quantity_int
                }
            current_inventory_dump_offset += 12
        except IndexError:
            print(f"ERROR: Cannot read entry {i+1}. Out of bounds. Only {i} entries found.")
            break
    current_inventory_dump_offset += 4
    for i in range(HELD_KEY_ITEMS_CAPACITY): # Dump 3 entries of 12 bytes
        try:
            entry_bytes = save_data[current_inventory_dump_offset : current_inventory_dump_offset + 12]
            id_int = struct.unpack("<I", entry_bytes[0:4])[0]
            quantity_int = struct.unpack("<I", entry_bytes[4:8])[0]

            if id_int != 0:
                inventory_dict[i+GAITEM_MAP_COUNT+HELD_COMMON_ITEMS_CAPACITY] = {
                    "key_id": hex(id_int),  # Still display as hex if you want
                    "number": quantity_int
                }
            current_inventory_dump_offset += 12
        except IndexError:
            print(f"ERROR: Cannot read entry {i+1}. Out of bounds. Only {i} entries found.")
            break
    print("\n--- Raw Data Dump Complete ---")
    return inventory_dict

# =============================================================================
# --- MAIN EXECUTION ---
# =============================================================================
if __name__ == '__main__':
    inventory_dict = dump_definitive_raw_data(SAVE_FILE_PATH, CHARACTER_NAME, CHARACTER_SLOT)

    with open('output.json', 'w') as f:
        json.dump(inventory_dict, f, indent=2)