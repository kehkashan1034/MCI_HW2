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


def find_sample_alignment(data):
    # Each sample is two bytes; its high byte must have marker nibble 0xA.
    if len(data) < 64:
        return None

    for start in range(len(data) - 63):
        headers_match = all(
            (data[start + 2 * sample + 1] & 0xF0) == 0xA0
            for sample in range(32)
        )

        if headers_match:
            return start

    return None


def update(frame):
    global aligned

    # Read available serial data.
    data = ser.read(ser.in_waiting)
    if data:
        pending.extend(data)

    values = []

    while True:
        if not aligned:
            start = find_sample_alignment(pending)

            if start is None:
                # Keep a short tail so the next incoming bytes can complete a scan.
                if len(pending) > 4096:
                    del pending[:-63]
                break

            # Discard bytes before the first matching sample boundary.
            if start > 0:
                del pending[:start]

            aligned = True

        if len(pending) < 2:
            break

        low_byte = pending[0]
        high_byte = pending[1]

        if (high_byte & 0xF0) == 0xA0:
            sample = low_byte | ((high_byte & 0x0F) << 8)
            values.append(sample)
            del pending[:2]
        else:
            # A byte was lost. Scan the buffer again for a sample boundary.
            del pending[0]
            aligned = False

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