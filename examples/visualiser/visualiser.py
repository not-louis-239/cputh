# simple music visualiser in CPuth
# that captures speaker output
# and displays it in a pygame window

# you just want attention, you don't want my heart
# maybe you just hate the thought of me with someone new

from typing import Any

import pygame as pg
import sounddevice as sd
import numpy as np

WN_W, WN_H = 800, 600
BAR_COUNT = 64
BAR_MAG_MULT = 30
BLOCK_SIZE = 1024

PULSE_COLOUR_MARKERS: dict[int, tuple[int, int, int]] = {
    0: (0, 0, 0),
    500: (70, 0, 200),
    750: (140, 50, 250)
}
sorted_keys = sorted(PULSE_COLOUR_MARKERS.keys())

class Visualiser:
    DECAY_RATE = 0.4  # decay rate for smooth FFT
    RENDER_DECAY_RATE = 0.05  # decay rate for visual graph
    ALPHA_FADE = 36
    PEAK_FALL_RATE = 8
    HALF_H = WN_H // 2

    def __init__(self):
        self.fft = np.zeros(BAR_COUNT)
        self.smooth_fft = np.zeros(BAR_COUNT)
        self.peak_heights = np.zeros(BAR_COUNT)

        self.bg_surface = pg.Surface((WN_W, WN_H), pg.SRCALPHA)
        self.fg_surface = pg.Surface((WN_W, self.HALF_H), pg.SRCALPHA)

    def _pulse_intensity_to_colour(self, pulse_intensity: float) -> tuple[int, int, int]:
        # Handle boundaries
        if pulse_intensity <= sorted_keys[0]:
            return PULSE_COLOUR_MARKERS[sorted_keys[0]]
        if pulse_intensity >= sorted_keys[-1]:
            return PULSE_COLOUR_MARKERS[sorted_keys[-1]]

        # Find the two markers to interpolate between
        for i in range(len(sorted_keys) - 1):
            lower_bound = sorted_keys[i]
            upper_bound = sorted_keys[i + 1]

            if lower_bound <= pulse_intensity <= upper_bound:
                # Calculate the relative position (0.0 to 1.0) between markers
                t = (pulse_intensity - lower_bound) / (upper_bound - lower_bound)

                return lerp_colours(
                    PULSE_COLOUR_MARKERS[lower_bound],
                    PULSE_COLOUR_MARKERS[upper_bound],
                    t
                )

        return PULSE_COLOUR_MARKERS[sorted_keys[-1]]

    def _calc_bar_height(self, mag: float, i: int, graph_height: int) -> int:
        mag = mag * (i + 1)
        return min(int(np.log1p(mag) * BAR_MAG_MULT), graph_height - 1)

    def _update_peak_caps(self, fft: np.ndarray, graph_height: int) -> None:
        for i, mag in enumerate(fft):
            h = self._calc_bar_height(mag, i, graph_height)

            if h > self.peak_heights[i]:
                self.peak_heights[i] = h
            else:
                self.peak_heights[i] = max(h, self.peak_heights[i] - self.PEAK_FALL_RATE)

    def _draw_fft_graph(
            self, fft: np.ndarray, screen: pg.Surface,
            xy_topleft: tuple[int, int], xy_botright: tuple[int, int],
        ) -> None:
        min_x, min_y = xy_topleft
        max_x, max_y = xy_botright

        graph_width = max_x - min_x
        graph_height = max_y - min_y
        bar_w = graph_width / BAR_COUNT

        for i, mag in enumerate(fft):
            h = self._calc_bar_height(mag, i, graph_height)

            x = min_x + i * bar_w
            y = max_y - h

            colour = BAR_COLOURS[i]

            pg.draw.rect(screen, colour, (int(x), int(y), max(1, int(bar_w - 2)), int(h)))

    def _draw_peak_caps(
            self, screen: pg.Surface,
            xy_topleft: tuple[int, int], xy_botright: tuple[int, int],
        ) -> None:
        min_x, min_y = xy_topleft
        max_x, max_y = xy_botright

        graph_width = max_x - min_x
        graph_height = max_y - min_y
        bar_w = graph_width / BAR_COUNT
        cap_h = 4

        self._update_peak_caps(self.smooth_fft, graph_height)

        for i, peak_h in enumerate(self.peak_heights):
            x = min_x + i * bar_w
            y = max(min_y, max_y - int(peak_h) - cap_h)
            width = max(2, int(bar_w - 1))

            cl = BAR_COLOURS[i]
            base_colour = (cl.r, cl.g, cl.b)
            cap_colour = lerp_colours((255, 255, 255), base_colour, 0.35)

            pg.draw.rect(screen, cap_colour, (int(x), int(y), width, cap_h), border_radius=2)

    def update(self, new_fft: np.ndarray) -> None:
        self.smooth_fft = self.DECAY_RATE * new_fft + (1 - self.DECAY_RATE) * self.smooth_fft
        self.fft = new_fft

    def render(self, screen: pg.Surface):
        # Background pulse
        energy = np.mean(self.smooth_fft)
        pulse_intensity = int(np.log1p(energy) * 200)
        self.bg_surface.fill(self._pulse_intensity_to_colour(pulse_intensity))

        # Create a temporary work surface
        # We need to move the history to a temp surface to work on it
        temp_surface = self.fg_surface.copy()

        # Apply fade to history - we don't talk anymore, but the bars still do
        fade = pg.Surface((WN_W, self.HALF_H), pg.SRCALPHA)
        fade.fill((0, 0, 0, self.ALPHA_FADE))  # higher alpha value = shorter trails
        temp_surface.blit(fade, (0, 0), special_flags=pg.BLEND_RGBA_SUB)

        # Apply scale/zoom - more recent -> more attention
        scaled_w = int(WN_W * (1 - self.RENDER_DECAY_RATE))
        scaled_h = int(self.HALF_H * (1 - self.RENDER_DECAY_RATE))
        scaled = pg.transform.scale(temp_surface, (scaled_w, scaled_h))  # using pg.scale because pg.smoothscale creates ugly black smudges

        # Clear the main surface so we can then put back the history
        self.fg_surface.fill((0, 0, 0, 0))
        self.fg_surface.blit(
            scaled,
            ((WN_W - scaled_w) // 2, self.HALF_H - scaled_h)
        )

        # Draw the new bars on top of the clean surface
        self._draw_fft_graph(
            fft=self.smooth_fft,
            screen=self.fg_surface,
            xy_topleft=(0, 0),
            xy_botright=(WN_W, self.HALF_H),
        )

        cap_surface = pg.Surface((WN_W, self.HALF_H), pg.SRCALPHA)
        self._draw_peak_caps(cap_surface, (0, 0), (WN_W, self.HALF_H))

        # Tell me honestly - what is all this work without blitting?
        screen.blit(self.bg_surface, (0, 0))
        screen.blit(self.fg_surface, (0, 0))
        screen.blit(pg.transform.flip(self.fg_surface, False, True), (0, self.HALF_H))
        screen.blit(cap_surface, (0, 0))
        screen.blit(pg.transform.flip(cap_surface, False, True), (0, self.HALF_H))

# yes this is a global
# yes global vars freaking suck
# but it's the only thing I can think of right now that would work
buf = Visualiser()

def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t

# Compute bar colours once at startup to avoid wasteful computation
BAR_COLOURS: list[pg.Color] = []
for i in range(BAR_COUNT):
    c = pg.Color(0)
    c.hsva = (lerp(120, 210, i / BAR_COUNT), 60, 100, 100)
    BAR_COLOURS.append(c)

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

    raise RuntimeError(
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

    fft_data = np.abs(np.fft.rfft(audio))
    n_fft = len(fft_data)

    indices = np.geomspace(1, n_fft, BAR_COUNT + 1).astype(int)

    latest_fft = np.zeros(BAR_COUNT)
    for i in range(BAR_COUNT):
        start = indices[i]
        end = indices[i+1]

        if start == end:
            latest_fft[i] = fft_data[min(start, n_fft - 1)]
        else:
            latest_fft[i] = np.mean(fft_data[start:end])

    tilt = np.linspace(1, 6, BAR_COUNT)
    latest_fft *= tilt

    buf.update(new_fft=latest_fft)

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

            buf.render(screen=screen)
            pg.display.flip()
            clock.tick(60)

    finally:
        if stream:
            stream.stop()
            stream.close()
        pg.quit()

if __name__ == "__main__":
    main()
