# Pi 1 Script

import numpy as np
import matplotlib.pyplot as plt
import soundfile as sf
import smbus2
import time
import serial

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

ADS1115_I2C_ADDRESS = 0x48
bus = smbus2.SMBus(1)
config = [0b11000000, 0b00000001]
bus.write_i2c_block_data(ADS1115_I2C_ADDRESS, 1, config)
uart_port = '/dev/ttyS0'
uart_baudrate = 115200

num_samples = 1000

ads1115_data = []
for _ in range(num_samples):
    data = bus.read_i2c_block_data(ADS1115_I2C_ADDRESS, 0, 2)
    adc_value = (data[0] << 8) + data[1]
    ads1115_data.append(adc_value)

bus.close()

threshold = 0.5

#ads1115_signal = (np.array(ads1115_data) > threshold).astype(int)

# Set parameters for the sinusoidal signal
frequency = 1.0  # Frequency of the sinusoid in Hz
amplitude = 0.5  # Amplitude of the sinusoid
sampling_rate = 1000  # Sampling rate in samples per second
duration = 2  # Duration of the signal in seconds

# Generate time values from 0 to duration with a step based on the sampling rate
time_values = np.arange(0, duration, 1/sampling_rate)

# Generate a sinusoidal waveform
sinusoidal_signal = amplitude * np.sin(2 * np.pi * frequency * time_values)

# Apply thresholding to create the binary signal
threshold = 0.0  # Set your threshold value
ads1115_signal = (sinusoidal_signal > threshold).astype(int)

gold_sequence = generate_gold_sequence([1, 0, 1], [1, 1, 0], len(ads1115_signal))

noise_power = 0.001

modulated_signal = ads1115_signal * gold_sequence + np.random.normal(0, np.sqrt(noise_power), len(ads1115_signal))

uart = serial.Serial(uart_port, uart_baudrate)

for chunk in modulated_signal:
    uart.write(chunk)
    time.sleep(0.00000001)

uart.close()

print("uart closed")

plt.figure(figsize=(7, 7))
plt.subplot(2, 1, 1)
plt.plot(ads1115_signal[:1000], label='Input Signal')
plt.title('Input Signal')
plt.xlabel('Sample Number')  # Label X-axis
plt.ylabel('ADC Value')     # Label Y-axis
plt.legend()

plt.subplot(2, 1, 2)
plt.plot(modulated_signal[:1000], label='Modulated Signal')
plt.xlabel('Sample Number')  # Label X-axis
plt.ylabel('Modulated Amplitude')  # Label Y-axis
plt.title('Modulated Signal (Gold sequence CDMA)')
plt.legend()

sf.write('modulated_signal.wav', modulated_signal, 44100)
plt.tight_layout()
plt.show()
