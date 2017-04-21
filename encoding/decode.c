#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <unistd.h>

#define BUFFER_SIZE 256

/* decode:
 * 1001 -> 0
 * 0110 -> 1
 * else -> error
 *
 * only 4 valid combinations per byte:
 * 00 - 0x99
 * 01 - 0x96
 * 10 - 0x69
 * 11 - 0x66
 */

// Bit pattern for 4 possible 2 bit decoded states.
#define ENCODED_BYTE_ZERO  0x99
#define ENCODED_BYTE_ONE   0x96
#define ENCODED_BYTE_TWO   0x69
#define ENCODED_BYTE_THREE 0x66

static int decode(uint8_t * encoded, uint8_t * decoded)
{
	unsigned int idx = 0;
	// Bit positions for index 0->3: 6, 4, 2, 0
	unsigned int bit_pos = 6;

	// The bit index increments by 2 for each byte of encoded data
	for (idx = 0; idx < 4; idx++) {
		// Decode byte into to 2 bits
		switch(encoded[idx]) {
		case ENCODED_BYTE_ZERO:
			// 0-initialized, no action required
			break;
		case ENCODED_BYTE_ONE:
			*decoded += 1<<bit_pos;
			break;
		case ENCODED_BYTE_TWO:
			*decoded += 2<<bit_pos;
			break;
		case ENCODED_BYTE_THREE:
			*decoded += 3<<bit_pos;
			break;
		default:
			return EXIT_FAILURE;
		}
		// Move on to the next input byte's bit position
		bit_pos -= 2;
		//printf("enc: 0x%x ", encoded[idx]);
	}
	//printf("byte: 0x%x / %c\n", *decoded, *decoded);
	return EXIT_SUCCESS;
}

int main(int argc, char* argv[]) {
	ssize_t bytes_read;
	ssize_t bytes_written;
	int ret = 0;

	// Input buffer (4 encoded bytes -> 1 decoded byte)
	uint8_t buffer[4] = {0,0,0,0};

	while ((bytes_read = read(STDIN_FILENO, &buffer, 4)) > 0){
		int i = 0;
		uint8_t byte_out = 0;

		// Ensure exactly 4 bytes were read or a byte cannot be decoded.
		if (bytes_read != 4){
			perror("Input read error");
			return EXIT_FAILURE;
		}

		// Decode the byte
		ret = decode(buffer, &byte_out);
		if (ret == EXIT_FAILURE) {
			perror("Invalid input error");
			return EXIT_FAILURE;
		}

		// 1 output byte per 4 input bytes
		bytes_written = write(STDOUT_FILENO, &byte_out, 1);
		if (bytes_written != 1){
			perror("Output write error");
			return EXIT_FAILURE;
		}
	}

	return EXIT_SUCCESS;
}
