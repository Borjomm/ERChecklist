import struct
from typing import Dict, Set, Tuple
# Assuming ITEM_DB and CATEGORY_MASK, etc. are imported or defined globally as in your project
import json
# =============================================================================
# --- CONSTANTS & DB (Re-include for standalone test if needed) ---
# =============================================================================
SAVE_HEADER_SIZE = 0x300
SLOT_SIZE = 0x280000
SLOT_CHECKSUM_SIZE = 0x10

INVENTORY_ANCHOR_PATTERN = bytes([0xB0, 0xAD, 0x01, 0x00, 0x01, 0xFF, 0xFF, 0xFF])
INVENTORY_ANCHOR_OFFSET = len(INVENTORY_ANCHOR_PATTERN) + 8
INVENTORY_ANCHOR_PATTERN_DLC = bytes([0xB0, 0xAD, 0x01, 0x00, 0x01])
INVENTORY_ANCHOR_OFFSET_DLC = len(INVENTORY_ANCHOR_PATTERN_DLC) + 3
INVENTORY_END_PATTERN = bytes([0] * 50)

# These SLOT_OFFSETS are for direct slice access within the save file
SLOT_OFFSETS = [
    (0x00000310, 0x00280310), (0x00280320, 0x0500320),
    (0x0500330, 0x0780330), (0x0780340, 0x0a00340),
    (0x0a00350, 0x0c80350), (0x0c80360, 0x0f00360),
    (0x0f00370, 0x1180370), (0x1180380, 0x1400380),
    (0x1400390, 0x168038f), (0x16803a0, 0x190039f + 1),
]

CATEGORY_MASK = 0xF0000000
CATEGORY_WEAPON = 0x00000000
CATEGORY_ARMOR = 0x10000000
CATEGORY_ACCESSORY = 0x20000000
CATEGORY_GOODS = 0x40000000
CATEGORY_AOW = 0x80000000

with open('util/item_dict.json', 'r', encoding='utf-8') as f:
        data = json.load(f) 

# Placeholder ITEM_DB for testing, use your full DB in actual project

ITEM_IDS_SET = set(int(entry, 16) for entry in data.keys())

# =============================================================================
# --- Utility for Raw ID (for `getIdReversed` if needed, but using direct unpack) ---
# =============================================================================
def getIdReversed(id_bytes):
    """Converts a 4-byte little-endian ID to a big-endian hex string."""
    return ''.join([f'{byte:02X}' for byte in id_bytes[:4][::-1]])

def subfinder(mylist, pattern):
    """Simple byte pattern finder."""
    for i in range(len(mylist) - len(pattern) + 1):
        if mylist[i:i+len(pattern)] == pattern:
            return i
    return -1

# =============================================================================
# --- MODIFIED ITEM IDENTIFICATION PARSER ---
# =============================================================================

def get_all_owned_items_and_details(save_file_path: str, profile_index: int) -> Tuple[Set[int], Dict[int, Dict[str, str]]]:
    """
    Finds which items are owned and returns detailed parsed information for each entry.

    Returns:
        A tuple:
        - Set[int]: Set of owned true_item_ids.
        - Dict[int, Dict[str, str]]: Dictionary mapping entry index to parsed details.
                                     Details include 'raw_id', 'true_item_id', and
                                     'field_1', 'field_2', 'field_3' as hex strings,
                                     depending on chunk size.
    """
    owned_ids: Set[int] = set()
    detailed_entries: Dict[int, Dict[str, str]] = {} # New dict for parsed details

    try:
        with open(save_file_path, 'rb') as f:
            save_data = f.read()
    except FileNotFoundError:
        print(f"ERROR: Save file not found at '{save_file_path}'.")
        return owned_ids, detailed_entries

    start, end = SLOT_OFFSETS[profile_index]
    slot_data = save_data[start:end]

    inventory_start: int = -1
    is_dlc_file: bool = False

    # Find inventory start using patterns
    index = subfinder(slot_data, INVENTORY_ANCHOR_PATTERN)
    if index != -1:
        inventory_start = index + INVENTORY_ANCHOR_OFFSET
    else:
        index = subfinder(slot_data, INVENTORY_ANCHOR_PATTERN_DLC)
        if index != -1:
            inventory_start = index + INVENTORY_ANCHOR_OFFSET_DLC
            is_dlc_file = True

    if inventory_start == -1:
        print("ERROR: Inventory anchor pattern not found.")
        return owned_ids, detailed_entries

    # Find inventory end using null pattern
    inventory_end_relative = subfinder(slot_data[inventory_start:], INVENTORY_END_PATTERN)
    if inventory_end_relative == -1:
        print("ERROR: Inventory end pattern not found.")
        return owned_ids, detailed_entries
    
    inventory_end = inventory_start + inventory_end_relative + 6 # +6 bytes as per original logic

    raw_inventory_data = slot_data[inventory_start:inventory_end]
    chunk_size = 8 if is_dlc_file else 16
    
    # Split raw data into chunks
    item_chunks = [raw_inventory_data[i:i + chunk_size] for i in range(0, len(raw_inventory_data), chunk_size)]

    # Process each chunk
    for i, chunk in enumerate(item_chunks):
        if not chunk or len(chunk) < 4:
            # Skip malformed chunks or those too short to contain an ID
            continue

        # Initialize current entry details
        current_entry_details = {}

        try:
            # Parse raw_id (first 4 bytes)
            raw_id = struct.unpack_from('<I', chunk, 0)[0]
            current_entry_details['raw_id'] = f"0x{raw_id:08X}"

            if raw_id == 0 or raw_id == 0xFFFFFFFF:
                # Store empty entries for completeness if desired, but not as "owned"
                # If you want to skip these from the detailed_entries dict entirely:
                # continue
                current_entry_details['true_item_id'] = 'N/A (Empty)'
                # Store the fields even for empty entries if they exist
                if chunk_size == 16:
                    current_entry_details['field_1'] = hex(struct.unpack_from('<I', chunk, 4)[0])
                    current_entry_details['field_2'] = hex(struct.unpack_from('<I', chunk, 8)[0])
                    current_entry_details['field_3'] = hex(struct.unpack_from('<I', chunk, 12)[0])
                elif chunk_size == 8:
                    current_entry_details['field_1'] = hex(struct.unpack_from('<I', chunk, 4)[0])
                
                detailed_entries[i] = current_entry_details
                continue # Do not add to owned_ids set

            # Determine true_item_id based on category and heuristics
            category = raw_id & CATEGORY_MASK
            true_item_id = -1 # Default to -1 if no match found

            if category == CATEGORY_WEAPON: # Weapon (Category 0x0...)
                found_base_id = False
                for base_id_unique in ITEM_IDS_SET:
                    # Check if it's a weapon base ID and if raw_id is within a plausible range (base to base+10, assuming base % 10000 == 0)
                    # This implies Base IDs for weapons are often multiples of 10000.
                    if base_id_unique % 10000 == 0 and (base_id_unique <= raw_id <= base_id_unique + 9999): # Check within the whole 10000 range
                        true_item_id = base_id_unique
                        found_base_id = True
                        break
                if not found_base_id:
                    # Fallback for weapons if exact base+offset not found in ITEM_IDS_SET.
                    # This heuristic converts any weapon ID to its base form.
                    true_item_id = (raw_id // 10000) * 10000 
            elif category in [CATEGORY_ARMOR, CATEGORY_ACCESSORY, CATEGORY_GOODS, CATEGORY_AOW]:
                # For these categories, the raw_id is typically the true_item_id
                true_item_id = raw_id
            
            # Add to owned_ids set only if it matches an ID in ITEM_DB
            if true_item_id in ITEM_IDS_SET:
                owned_ids.add(true_item_id)
            else:
                current_entry_details['note'] = f"ID 0x{true_item_id:X} not found in ITEM_DB for identification."


            current_entry_details['true_item_id'] = f"0x{true_item_id:08X}"

            # Parse remaining fields based on chunk_size (GaItem2 structure)
            if chunk_size == 16:
                # GaItem2: id (4), unk (4), reinforce_type (4), unk1 (4)
                field_1, field_2, field_3 = struct.unpack_from('<III', chunk, 4)
                current_entry_details['field_1'] = hex(field_1) # likely unk or value
                current_entry_details['field_2'] = hex(field_2) # likely reinforce_type
                current_entry_details['field_3'] = hex(field_3) # likely unk1
            elif chunk_size == 8:
                # GaItem2 (DLC variant): id (4), unk (4)
                field_1 = struct.unpack_from('<I', chunk, 4)[0]
                current_entry_details['field_1'] = hex(field_1) # likely unk or value
            
            detailed_entries[i] = current_entry_details

        except struct.error as e:
            print(f"WARNING: Struct unpacking error in chunk {i} (length {len(chunk)} bytes): {e}. Skipping chunk.")
            continue # Continue to next chunk if this one fails
        except IndexError:
            print(f"WARNING: Index out of bounds in chunk {i} (length {len(chunk)} bytes). Skipping chunk.")
            continue

    return owned_ids, detailed_entries

# =============================================================================
# --- MAIN EXECUTION BLOCK (for testing this function) ---
# =============================================================================
if __name__ == '__main__':
    # Assuming SAVE_FILE_PATH, CHARACTER_SLOT are defined globally or passed
    # Example usage:
    SAVE_FILE_PATH = 'after.sl2'
    CHARACTER_SLOT = 0

    owned_ids_set, detailed_inventory_dict = get_all_owned_items_and_details(SAVE_FILE_PATH, CHARACTER_SLOT)

    print("\n--- Owned Item IDs (from set) ---")
    for item_id in sorted(list(owned_ids_set)):
        print(f"  - 0x{item_id:X} ({data.get(item_id, 'Unknown Name')})")

    print("\n--- Detailed Inventory Entries (by original index) ---")
    import json # For pretty printing the dict
    print(json.dumps(detailed_inventory_dict, indent=2))

    print("\n--- Summary of GaItem2 Fields ---")
    for idx, entry in detailed_inventory_dict.items():
        raw_id_str = entry.get('raw_id', 'N/A')
        true_id_str = entry.get('true_item_id', 'N/A')
        field1_str = entry.get('field_1', 'N/A')
        field2_str = entry.get('field_2', 'N/A')
        field3_str = entry.get('field_3', 'N/A')

        item_name = data.get(true_id_str if true_id_str.startswith('0x') else 0, 'Unknown') if true_id_str != 'N/A (Empty)' else 'Empty/N/A'
        
        print(f"Index {idx:<4}: Raw ID: {raw_id_str:<10} | Name: {item_name:<40} | F1: {field1_str:<10} | F2: {field2_str:<10} | F3: {field3_str:<10}")