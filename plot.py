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
    global pending, aligned

    # Read available serial data
    data = ser.read(ser.in_waiting)

    if len(data) > 0:
        pending.extend(data)

    # The high byte of each 12-bit ADC sample is always 0 to 15.
    if not aligned and len(pending) >= 128:
        even_bytes_are_high = all(pending[i] <= 15 for i in range(0, 128, 2))
        odd_bytes_are_high = all(pending[i] <= 15 for i in range(1, 128, 2))

        if even_bytes_are_high:
            del pending[0]
            aligned = True
        elif odd_bytes_are_high:
            aligned = True

    # Process complete 2-byte samples
    count = len(pending) // 2 if aligned else 0

    if count > 0:
        usable = count * 2

        raw = np.frombuffer(
            pending[:usable], dtype='<u2'
        )

        voltage = raw * VREF / 4095
        samples.extend(voltage)

        del pending[:usable]

    # Update graph
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