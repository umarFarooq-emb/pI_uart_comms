#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <fcntl.h>
#include <termios.h>
#include <unistd.h>
#include <sndfile.h>

// UART file descriptor
int uart_fd;

// Function to initialize UART
void initializeUART();

// Function to receive data over UART
size_t receiveData(uint16_t *data, size_t maxSize);

int main() {
    // Initialize UART
    initializeUART();

    // Buffer to store received audio data
    size_t bufferSize = 1000;  // Choose an appropriate size
    uint16_t *receivedData = malloc(bufferSize * sizeof(uint16_t));
    if (!receivedData) {
        fprintf(stderr, "Memory allocation error\n");
        close(uart_fd);
        return 1;
    }

    // Receive data over UART
    size_t receivedSize = receiveData(receivedData, bufferSize);

    // Write received data to a .wav file
    SF_INFO sfInfo;
    sfInfo.format = SF_FORMAT_WAV | SF_FORMAT_PCM_16;
    sfInfo.channels = 1;  // Adjust accordingly
    sfInfo.samplerate = 44100;  // Adjust accordingly

    SNDFILE *sndFile = sf_open("modulated_signal.wav", SFM_WRITE, &sfInfo);
    if (!sndFile) {
        fprintf(stderr, "Error opening .wav file for writing\n");
        free(receivedData);
        close(uart_fd);
        return 1;
    }

    sf_write_short(sndFile, receivedData, receivedSize);

    // Cleanup
    free(receivedData);
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

size_t receiveData(uint16_t *data, size_t maxSize) {
    size_t bytesRead = 0;

    while (1) {
        if (bytesRead >= maxSize) {
            fprintf(stderr, "Received data exceeds buffer size\n");
            break;
        }

        uint8_t byte1, byte2;

        // Receive two bytes over UART
        ssize_t bytesRead1 = read(uart_fd, &byte1, 1);
        ssize_t bytesRead2 = read(uart_fd, &byte2, 1);

        if (bytesRead1 == 1 && bytesRead2 == 1) {
            // Combine bytes into a 16-bit value
            data[bytesRead] = (uint16_t)((byte2 << 8) | byte1);

            // Increment the number of bytes read
            bytesRead++;
        } else {
            // Break the loop if no more data is available
            // break;
        }
    }

    return bytesRead;
}

