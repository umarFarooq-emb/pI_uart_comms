#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <fcntl.h>
#include <termios.h>
#include <unistd.h>
#include <sndfile.h>

// UART file descriptor
int uart_fd;
int umar;
// Function to initialize UART
void initializeUART();

// Function to transmit data over UART
void transmitData(const uint16_t *data, size_t size);

int main() {
    // Initialize UART
    initializeUART();

    // Read the .wav file
    SF_INFO sfInfo;
    sfInfo.format = 0;
    SNDFILE *sndFile = sf_open("modulated_signal.wav", SFM_READ, &sfInfo);
    if (!sndFile) {
        fprintf(stderr, "Error opening .wav file\n");
        return 1;
    }

    // Allocate memory to store the audio data
    uint16_t *audioData = malloc(sfInfo.frames * sizeof(uint16_t));
    if (!audioData) {
        fprintf(stderr, "Memory allocation error\n");
        sf_close(sndFile);
        return 1;
    }

    // Read the audio data from the .wav file
    sf_read_short(sndFile, audioData, sfInfo.frames);

    // Transmit the audio data over UART
    transmitData(audioData, sfInfo.frames);

    // Cleanup
    free(audioData);
    sf_close(sndFile);
    close(uart_fd);

    return 0;
}

void initializeUART() {
    // Open UART file descriptor
    uart_fd = open("/dev/ttyS0", O_RDWR | O_NOCTTY | O_NDELAY);
    if (uart_fd == -1) {
        perror("Error - Unable to open UART");
        exit(EXIT_FAILURE);
    }

    // Configure UART
    struct termios options;
    tcgetattr(uart_fd, &options);
    cfsetospeed(&options, B921600);
    cfsetispeed(&options, B921600);
    options.c_cflag |= (CLOCAL | CREAD);
    options.c_cflag &= ~PARENB;
    options.c_cflag &= ~CSTOPB;
    options.c_cflag &= ~CSIZE;
    options.c_cflag |= CS8;
    tcsetattr(uart_fd, TCSANOW, &options);
}

void transmitData(const uint16_t *data, size_t size) {
    for (size_t i = 0; i < size; i++) {
        // Break the 16-bit value into two bytes
        uint8_t byte1 = (uint8_t)(data[i] & 0xFF);
        uint8_t byte2 = (uint8_t)((data[i] >> 8) & 0xFF);

        // Transmit the bytes over UART
        ssize_t bytesRead1 = write(uart_fd, &byte1, 1);
        ssize_t bytesRead2 = write(uart_fd, &byte2, 1);
    }
}
