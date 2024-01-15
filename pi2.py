# Pi 2 Script

import numpy as np
import matplotlib.pyplot as plt
import soundfile as sf
import serial
import time
import struct
from array import array

def generate_gold_sequence(first_polynomial, second_polynomial, sequence_length):
    first_shift_register = np.array([1] * (len(first_polynomial) - 1) + [0])
    second_shift_register = np.array([1] * (len(second_polynomial) - 1) + [0])
    gold_sequence = []
    for _ in range(sequence_length):
        chip = (first_shift_register[0] + second_shift_register[0]) % 2
        gold_sequence.append(chip)
        feedback = (first_shift_register[-1] + second_shift_register[0]) % 2
        first_shift_register = np.roll(first_shift_register, 1)
        first_shift_register[0] = feedback
        feedback = (second_shift_register[-1] + feedback) % 2
        second_shift_register = np.roll(second_shift_register, 1)
        second_shift_register[0] = feedback
    return gold_sequence

# UART configuration
uart_port = '/dev/ttyS0' # Can be changed according to the serial port.
uart_baudrate = 115200 # can be changed according to the requirements.

# Open UART Port.
uart = serial.Serial(uart_port, uart_baudrate)
modulated_signal = array('H', [])

print("Entering While Loop\n")
while True:
    if uart.in_waiting > 0:
        data_chunk = uart.read(2)
        value = struct.unpack('<H', data_chunk)[0]
        modulated_signal.extend(struct.pack('<H', value))
        time.sleep(0.00000001)
        print(modulated_signal)
        if uart.in_waiting <= 0:
            break

# with open("modulated_signal_1.wav", "wb") as file:
#    file.write(received_data)

uart.close()

modulated_array = np.array(modulated_signal)

# modulated_signal, _ = sf.read('modulated_signal_1.wav')

gold_sequence = generate_gold_sequence([1, 0, 1], [1, 1, 0], len(modulated_signal))

# Apply thresholding to demodulate the signal
threshold = 0.5
demodulated_signal = (modulated_array > threshold).astype(int)

# Calculate BER for the entire signal
ber = np.sum(demodulated_signal != gold_sequence) / len(gold_sequence)

plt.figure(figsize=(6, 6))

# Plot the modulated signal
plt.subplot(2, 1, 1)
plt.plot(modulated_signal[:1000], label='Modulated Signal')
plt.xlabel('Sample Number')  # Label X-axis
plt.ylabel('Modulated Amplitude')  # Label Y-axis
plt.title('Modulated Signal (Gold sequence CDMA)')
plt.legend()

# Plot the demodulated signal
plt.subplot(2, 1, 2)
plt.plot(demodulated_signal[:1000], label='Demodulated Signal')
plt.xlabel('Sample Number')  # Label X-axis
plt.ylabel('Demodulated Value')  # Label Y-axis
plt.title('Demodulated Signal')
plt.legend()

plt.tight_layout()
plt.show()
