"""PC oscilloscope for MCI_HW2_UART firmware (marker nibble 0xA)."""

# run command: python3 plot.py /dev/ttyUSB0

import argparse
from collections import deque
from time import monotonic

import matplotlib.animation as animation
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import numpy as np
import serial

# Serial settings
PORT = '/dev/ttyUSB0'
BAUD = 230400
FS = 10000
VREF = 3.3

# Display settings
WINDOW = 2000

samples = deque(maxlen=WINDOW)
pending = bytearray()
aligned = False

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


def read_samples(ser):
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

    return bool(values)


def crossing_times(voltage, level):
    """Find midpoint crossing times in sample units, with interpolation."""
    before, after = voltage[:-1], voltage[1:]
    rising = np.flatnonzero((before < level) & (after >= level))
    falling = np.flatnonzero((before >= level) & (after < level))

    def interpolate(indices):
        return indices + (level - before[indices]) / (after[indices] - before[indices])

    return interpolate(rising), interpolate(falling)


def measure_timing(voltage, low, high, show_duty):
    # Ignore flat signals and swings of fewer than eight ADC counts.
    if high - low < 8 * VREF / 4095:
        return None, None, np.array([])

    rising, falling = crossing_times(voltage, (low + high) / 2)
    periods = np.diff(rising)
    if len(periods) < 2:
        return None, None, np.array([])

    typical = np.median(periods)
    if np.any(np.abs(periods - typical) > 0.20 * typical):
        return None, None, np.array([])

    period_ms = np.mean(periods) * 1000 / FS
    duty = None
    if show_duty:
        # A complete PWM cycle has one falling edge between two rising edges.
        widths = []
        for start, stop in zip(rising[:-1], rising[1:]):
            edges = falling[(falling > start) & (falling < stop)]
            if len(edges) == 1:
                widths.append((edges[0] - start) / (stop - start))
        if widths:
            duty = 100 * np.mean(widths)
    return period_ms, duty, rising



def show_scope(ser):
    background = '#0e1820'
    screen = '#080e13'
    muted = '#a7bcc8'
    ink = '#e6f2f8'
    yellow = '#f8dc62'
    teal = '#65e3ce'
    panel = '#1b2b36'
    selected = '#284b55'

    fig, ax = plt.subplots(figsize=(11.6, 6.4), facecolor=background)
    fig.canvas.manager.set_window_title('STM32 Digital Oscilloscope')
    fig.subplots_adjust(left=0.085, right=0.96, bottom=0.205, top=0.735)
    fig.text(0.085, 0.92, 'STM32 Digital Oscilloscope', color=ink,
             fontsize=22, weight='bold')
    fig.text(0.96, 0.925, f'{ser.port}  |  {FS / 1000:g} kS/s', color=muted,
             fontsize=10, ha='right')
    fig.text(0.085, 0.875, f'MEASUREMENTS  /  {WINDOW / FS * 1000:g} ms capture',
             color=muted, fontsize=9)

    labels = ('FREQUENCY', 'PERIOD', 'MIN', 'MAX', 'AVERAGE', 'PEAK TO PEAK', 'PWM DUTY')
    readouts = []
    for x, label in zip(np.linspace(0.085, 0.835, len(labels)), labels):
        fig.text(x, 0.826, label, color=muted, fontsize=9)
        readouts.append(fig.text(x, 0.773, '\u2014', color=yellow, fontsize=17,
                                 family='monospace', weight='bold'))

    ax.set_facecolor(screen)
    ax.set_xlabel('Time (ms)', color=muted)
    ax.set_ylabel('Voltage (V)', color=muted)
    ax.set_ylim(-0.06, VREF + 0.06)  # Keep traces at either ADC rail visible.
    ax.set_yticks(np.linspace(0, VREF, 7))
    ax.tick_params(colors=muted, length=0, pad=7)
    ax.grid(color='#2b3f49', linewidth=0.8)
    for spine in ax.spines.values():
        spine.set_color('#3b535f')
    line, = ax.plot([], [], color=yellow, linewidth=1.6)
    status = fig.text(0.96, 0.046, 'WAITING FOR SAMPLES', color=muted,
                      fontsize=9, ha='right')
    fig.text(0.085, 0.046, 'TIME SPAN', color=muted, fontsize=9)

    span_ms = 20
    paused = False
    show_duty = False
    displayed = np.array([])
    last_sample_time = None

    def draw_capture():
        if not len(displayed):
            return

        low, high = displayed.min(), displayed.max()
        period, duty, rising = measure_timing(displayed, low, high, show_duty)
        readings = (
            f'{1000 / period:.1f} Hz' if period is not None else '\u2014',
            f'{period:.2f} ms' if period is not None else '\u2014',
            f'{low:.2f} V', f'{high:.2f} V',
            f'{displayed.mean():.2f} V', f'{high - low:.2f} V',
            'Off' if not show_duty else f'{duty:.0f}%' if duty is not None else '\u2014',
        )
        for readout, reading in zip(readouts, readings):
            readout.set_text(reading)

        intervals = int(FS * span_ms / 1000)
        # Start a zoomed trace at a rising edge when a full span fits after it.
        starts = rising[rising + intervals <= len(displayed) - 1]
        if len(starts):
            start = starts[-1]
            first = int(np.floor(start))
            stop = int(np.ceil(start + intervals)) + 1
            x = (np.arange(first, stop) - start) * 1000 / FS
            line.set_data(x, displayed[first:stop])
        else:
            visible = displayed[-(intervals + 1):]
            x = span_ms + np.arange(1 - len(visible), 1) * 1000 / FS
            line.set_data(x, visible)

    def update(_frame):
        nonlocal displayed, last_sample_time

        if read_samples(ser):
            last_sample_time = monotonic()
            if not paused:
                displayed = np.array(samples)
                draw_capture()

        if paused:
            status.set_text('PAUSED')
            status.set_color(yellow)
        elif last_sample_time is None:
            status.set_text('WAITING FOR SAMPLES')
            status.set_color(muted)
        elif monotonic() - last_sample_time > 0.5:
            status.set_text('NO NEW SAMPLES')
            status.set_color(muted)
        else:
            status.set_text('LIVE')
            status.set_color(teal)

    def make_button(x, width, label):
        button = Button(fig.add_axes([x, 0.025, width, 0.065]), label,
                        color=panel, hovercolor=selected)
        button.label.set_color(ink)
        button.label.set_fontsize(10)
        for spine in button.ax.spines.values():
            spine.set_visible(False)
        return button

    time_buttons = {}

    def set_span(milliseconds):
        nonlocal span_ms
        span_ms = milliseconds
        ax.set_xlim(0, span_ms)
        ax.set_xticks(np.linspace(0, span_ms, 6))
        for span, button in time_buttons.items():
            button.color = selected if span == span_ms else panel
            button.ax.set_facecolor(button.color)
        draw_capture()
        fig.canvas.draw_idle()

    def toggle_pause(_event):
        nonlocal paused, displayed
        paused = not paused
        pause_button.label.set_text('Resume' if paused else 'Pause')
        if not paused:
            displayed = np.array(samples)
            draw_capture()
        fig.canvas.draw_idle()

    def toggle_duty(_event):
        nonlocal show_duty
        show_duty = not show_duty
        duty_button.label.set_text(f'PWM duty: {"on" if show_duty else "off"}')
        draw_capture()
        fig.canvas.draw_idle()

    for i, span in enumerate((10, 20, 50, 200)):
        button = make_button(0.173 + i * 0.075, 0.066, f'{span} ms')
        button.on_clicked(lambda event, milliseconds=span: set_span(milliseconds))
        time_buttons[span] = button

    pause_button = make_button(0.49, 0.09, 'Pause')
    pause_button.on_clicked(toggle_pause)
    duty_button = make_button(0.59, 0.127, 'PWM duty: off')
    duty_button.on_clicked(toggle_duty)
    set_span(span_ms)

    # Keep the animation and buttons alive until the window closes.
    live_plot = animation.FuncAnimation(fig, update, interval=30, cache_frame_data=False)
    plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plot the STM32 ADC stream over UART.')
    parser.add_argument('port', nargs='?', default=PORT, help='serial port (default: %(default)s)')
    args = parser.parse_args()
    with serial.Serial(args.port, BAUD, timeout=0) as ser:
        show_scope(ser)
