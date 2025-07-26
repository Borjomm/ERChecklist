import struct
import os

EVENT_FLAG_SIZE = 0x1BF99F

def receive_event_section(path, character_id):

    #print(f"\n--- Parsing file '{path}' ---")
    with open(path, 'rb') as f:
        data = f.read()
    iVar10 = 0x330 + (character_id * 0x280010)
    for _ in range(5120):
        item_id = struct.unpack_from('<I', data, iVar10+4)[0]
        category = item_id & 0xF0000000
        if category == 0:
            iVar10 += 0x15
        elif category == 0x10000000:
            iVar10 += 0x10
        else:
            iVar10 += 0x8

    #print(f"\n- The offset after the ga_items structure is {hex(iVar10)}")
    uVar11 = iVar10 + 0x94cc
    #print(f"- Adding 0x94cc, offset is now {hex(uVar11)}")
    items_1 = struct.unpack_from('<I', data, uVar11)[0]
    #print(f"- Number of items to skip - {items_1}")
    uVar11 += items_1 * 8 + 0x62EB
    #print(f"- Skipping {items_1} items, adding 0x62EB. Address is now {hex(uVar11)}")
    items_2 = struct.unpack_from('<I', data, uVar11)[0]
    #print(f"- Number of items to skip - {items_2}")76
    uVar11 += (items_2 * 4) + 0x1c641
    #print(f"- Skipping {items_2} items, adding 0x1C641. Address is now {hex(uVar11)}")
    event_flags_region_offset = struct.unpack_from('<I', data, uVar11)[0]
    #print(f"- Reading final relative offset from {hex(uVar11)}: {hex(event_flags_region_offset)}")
    event_flags_base_addr = uVar11 + event_flags_region_offset + 0x21
    #print(f"- Final Event Flag Base Address is {hex(event_flags_base_addr)}")
    return data[event_flags_base_addr:event_flags_base_addr+EVENT_FLAG_SIZE]

def evaluate_difference(data1:bytes, data2:bytes):
    i = 0
    bit_offsets = []
    for byte1, byte2 in zip(data1, data2):
        if byte1 != byte2:
            diff = byte1 ^ byte2
            differing_bits = [bit for bit in range(8) if diff & (1 << bit)]
            #print(f"Byte {hex(i)} differs:")
            #print(f"  data1: {byte1:08b}")
            #print(f"  data2: {byte2:08b}")
            #print(f"  Differing bits: {differing_bits}")
            bit_offsets.append([i*8+entry for entry in differing_bits])
        i+=1
    return bit_offsets

def compare(folder):

    # Get full paths to all files (not directories) and sort them
    file_paths = [os.path.join(folder, f) for f in os.listdir(folder)]
    # Print or use the list
    for path in file_paths:
        print(f"--- ANALYZING {path} ---\n")
        file1 = os.path.join(path, 'before.bin')
        file2 = os.path.join(path, 'after.bin')
        with open(file1, 'rb') as f:
            data1 = f.read()
        with open(file2, 'rb') as f:
            data2 = f.read()
        difference = evaluate_difference(data1, data2)
        result = ", ".join(str(x) for sublist in difference for x in sublist)
        print(f"Bit differences in savefiles {path}:\n{result}\n")

def extract_events(folder, save_name, slot):
    print(f"--- Extracting event flags from {save_name}.sl2 ---")
    path1 = save_name + "_before.sl2"
    path2 = save_name + "_after.sl2"
    path1 = os.path.join("graces", path1)
    path2 = os.path.join("graces", path2)
    pointer1 = receive_event_section(path1, slot)
    pointer2 = receive_event_section(path2, slot)
    base_path = os.path.join(folder, save_name)
    if save_name not in os.listdir(folder):
        os.makedirs(base_path)
    with open(f'{base_path}/before.bin', 'wb') as f:
        f.write(pointer1)
    with open(f'{base_path}/after.bin', 'wb') as f:
        f.write(pointer2)

if __name__ == "__main__":
    FOLDER = 'graces\processed'
    NEEDS_EXTRACTION = False
    if NEEDS_EXTRACTION:
        CHAR_SLOT = 1
        PATHS = ["grave", "first_step", "elle", "east_limgrave", "limgrave_lake"]
        for entry in PATHS:
            extract_events(FOLDER, entry, CHAR_SLOT)
    compare(FOLDER)