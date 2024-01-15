import numpy as np
import matplotlib.pyplot as plt
import soundfile as sf
import smbus2
import time

# Functions to generate Gold sequences and process CDMA signal
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

def calculate_ber(original_signal, received_signal):
    if len(original_signal) != len(received_signal):
        raise ValueError("Signal lengths must be the same for BER calculation.")

    num_bits = len(original_signal)
    num_errors = np.sum(original_signal != received_signal)
    ber = num_errors / num_bits
    return ber

# ADS1115 configuration
ADS1115_I2C_ADDRESS = 0x48
bus = smbus2.SMBus(1)
config = [0b11000000, 0b00000001]
bus.write_i2c_block_data(ADS1115_I2C_ADDRESS, 1, config)

# Number of samples to read from ADS1115
num_samples = 1000

# Read samples from ADS1115
ads1115_data = []
for _ in range(num_samples):
    # Read ADC value from ADS1115 (adjust channel as needed)
    data = bus.read_i2c_block_data(ADS1115_I2C_ADDRESS, 0, 2)
    adc_value = (data[0] << 8) + data[1]
    ads1115_data.append(adc_value)

# Close the I2C connection
bus.close()

# Set the threshold for binary conversion
threshold = 0.5  # Adjust this value based on your signal characteristics

# Convert ADS1115 data to binary PAM signal using the threshold
ads1115_signal = (np.array(ads1115_data) > threshold).astype(int)

# Make sure gold_sequence has the same length as ads1115_signal
gold_sequence = generate_gold_sequence([1, 0, 1], [1, 1, 0], len(ads1115_signal))

# Transmission through a noisy channel (no need to modify the gold sequence here)
noise_power = 0.001  # Adjust the noise power

# Process CDMA signal with the ADS1115 signal
received_signal = ads1115_signal + np.random.normal(0, np.sqrt(noise_power), len(ads1115_signal))

# Print intermediate results for debugging
print("Input Signal:", ads1115_signal)
print("Gold Sequence:", gold_sequence)
print("Received Signal:", received_signal)

# Decode the received signal using the gold sequence
decoded_signal = received_signal * gold_sequence

# Calculate BER for the entire signal
ber = calculate_ber(ads1115_signal, decoded_signal)

# Plot the input signal
plt.figure(figsize=(12, 8))
plt.subplot(3, 2, 1)
plt.plot(ads1115_signal[:1000], label='Input Signal')
plt.title('Input Signal')
plt.legend()

# Plot the Gold sequence CDMA processed signal
plt.subplot(3, 2, 2)
plt.plot(decoded_signal[:1000], label='Processed Signal')
plt.title('Processed Signal (Gold sequence CDMA)')
plt.legend()

# Plot the received signal
plt.subplot(3, 2, 3)
plt.plot(received_signal[:1000], label='Received Signal')
plt.title('Received Signal')
plt.legend()

# Print BER
print("Bit Error Rate (BER):", ber)

# Plot the BER
plt.subplot(3, 2, 4)
plt.bar(['BER'], [ber], color=['blue'])
plt.title('Bit Error Rate (BER)')

plt.tight_layout()
plt.show()