import struct
from db import ITEM_DB

# =============================================================================
# CONSTANTS & DATABASE (Corrected based on your 788-byte finding)
# =============================================================================
SAVE_HEADER_SIZE, SLOT_SIZE, SLOT_CHECKSUM_SIZE = 0x300, 0x280000, 0x10
GAITEM_MAP_OFFSET, GAITEM_MAP_COUNT = 0x20, 0x1400

# The definitive magic offset YOU discovered: from the START of the character name
# to the START of the EquipInventoryData block.
OFFSET_FROM_NAME_TO_INVENTORY = 788 # 0x314 bytes. This is the direct, empirical link.

# The fixed size of the held inventory block, used to find the storage box.
HELD_INVENTORY_BLOCK_SIZE = 0x10840 # From Rust source (size of EquipInventoryData)

ITEM_IDS_SET = set(ITEM_DB.keys())

# =============================================================================
# THE DEFINITIVE PARSER (Using your 788-byte offset)
# =============================================================================

def get_inventory_from_structure(save_file_path: str, profile_index: int, character_name: str) -> dict:
    """
    Parses an Elden Ring save file using the definitive structural model
    discovered through collaborative analysis and hex diffing, leveraging the
    empirically proven 788-byte offset from the character name.
    """
    owned_items = {}
    try:
        with open(save_file_path, 'rb') as f:
            save_data = f.read()
    except FileNotFoundError:
        print(f"Error: Save file not found at '{save_file_path}'")
        return owned_items

    # --- Step 1: Locate character data block ---
    slot_start = SAVE_HEADER_SIZE + (profile_index * (SLOT_SIZE + SLOT_CHECKSUM_SIZE))
    data_start = slot_start + SLOT_CHECKSUM_SIZE
    
    # --- Step 2: Parse `ga_items` to build handle->id map (needed for equipment lookups) ---
    # This part is essential for correctly identifying unique equipment.
    handle_to_id_map = {}
    current_offset_in_gaitems = data_start + GAITEM_MAP_OFFSET
    
    for _ in range(GAITEM_MAP_COUNT):
        try:
            handle, item_id = struct.unpack_from('<II', save_data, current_offset_in_gaitems)
            bytes_to_skip = 8 # Base size of ga_item entry
            if item_id != 0 and handle != 0xFFFFFFFF:
                handle_to_id_map[handle] = item_id
                category = item_id & 0xF0000000
                if category == 0x00000000: bytes_to_skip += 13 # Weapon
                elif category == 0x10000000: bytes_to_skip += 8 # Armor
            current_offset_in_gaitems += bytes_to_skip
        except struct.error:
            break 
    
    # --- Step 3: Find the character name to get our robust anchor point ---
    name_pattern = character_name.encode('utf-16-le')
    slot_data_bytes = save_data[data_start : data_start + SLOT_SIZE] # Limit search to character slot
    
    name_offset_relative_to_slot = slot_data_bytes.find(name_pattern)
    if name_offset_relative_to_slot == -1:
        print(f"Error: Character name '{character_name}' not found in save slot {profile_index}.")
        return owned_items
    
    # The absolute offset of the character name's START
    character_name_absolute_start_offset = data_start + name_offset_relative_to_slot

    # --- Step 4: Calculate the precise start of the EquipInventoryData block ---
    # This is the direct jump from the character name using the 788-byte offset YOU discovered.
    held_inventory_start = character_name_absolute_start_offset + OFFSET_FROM_NAME_TO_INVENTORY
    
    # The storage box is at a fixed offset from the start of the held inventory block.
    storage_inventory_start = held_inventory_start + HELD_INVENTORY_BLOCK_SIZE

    # --- Step 5: Parse both the Held and Storage inventory blocks ---
    inventories_to_parse = [
        ("Held", held_inventory_start, 2688, 384),    # Offset, Common Slots, Key Slots (sizes from Rust)
        ("Storage", storage_inventory_start, 1920, 128) # Offset, Common Slots, Key Slots (sizes from Rust)
    ]
    
    for inv_name, inv_start, common_slots, key_slots in inventories_to_parse:
        # A: Parse Common Items
        offset = inv_start + 4 # Skip initial 4-byte metadata count
        for _ in range(common_slots): # Loop a fixed number of times as per structure
            try:
                handle, quantity, _ = struct.unpack_from('<III', save_data, offset)
                offset += 12 # Move to next 12-byte entry
                if handle == 0 or quantity == 0: continue

                true_item_id = -1
                
                # Logic to convert handle to true ItemID
                if handle in handle_to_id_map: # Unique equipment (Weapon, Armor, AoW)
                    item_id_with_upgrade = handle_to_id_map[handle]
                    category = item_id_with_upgrade & 0xF0000000
                    if category == 0x00000000: # Weapon
                        base_id_found = False
                        for base_id in ITEM_IDS_SET:
                            if base_id % 10000 != 0 and (base_id <= item_id_with_upgrade <= base_id + 10):
                                true_item_id = base_id; base_id_found = True; break
                        if not base_id_found: true_item_id = (item_id_with_upgrade // 10000) * 10000
                    else: # Armor, AoW
                        true_item_id = item_id_with_upgrade
                else: # Stackable items (Talisman or Good) - handle is an embedded ID
                    category = handle & 0xF0000000
                    if category in [0xA0000000, 0xB0000000]: # Talisman or Good
                        true_item_id = handle ^ category

                if true_item_id in ITEM_IDS_SET:
                    owned_items[true_item_id] = owned_items.get(true_item_id, 0) + quantity
            except struct.error: 
                # This often means we've hit the end of the file within a fixed-size loop.
                # It's expected for sparsely populated inventories.
                break 

        # B: Parse Key Items (separate fixed-size list within EquipInventoryData)
        # Offset here is relative to the START of the current inventory block.
        # This is (4 bytes count) + (common_slots * 12 bytes per item) + (4 bytes key_item_count)
        offset = inv_start + 4 + (common_slots * 12) + 4
        for _ in range(key_slots): # Loop a fixed number of times
            try:
                handle, quantity, _ = struct.unpack_from('<III', save_data, offset)
                offset += 12
                if handle == 0 or quantity == 0: continue
                
                # Key item handles are also embedded IDs, with an additional unmasking.
                true_item_id = (handle ^ 0xB0000000) ^ 0x40000000 
                if true_item_id in ITEM_IDS_SET:
                    owned_items[true_item_id] = owned_items.get(true_item_id, 0) + quantity
            except struct.error: 
                # End of file or block hit.
                break 
            
    return owned_items

# =============================================================================
# EXAMPLE USAGE
# =============================================================================
if __name__ == '__main__':
    # You MUST provide the correct character name for this parser to work.
    # Make sure 'Borjom' or 'Oneshot' is your active character in the save file.
    
    save_file_path = 'borjom.sl2' # Or 'oneshot.sl2', 'sanya.sl2', 'pure.sl2'
    character_name = 'Borjom' # The exact character name in that save file
    character_slot = 0 # The slot the character is in

    all_owned_items = get_inventory_from_structure(save_file_path, character_slot, character_name)

    if all_owned_items:
        print(f"SUCCESS: Found {len(all_owned_items)} unique items with quantities from the true inventory structure.")
        print("-" * 60)
        for item_id, quantity in sorted(all_owned_items.items()):
            item_name = ITEM_DB.get(item_id, "Unknown Item")
            print(f"  - {item_name:<40} (ID: 0x{item_id:X}, Quantity: {quantity})")
    else:
        print("Could not find any matching items using the structural parsing method.")