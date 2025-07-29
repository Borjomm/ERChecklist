// main.c
#include <stdio.h>
#include "parser.h"

// --- Test Configuration ---
// !!! IMPORTANT: CHANGE THIS TO THE PATH OF YOUR .sl2 FILE !!!
const char* SAVE_FILE_PATH = "D:\\Python\\save_parser\\after.sl2";
const int CHARACTER_SLOT_TO_TEST = 0; // Test with the first character slot

int main() {
    printf("--- C Parser Test Harness ---\n");

    // 1. Call the main parsing function
    printf("Parsing save file: %s for character slot %d\n", SAVE_FILE_PATH, CHARACTER_SLOT_TO_TEST);
    int result = update_character_data(SAVE_FILE_PATH, CHARACTER_SLOT_TO_TEST, 0);

    if (result != 0) {
        printf("Parsing failed with error code: %d\n", result);
        return 1; // Exit with an error
    }

    printf("Parsing successful.\n");

    // 2. Get the pointer to the populated global struct
    struct CharacterData* parsed_data = get_character_data_ptr();

    // 3. Write the contents of the struct to an output file
    const char* output_filename = "parsed_data.bin";
    FILE* output_file = fopen(output_filename, "wb");
    if (output_file == NULL) {
        perror("Error opening output file");
        return 1;
    }

    printf("Writing parsed data to %s...\n", output_filename);
    size_t bytes_written = fwrite(parsed_data, 1, sizeof(struct CharacterData), output_file);
    fclose(output_file);

    if (bytes_written != sizeof(struct CharacterData)) {
        printf("Error: Failed to write the full struct to the file. Wrote %zu bytes.\n", bytes_written);
        return 1;
    }

    printf("Successfully wrote %zu bytes.\n", bytes_written);
    printf("Test complete. You can now inspect '%s' with a hex editor.\n", output_filename);

    return 0; // Success
}