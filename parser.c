#include "parser.h"

#define HEADER_SIZE 0x300
#define SAVE_SLOT_SIZE 0x280010
#define EVENT_FLAG_SIZE 0x1Bf99F
#define ITERATION_COUNT 5120
#define EXPECTED_FILE_SIZE 0x1BA03D0L
#define min(a, b) ((a) < (b) ? (a) : (b))

static struct CharacterData g_character_data;
static unsigned char initialized_headers = 0;

struct CharacterData* EXPORT get_character_data_ptr() {
    return &g_character_data;
}

void EXPORT invalidate_headers() {
    initialized_headers = 0;
}

unsigned char* calculate_ga_items_offset(unsigned char* offset) {
    unsigned int item_id;
    unsigned int category;
    for (int i = 0; i < ITERATION_COUNT; i++) {
        item_id = *(unsigned int*)(offset + 4);
        category = item_id & 0xF0000000;
        if (category == 0) {
            offset += 0x15;
        }
        else if (category == 0x10000000) {
            offset += 0x10;
        }
        else {
            offset += 0x8;
        }
    }
    return offset;
}

int initialize_headers(unsigned char* save_data_buffer, unsigned char* data_buffer) {
    unsigned int version_id;
    unsigned char* save_offset;
    save_data_buffer += HEADER_SIZE;
    for (int i = 0; i < 10; i++) {
        version_id = *(unsigned int*)(save_data_buffer+0x10);
        if (version_id != 0) {
            save_offset = calculate_ga_items_offset(save_data_buffer+0x30);
            // This is now the start of 'Player' field
            memcpy(data_buffer + (i * 0x24), save_offset+0x94, 0x20); // Copy character name
            wchar_t *name = (wchar_t *)(data_buffer + (i * 0x24));
            memcpy(data_buffer + (i * 0x24) + 0x20, save_offset+0x60, 0x4); // Copy level
        }
        save_data_buffer += SAVE_SLOT_SIZE;
    }
    return 0;
}

unsigned char* fill_ga_items(unsigned char* save_ptr, unsigned char* data_ptr) {
    unsigned char* data_offset = data_ptr + 0x4;
    unsigned int item_id;
    unsigned int category;
    int k = 0;
    for (int i = 0; i < ITERATION_COUNT; i++) {
        item_id = *(unsigned int*)(save_ptr + 4);
        if (item_id == 0x1AD80) {
            save_ptr += 0x15; // 1AD80 is a common id, but doesn't map to anything, so we skip it
        }
        else if (item_id == 0xFFFFFFFF) {
            save_ptr += 0x8;
        }
        else {
            memcpy(data_offset, save_ptr, 0x4); // This is ga_item_handle
            memcpy(data_offset+0x4, &item_id, 0x4);
            category = item_id & 0xF0000000;
            if (category == 0) {
                memcpy(data_offset+0x8, save_ptr+0x10, 0x4); //This is aow
                save_ptr += 0x15;
            }
            else if (category == 0x10000000) {
                save_ptr += 0x10;
            }
            else {
                save_ptr += 0x8;
            }
            data_offset += 0xC;
            k++;
        }
    }
    memcpy(data_ptr, &k, 0x4);
    return save_ptr;
}

void fill_player(unsigned char* save_ptr, unsigned char* data_ptr) {
    save_ptr += 0x8;
    memcpy(data_ptr, save_ptr, 0x18); // Health, Max health, Base max health, FP, Max FP, Base Max FP

    data_ptr += 0x18; // 24
    save_ptr += 0x1C; // 28

    memcpy(data_ptr, save_ptr, 0xC); // SP, Max SP, Base Max SP

    data_ptr += 0xC; // 12
    save_ptr += 0x10; // 16

    memcpy(data_ptr, save_ptr, 0x24); // Vigor, Mind, Endurance, Strength, Dexterity, Intelligence, Faith, Arcane, Humanity

    data_ptr += 0x24; // 36
    save_ptr += 0x2C; // 44

    memcpy(data_ptr, save_ptr, 0xC); // Level, Souls, Soulmemory

    data_ptr += 0xC;
    save_ptr += 0x30;

    memcpy(data_ptr, save_ptr, 0x24); // Character type int + characterName[16] wchar_t

    data_ptr += 0x24;
    save_ptr += 0x26;

    memcpy(data_ptr, save_ptr, 0x2); // Gender + Archetype

    data_ptr += 0x2;
    save_ptr += 0x4;

    memcpy(data_ptr, save_ptr, 0x2); // VoiceType + Gift

    data_ptr += 0x2;
    save_ptr += 0x4;

    memcpy(data_ptr, save_ptr, 0x2); // AdditionalTalismanSlotsCount, SummonSpiritLevel
    data_ptr += 0x2;
    save_ptr += 0x1A;

    memcpy(data_ptr, save_ptr, 0x1); //FurlCallingFingerOn

    data_ptr += 0x1;
    save_ptr += 0x2;

    memcpy(data_ptr, save_ptr, 0x1); // MatchmakingWeaponLvl

    data_ptr += 0x1;
    save_ptr += 0x4;

    memcpy(data_ptr, save_ptr, 0x1); // GreatRuneOn

    data_ptr += 0x1;
    save_ptr += 0x2;

    memcpy(data_ptr, save_ptr, 0x2); // MaxCrimsonFlaskCount, MaxCeruleanFlaskCount

    return;
}

void fill_equipment(unsigned char* save_ptr, unsigned char* data_ptr) {
    memcpy(data_ptr, save_ptr, 0x28); // Weapons and projectiles

    data_ptr += 0x28;
    save_ptr += 0x30;

    memcpy(data_ptr, save_ptr, 0x10); // Armor

    data_ptr += 0x10;
    save_ptr += 0x14;

    memcpy(data_ptr, save_ptr, 0x10); // Talismans (Fun fact, there is a fifth talisman slot in the savefile)
}

void fill_inventory(unsigned char* save_ptr, unsigned char* data_ptr, int max_iterations, int extra_items) {
    unsigned int item_amount = *(unsigned int*)(save_ptr) + extra_items;
    max_iterations = min(max_iterations, item_amount);
    memcpy(data_ptr, &item_amount, 0x4);
    save_ptr += 0x4, data_ptr += 0x4;
    for(int i=0; i<max_iterations; i++) {
        memcpy(data_ptr, save_ptr, 0x8);
        save_ptr += 0xC, data_ptr += 0x8;
    }
}

int skip_region(unsigned char* save_ptr, int segment_size) {
    unsigned int item_amount = *(unsigned int*)(save_ptr);
    // printf("Amount to skip, %d\n", item_amount);
    return 0x4 + (item_amount*segment_size);
}

void fill_allItems(unsigned char* save_ptr, unsigned char* data_ptr, int max_iterations) {
    unsigned int item_amount = *(unsigned int*)(save_ptr);
    max_iterations = min(max_iterations, item_amount);
    memcpy(data_ptr, save_ptr, 0x4);
    data_ptr += 0x4, save_ptr += 0x8;
    for(int i=0; i<max_iterations; i++) {
        memcpy(data_ptr, save_ptr, 0x4);
        save_ptr += 0x8, data_ptr += 0x4;
    }
}

int EXPORT update_character_data(const char* filepath, int slot_index, int header_mode) {
    unsigned char* data_ptr;
    // Read the savefile, make a local copy
    FILE* file = fopen(filepath, "rb");
    if (file == NULL) {
        perror("Error opening save file");
        return -1;
    }

    fseek(file, 0, SEEK_END);
    long file_size = ftell(file);
    fseek(file, 0, SEEK_SET);

    if(file_size != EXPECTED_FILE_SIZE) {
        printf("Error: Invalid save file size. Expected %ld bytes, but got %ld bytes", EXPECTED_FILE_SIZE, file_size);
        return -2;
    }

    unsigned char* static_save_ptr = (unsigned char*)malloc(file_size);
    if (static_save_ptr == NULL) {
        printf("Error allocating memory for save file.\n");
        return -3;
    }
    fread(static_save_ptr, 1, file_size, file);
    fclose(file);

    data_ptr = (unsigned char*)get_character_data_ptr();
    size_t data_offset = 0x0;
    unsigned char* save_ptr = static_save_ptr;

    // If it's the first time, load player names and levels
    if (initialized_headers == 0) {
        memset(&g_character_data, 0, sizeof(struct CharacterData));
        initialize_headers(save_ptr, data_ptr);
        initialized_headers = 1;
    }
    if (header_mode == 1) {
        return 1; // Headers initialized
    }

    save_ptr += HEADER_SIZE + (slot_index * SAVE_SLOT_SIZE); // Now we parse a single character
    data_ptr += 0x168;

    memcpy(data_ptr, save_ptr, 0x14); // Copy checksum and version

    save_ptr += 0x30;
    data_ptr += 0x14;

    save_ptr = fill_ga_items(save_ptr, data_ptr);
    data_ptr += 0xF004;

    fill_player(save_ptr, data_ptr);

    save_ptr += 0x34C; // Move to EquippedItemsGaItemHandles
    data_ptr += 0xA0;

    fill_equipment(save_ptr, data_ptr);

    save_ptr += 0x58;
    data_ptr += 0x48;

    fill_inventory(save_ptr, data_ptr, 2688, 1); // For some reason, there is always ONE BLANK ITEM in the middle of the inventory, which is not reflected in the game count (This is CommonItemsInventory)

    data_ptr += 0x5404;
    save_ptr += 0x7E04;
    fill_inventory(save_ptr, data_ptr, 384, 0); // KeyItemsInventory

    data_ptr += 0xC04;
    save_ptr += 0x1324; //Moving to the start of acquiredprojectiles

    save_ptr += skip_region(save_ptr, 0x8) + 0x1D7; // Storage Box
    fill_inventory(save_ptr, data_ptr, 1920, 1); // CommonItemsStorage. Idk if there is an extra item, I'll place it just to be safe

    data_ptr += 0x3C04;
    save_ptr += 0x5A04;

    fill_inventory(save_ptr, data_ptr, 128, 0); // KeyItemsStorage

    data_ptr += 0x404;
    save_ptr += 0x70C; // Moving to the start of UnlockedRegions

    save_ptr += skip_region(save_ptr, 0x4) + 0x10B1;

    fill_allItems(save_ptr, data_ptr, 7000); // All items, this will be used for the checklist

    data_ptr += 0x6D64;
    save_ptr += 0x1B993;

    memcpy(data_ptr, save_ptr, 0x4); // Total deaths

    save_ptr += 0x1A;
    data_ptr += 0x4;

    memcpy(data_ptr, save_ptr, EVENT_FLAG_SIZE); // Here we go with the data dump

    save_ptr += EVENT_FLAG_SIZE + 0x1;
    data_ptr += EVENT_FLAG_SIZE;

    save_ptr += skip_region(save_ptr, 0x1); //FieldArea
    save_ptr += skip_region(save_ptr, 0x1); //WorldArea
    save_ptr += skip_region(save_ptr, 0x1); //WorldGeom
    save_ptr += skip_region(save_ptr, 0x1); //WorldGeom2
    save_ptr += skip_region(save_ptr, 0x1); //RendMan

    save_ptr += 0x200A0;



    memcpy(data_ptr, save_ptr, 0x2); // DLC

    free(static_save_ptr);

    // printf("C Parser: Update complete for slot %d.\n", slot_index);
    return 0;
}

