#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <wchar.h>

#pragma pack(1)
struct CharHeader {
    char checksum[16];
    int version;
};

#pragma pack(1)
struct GaItemEntry { // 5120 of those, I chose to store as static 12byte structures to avoid dynamic size shenanigans that happen in the savefile //F000h bytes in total
    unsigned int gaHandle;
    unsigned int id;
    unsigned int aowId;
};

#pragma pack(1)
struct Player { // A0h bytes
    unsigned int health; // 4h
    unsigned int maxHealth; // 8h
    unsigned int baseMaxHealth; // Ch
    unsigned int FP; // 10
    unsigned int maxFP; // 14
    unsigned int baseMaxFP; // 18
    unsigned int SP; // 1C
    unsigned int maxSP; // 20
    unsigned int baseMaxSP; // 24
    unsigned int vigor; // 28
    unsigned int mind; // 2C
    unsigned int endurance; // 30
    unsigned int strength; // 34
    unsigned int dexterity; // 38
    unsigned int intelligence; // 3C
    unsigned int faith; // 40
    unsigned int arcane; // 44
    unsigned int humanity; // 48
    unsigned int level; // 4C
    unsigned int souls; // 50
    unsigned int soulMemory; // 54
    unsigned int characterType; // 58
    wchar_t characterName[16]; // 78
    unsigned char gender; // 79
    unsigned char archeType; // 7A
    unsigned char voiceType; // 7B
    unsigned char gift; // 7C
    unsigned char additionalTalismanSlotsCount; // 7D
    unsigned char summonSpiritLevel; // 7E
    unsigned char furlCallingFingerOn; // 7F
    unsigned char matchmakingWeaponLevel; // 80
    unsigned char greatRuneOn; // 81
    unsigned char maxCrimsonFlaskCount; // 82
    unsigned char maxCeruleanFlaskCount; //83
    unsigned char padding[29];
};

#pragma pack(1)
struct EquippedItemsGaHandles { // 48h bytes
    unsigned int leftHand1;
    unsigned int rightHand1;
    unsigned int leftHand2;
    unsigned int rightHand2;
    unsigned int leftHand3;
    unsigned int rightHand3;
    unsigned int arrows1;
    unsigned int bolts1;
    unsigned int arrows2;
    unsigned int bolts2;
    unsigned int head;
    unsigned int chest;
    unsigned int arms;
    unsigned int legs;
    unsigned int talisman1;
    unsigned int talisman2;
    unsigned int talisman3;
    unsigned int talisman4;
};

#pragma pack(1)
struct InventoryHeld { 
    unsigned int itemId;
    unsigned int quantity;
};

#pragma pack(1)
struct CharacterSelection {
    wchar_t characterName[16];
    unsigned int level;
};

#pragma pack(1)
struct CharacterData {
    struct CharacterSelection characterSelection[10]; // 168h
    struct CharHeader header; // 14h, 0x168 offset
    unsigned int gaItemCount; //4h, 0x17C
    struct GaItemEntry gaItemEntry[5120]; // F000h, 0x180 offset
    struct Player player; // A0h, F180 offset
    struct EquippedItemsGaHandles equippedItems; // 48h, 0xF220 offset
    unsigned int commonItemInventoryCount; // 4h, 0xF268 offset
    struct InventoryHeld commonItemsInventory[2688]; // 5400h, 0xF26C offset
    unsigned int keyItemInventoryCount; //4h, 0x1466C offset
    struct InventoryHeld keyItemsInventory[384]; // C00h, 0x14670 offset
    unsigned int commonItemStorageCount; //4h, 0x15270 offset
    struct InventoryHeld commonItemsStorage[1920]; // 3C00h, 0x15274 offset
    unsigned int keyItemStorageCount; //4h, 0x18E74 offset
    struct InventoryHeld keyItemsStorage[128]; // 400h, 0x18E78 offset
    unsigned int allItemsCount; //4h, 0x19278 offset
    unsigned int allItems[7000]; //6D60h, 0x1927C offset
    unsigned int totalDeathsCount; //4h, 0x1FFDC offset
    unsigned char EventFlags[1833375]; //1BF99Fh, 0x1FFE0 offset
    unsigned short dlc; //0x2, 0x1df97f offset
};

__declspec(dllexport) int update_character_data(const char* filepath, int slot_index, int header_mode);
__declspec(dllexport) struct CharacterData* get_character_data_ptr();
__declspec(dllexport) void invalidate_headers();

#ifdef _WIN32
    #define EXPORT __declspec(dllexport)
#else
    #define EXPORT
#endif

int EXPORT update_character_data(const char* filepath, int slot_index, int header_mode);

struct CharacterData* EXPORT get_character_data_ptr(void); // Added 'void' for C style correctness

void EXPORT invalidate_headers(void);