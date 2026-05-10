# simple music visualiser in CPuth
# that captures speaker output
# and displays it in a pygame window

# how long has this been going on?

from typing import Any

import pygame as pg
import sounddevice as sd
import numpy as np


WN_W, WN_H = 800, 600
BAR_COUNT = 64
BAR_MAG_MULT = 200
BLOCK_SIZE = 1024

class AudioBuffer:
    def __init__(self):
        self.fft = np.zeros(BAR_COUNT)
        self.smooth_fft = np.zeros(BAR_COUNT)
        self.decay_rate = 0.6  # decay rate for smooth FFT

# yes this is a global
# yes global vars freaking suck
# but it's the only thing I can think of right now that would work
buf = AudioBuffer()

def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t

def lerp_colours(c1: tuple[int, int, int], c2: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    r1, g1, b1 = c1
    r2, g2, b2 = c2
    return (
        int(lerp(r1, r2, t)),
        int(lerp(g1, g2, t)),
        int(lerp(b1, b2, t))
    )

def find_blackhole_device():
    devices: list[dict[str, Any]] = sd.query_devices()

    for i, device in enumerate(devices):
        name = device.get("name", "unknown-device").lower()

        # dumb substring search but it works so oh well
        if "blackhole" in name and device["max_input_channels"] > 0:
            return i

    raise ValueError(
        "BlackHole device not found. "
        "Make sure BlackHole is installed and enabled in Audio MIDI Setup."
    )

def audio_callback(indata, frames, time, status) -> None:
    # It might look like those 4 args aren't used, but otherwise
    # something throws a TypeError and I have no idea why
    # We can't change the type signature.
    # Whatever, let's just leave them there

    global buf

    audio = indata[:, 0]

    print(f"in: {audio.shape}, max: {float(np.max(np.abs(audio))):.4f}")

    fft = np.abs(np.fft.rfft(audio))
    fft = fft[:len(fft) // 2]

    bins = np.array_split(fft, BAR_COUNT)
    latest_fft = np.array([b.mean() for b in bins])

    # This is the part where we update the buffer
    buf.fft = latest_fft
    buf.smooth_fft = buf.decay_rate * buf.smooth_fft + (1 - buf.decay_rate) * latest_fft

def draw_visualiser(buf: AudioBuffer, screen: pg.Surface) -> None:
    screen.fill((0, 0, 0))

    bar_w = WN_W // BAR_COUNT

    # Pulsing effect based on fft intensity
    energy = np.mean(buf.fft)
    pulse = min(255, int(energy * 255))
    screen.fill((pulse // 5, 0, pulse // 2))

    # Draw bars
    for i, mag in enumerate(buf.smooth_fft):
        h = int(np.log1p(mag) * BAR_MAG_MULT)

        colour = pg.Color(0)
        colour.hsva = (lerp(120, 210, i / BAR_COUNT), 60, 100, 100)
        pg.draw.rect(
            screen,
            colour,
            (i * bar_w, WN_H - h, bar_w - 2, h),
        )

    pg.display.flip()

def main():
    # XXX: make sure nothing else is outputting from BLACKHOLE_IDX
    # XXX: otherwise you get AUHAL -50. I don't f*cking know why

    global buf

    BLACKHOLE_IDX = find_blackhole_device()
    print(sd.query_devices(BLACKHOLE_IDX))  # DEBUG

    SAMPLE_RATE = 44100  # force stable mode

    pg.init()
    screen = pg.display.set_mode((WN_W, WN_H))
    pg.display.set_caption("CPuth Music Visualiser")
    clock = pg.time.Clock()

    stream = None

    try:
        stream = sd.InputStream(
            device=BLACKHOLE_IDX,
            channels=1,
            samplerate=SAMPLE_RATE,
            blocksize=BLOCK_SIZE,
            dtype="float32",
            callback=audio_callback,
            latency="low",
            clip_off=True,
            dither_off=True,
        )

        stream.start()

        running = True
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False

            draw_visualiser(buf=buf, screen=screen)
            pg.display.flip()
            clock.tick(60)

    finally:
        if stream:
            stream.stop()
            stream.close()
        pg.quit()

if __name__ == "__main__":
    main()
