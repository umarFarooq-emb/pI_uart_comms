import numpy as np
import matplotlib.pyplot as plt

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

# Number of samples for the sinusoidal signal
num_samples = 1000

# Generate a sinusoidal input signal
frequency = 1.0  # Adjust the frequency of the sinusoid
time_values = np.linspace(0, 1, num_samples, endpoint=False)
sinusoidal_signal = np.sin(2 * np.pi * frequency * time_values)

# Set the threshold for binary conversion
threshold = 0.5  # Adjust this value based on your signal characteristics

# Convert sinusoidal signal to binary PAM signal using the threshold
sinusoidal_binary_signal = (sinusoidal_signal > threshold).astype(int)

# Make sure gold_sequence has the same length as sinusoidal_binary_signal
gold_sequence = generate_gold_sequence([1, 0, 1], [1, 1, 0], len(sinusoidal_binary_signal))

# Transmission through a noisy channel
noise_power = 0.001  # Adjust the noise power

# Process CDMA signal with the sinusoidal binary signal
received_signal = sinusoidal_binary_signal + np.random.normal(0, np.sqrt(noise_power), len(sinusoidal_binary_signal))

# Print intermediate results for debugging
print("Input Signal:", sinusoidal_binary_signal)
print("Gold Sequence:", gold_sequence)
print("Received Signal:", received_signal)

# Decode the received signal using the gold sequence
decoded_signal = received_signal * gold_sequence

# Calculate BER for the entire signal
ber = calculate_ber(sinusoidal_binary_signal, decoded_signal)

# Plot the input signal
plt.figure(figsize=(12, 8))
plt.subplot(3, 2, 1)
plt.plot(sinusoidal_binary_signal, label='Input Signal (Sinusoidal)')
plt.title('Input Signal (Sinusoidal)')
plt.legend()

# Plot the Gold sequence CDMA processed signal
plt.subplot(3, 2, 2)
plt.plot(decoded_signal, label='Processed Signal')
plt.title('Processed Signal (Gold sequence CDMA)')
plt.legend()

# Plot the received signal
plt.subplot(3, 2, 3)
plt.plot(received_signal, label='Received Signal')
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
