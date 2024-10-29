import pygame
import numpy as np

# Initialize Pygame and the mixer
pygame.init()

# Use pre_init to set mixer settings before pygame.init()
pygame.mixer.pre_init(frequency=44100, size=-16)

# Initialize the mixer
pygame.mixer.init()

# Verify mixer settings
mixer_frequency, mixer_format, mixer_channels = pygame.mixer.get_init()
print(f"Mixer settings: {mixer_frequency} Hz, format {mixer_format}, channels {mixer_channels}")

# Set up the display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Sonic Spectrum Visualizer')

# Generate frequencies for a series of minor chords below 1000 Hz
frequencies = []
root_freq = 55  # Starting base frequency, e.g., 55 Hz (A1)

# Define intervals for a minor chord
minor_third_ratio = 2 ** (3 / 12)
perfect_fifth_ratio = 2 ** (7 / 12)

while root_freq < 1000:
    # Add the minor chord frequencies: root, minor third, and perfect fifth
    frequencies.append(int(root_freq))  # Root
    frequencies.append(int(root_freq * minor_third_ratio))  # Minor third
    frequencies.append(int(root_freq * perfect_fifth_ratio))  # Perfect fifth
    
    # Move to the next octave (doubling the root frequency)
    root_freq *= 2

# Remove duplicates and ensure frequencies are in ascending order
frequencies = sorted(set(frequencies))
print("Frequencies:", frequencies)

# Audio settings
SAMPLE_RATE = mixer_frequency  # Use the mixer frequency
DURATION = 150                   # Seconds

# Generate time samples
t = np.linspace(0, DURATION, int(SAMPLE_RATE * DURATION), endpoint=False)

# Initialize the waveform
waveform = np.zeros_like(t)

# Generate and sum sine waves for each frequency
for freq in frequencies:
    waveform += np.sin(2 * np.pi * freq * t)

# Normalize the waveform to prevent clipping
waveform /= len(frequencies)

# Convert waveform to 16-bit signed integers
audio = np.int16(waveform * 32767)

# Replicate the mono signal into all channels
audio = np.tile(audio[:, np.newaxis], (1, mixer_channels))

# Create a Pygame Sound object from the numpy array
sound = pygame.sndarray.make_sound(audio)

# Play the sound
sound.play()

# Define the frequency range for visualization
MIN_FREQ = 20    # Minimum frequency (Hz)
MAX_FREQ = 1000  # Maximum frequency (Hz)

# Particle class for visualization
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.radius = np.random.randint(3, 7)
        self.color = color
        self.velocity = np.random.uniform(-1, 1), np.random.uniform(-0.5, -1)
    
    def update(self):
        vx, vy = self.velocity
        self.x += vx
        self.y += vy
        self.radius *= 0.98  # Shrink over time

    def draw(self, surface):
        if self.radius > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.radius))

# List to hold particles
particles = []

# Helper function to interpolate colors based on frequency
def get_color_from_frequency(normalized_freq):
    if normalized_freq < 0.2:
        # Purple to Blue
        return (128 + int(127 * normalized_freq / 0.2), 0, 255)
    elif normalized_freq < 0.4:
        # Blue to Green
        return (0, int(255 * (normalized_freq - 0.2) / 0.2), 255 - int(255 * (normalized_freq - 0.2) / 0.2))
    elif normalized_freq < 0.6:
        # Green to Yellow
        return (255, 255, int(255 * (0.6 - normalized_freq) / 0.2))
    elif normalized_freq < 0.8:
        # Yellow to Orange
        return (255, int(255 * (0.8 - normalized_freq) / 0.2), 0)
    else:
        # Orange to Red
        return (255, 0, int(255 * (1 - normalized_freq) / 0.2))

# Main loop variables
clock = pygame.time.Clock()
running = True

while running:
    clock.tick(60)  # Frame rate limit
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update and remove particles
    for particle in particles[:]:
        particle.update()
        if particle.radius <= 0:
            particles.remove(particle)

    # Spawn particles for each frequency
    for freq in frequencies:
        # Normalize frequency to a value between 0 and 1
        normalized_freq = np.clip((freq - MIN_FREQ) / (MAX_FREQ - MIN_FREQ), 0, 1)
        # Map normalized frequency to y-coordinate
        y = HEIGHT - normalized_freq * HEIGHT
        x = np.random.randint(0, WIDTH)

        # Get color based on frequency
        color = get_color_from_frequency(normalized_freq)

        particles.append(Particle(x, y, color))

    # Clear the screen
    screen.fill((0, 0, 0))

    # Draw particles
    for particle in particles:
        particle.draw(screen)

    # Update the display
    pygame.display.flip()

# Clean up
pygame.quit()
