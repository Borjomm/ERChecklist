import struct
from db import ITEM_DB # Assuming db.py contains your ITEM_DB dictionary

# =============================================================================
# CONSTANTS & DB (Same as your working script)
# =============================================================================
INVENTORY_ANCHOR_PATTERN = bytes([0xB0, 0xAD, 0x01, 0x00, 0x01, 0xFF, 0xFF, 0xFF])
INVENTORY_ANCHOR_OFFSET = len(INVENTORY_ANCHOR_PATTERN) + 8
INVENTORY_ANCHOR_PATTERN_DLC = bytes([0xB0, 0xAD, 0x01, 0x00, 0x01])
INVENTORY_ANCHOR_OFFSET_DLC = len(INVENTORY_ANCHOR_PATTERN_DLC) + 3
INVENTORY_END_PATTERN = bytes([0] * 50)
SLOT_OFFSETS = [
    (0x00000310, 0x00280310), (0x00280320, 0x0500320),
    (0x0500330, 0x0780330), (0x0780340, 0x0a00340),
    (0x0a00350, 0x0c80350), (0x0c80360, 0x0f00360),
    (0x0f00370, 0x1180370), (0x1180380, 0x1400380),
    (0x1400390, 0x168038f), (0x16803a0, 0x190039f + 1),
]
ITEM_IDS_SET = set(ITEM_DB.keys())

# =============================================================================
# --- YOUR PROVEN ITEM IDENTIFICATION PARSER (UNCHANGED) ---
# =============================================================================
def get_all_owned_items(save_file_path: str, profile_index: int) -> set:
    """
    Finds which items are owned by parsing the pattern-matched inventory list.
    This function is KNOWN TO BE CORRECT FOR IDENTIFICATION and will not be changed.
    """
    owned_ids = set()
    try:
        with open(save_file_path, 'rb') as f: save_data = f.read()
    except FileNotFoundError: return owned_ids
    start, end = SLOT_OFFSETS[profile_index]
    slot_data = save_data[start:end]
    inventory_start, is_dlc_file = -1, False
    index = slot_data.find(INVENTORY_ANCHOR_PATTERN)
    if index != -1: inventory_start = index + INVENTORY_ANCHOR_OFFSET
    else:
        index = slot_data.find(INVENTORY_ANCHOR_PATTERN_DLC)
        if index != -1: inventory_start = index + INVENTORY_ANCHOR_OFFSET_DLC; is_dlc_file = True
    if inventory_start == -1: return owned_ids
    inventory_end = slot_data.find(INVENTORY_END_PATTERN, inventory_start)
    if inventory_end == -1: return owned_ids
    inventory_end += 6
    raw_inventory_data = slot_data[inventory_start:inventory_end]
    chunk_size = 8 if is_dlc_file else 16
    item_chunks = [raw_inventory_data[i:i + chunk_size] for i in range(0, len(raw_inventory_data), chunk_size)]
    for chunk in item_chunks:
        if not chunk or len(chunk) < 4: continue
        raw_id = struct.unpack_from('<I', chunk, 0)[0]
        if raw_id == 0 or raw_id == 0xFFFFFFFF: continue
        category = raw_id & 0xF0000000
        true_item_id = -1
        if category == 0x00000000:
            found = False
            for base_id_unique in ITEM_IDS_SET:
                if base_id_unique % 10000 != 0 and (base_id_unique <= raw_id <= base_id_unique + 10):
                    true_item_id = base_id_unique; found = True; break
            if not found: true_item_id = (raw_id // 10000) * 10000
        elif category in [0x10000000, 0x20000000, 0x40000000, 0x80000000]:
            true_item_id = raw_id
        if true_item_id in ITEM_IDS_SET:
            owned_ids.add(true_item_id)
    return owned_ids

# =============================================================================
# --- NEW, SEPARATE FUNCTION TO BRUTE-FORCE FIND QUANTITIES ---
# =============================================================================
def get_true_quantities(save_file_path: str, profile_index: int, owned_ids_to_check: list) -> dict:
    """
    Given a set of owned ItemIDs, this function brute-force searches the save file
    for their corresponding handles to find their true quantities.
    """
    quantities = {}
    try:
        with open(save_file_path, 'rb') as f:
            save_data = f.read()
    except FileNotFoundError:
        return quantities

    start, end = SLOT_OFFSETS[profile_index]
    slot_data = save_data[start:end]

    for item_id in owned_ids_to_check:
        # We only need to do this for stackable items, others are quantity 1.
        category = item_id & 0xF0000000
        if category == 0x40000000: # "Goods" category
            
            # This is the handle generation logic we discovered from your hex diff.
            # It seems to be a combination of a mask and the lower bits of the ItemID.
            handle_to_find = 0xB0000000 | (item_id & 0x00FFFFFF)
            handle_pattern = struct.pack('<I', handle_to_find)

            # Search for this handle in the character data
            offset = slot_data.find(handle_pattern)
            
            if offset != -1:
                # The quantity is the 4 bytes immediately following the handle
                quantity_bytes = slot_data[offset + 4 : offset + 8]
                struct_bytes = slot_data[offset : offset + 12]
                print(f"Entry {handle_to_find:X}: {struct_bytes.hex(' ')}")
                quantity = struct.unpack('<I', quantity_bytes)[0]
                quantities[item_id] = quantity

    return quantities

# =============================================================================
# MAIN EXECUTION BLOCK
# =============================================================================
if __name__ == '__main__':
    save_path = 'after.sl2'
    character_slot = 0
    
    # Stage 1: Get the set of all owned items using our reliable parser.
    owned_item_ids = sorted(list(get_all_owned_items(save_path, character_slot)))
    
    # Stage 2: Get the dictionary of true quantities by searching for handles.
    item_quantities = get_true_quantities(save_path, character_slot, owned_item_ids)

    # Stage 3: Print the combined, final results.
    if owned_item_ids:
        print(f"SUCCESS: Found {len(owned_item_ids)} unique items from the database.")
        print("-" * 60)
        
        for item_id in owned_item_ids:
            item_name = ITEM_DB.get(item_id, "Unknown Item")
            # Get the real quantity from our new dictionary, defaulting to 1 if it's not a stackable.
            quantity = item_quantities.get(item_id, 1)
            print(f"  - {item_name:<40} (ID: 0x{item_id:X}, Quantity: {quantity})")
            
    else:
        print("Could not find any matching items in the save file.")