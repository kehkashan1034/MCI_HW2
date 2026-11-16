import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
import numpy as np

# Serial settings
PORT = '/dev/ttyUSB0'
BAUD = 230400
FS = 10000
VREF = 3.3

# Display settings
WINDOW = 2000

ser = serial.Serial(PORT, BAUD, timeout=0)

samples = deque([0] * WINDOW, maxlen=WINDOW)
pending = bytearray()
aligned = False

fig, ax = plt.subplots()
line, = ax.plot([], [], linewidth=1)

ax.set_title("STM32 Digital Oscilloscope")
ax.set_xlabel("Time (ms)")
ax.set_ylabel("Voltage (V)")
ax.set_ylim(0, 3.3)
ax.set_xlim(-WINDOW / FS * 1000, 0)
ax.grid(True)

time_axis = np.arange(-WINDOW, 0) / FS * 1000


def update(frame):
    global aligned

    # Read available serial data
    data = ser.read(ser.in_waiting)
    if data:
        pending.extend(data)

    # Find the high byte of each 12-bit sample.
    # Its value must be between 0 and 15.
    if not aligned and len(pending) >= 128:
        check_length = min(len(pending), 512)
        check_length -= check_length % 2

        even_bytes_are_high = all(
            pending[i] <= 15 for i in range(0, check_length, 2)
        )
        odd_bytes_are_high = all(
            pending[i] <= 15 for i in range(1, check_length, 2)
        )

        if even_bytes_are_high and not odd_bytes_are_high:
            # The first byte is a high byte, so discard it.
            del pending[0]
            aligned = True
        elif odd_bytes_are_high and not even_bytes_are_high:
            # The first byte is a low byte; sample pairs are aligned.
            aligned = True

    # Decode complete samples. If the byte order slips, realign.
    values = []

    while aligned and len(pending) >= 2:
        low_byte = pending[0]
        high_byte = pending[1]

        if high_byte <= 15:
            values.append(low_byte | (high_byte << 8))
            del pending[:2]
        else:
            # Shift by one byte and search for sample alignment again.
            del pending[0]
            aligned = False
            break

    if values:
        voltage = np.array(values) * VREF / 4095
        samples.extend(voltage)

    line.set_data(time_axis, list(samples))
    return line,


ani = animation.FuncAnimation(
    fig,
    update,
    interval=30,
    blit=True,
    cache_frame_data=False
)

plt.tight_layout()
plt.show()

ser.close()