#include <string>

extern "C" __declspec(dllexport) int encode(char* input, char* output, unsigned int size);

int encode(char* input, char* output, unsigned int size) {
	int current_length = 0, cc = 0; // cc, current character
	char enc = 0x00;

	for (unsigned int i = 0; i < size; i++) {
		enc = (input[i] + 42) % 256; // Encode in the input character
		if (enc == 0x00 || enc == 0x0A || enc == 0x0D || enc == 0x3D) { // Check for illegal yenc characters and escape them
			output[cc] = 0x3D; // Add escape character for illegal character
			cc++;
			current_length += 1; // Can't have a line that is too long
			enc = (enc + 64) % 256; // Reencode data using modified algorithm
		}

		output[cc] = enc; // Output encoded data to output buffer
		cc++;
		current_length += 1; // Can't have a line that is too long

		if (current_length >= 127) { // New line because we don't want it to be too long
			output[cc] = char(0x0D);
			cc++;
			output[cc] = char(0x0A);
			cc++;
			current_length = 0; // Reset line length
		}
	}

	return cc;
}