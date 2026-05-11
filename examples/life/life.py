import random
from typing import Generator

import pygame as pg
import numpy as np

WN_W, WN_H = 1100, 848
SIM_W, SIM_H = 275, 212
FPS = 60

NEIGHBOUR_DIFFS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

def chance(p: float) -> bool:
    return random.random() < p

class Grid:
    def __init__(self, width: int, height: int):
        self.w, self.h = width, height
        self.paused = False
        # Create a random grid of 0s and 1s, then cast to lightswitch (bool)
        # Using NumPy arrays for maximum speed!!

        self.reset()

    def reset(self) -> None:
        self.cells = (np.random.random((self.h, self.w)) < 0.2).astype(np.uint8)
        self.paused = False

    def run_gen(self) -> None:
        # Sum up all 8 neighbors by shifting the entire array
        # This effectively "slides" the grid to align neighbors with the center cell
        nbrs = (
            np.roll(self.cells, (1, 1), axis=(0, 1)) + np.roll(self.cells, (1, 0), axis=(0, 1)) +
            np.roll(self.cells, (1, -1), axis=(0, 1)) + np.roll(self.cells, (0, 1), axis=(0, 1)) +
            np.roll(self.cells, (0, -1), axis=(0, 1)) + np.roll(self.cells, (-1, 1), axis=(0, 1)) +
            np.roll(self.cells, (-1, 0), axis=(0, 1)) + np.roll(self.cells, (-1, -1), axis=(0, 1))
        )

        # Apply Conway's rules to the entire array at once
        # Rule 1: A cell becomes/stays alive if it has 3 neighbors
        # Rule 2: A live cell stays alive if it has 2 neighbors
        birth = (nbrs == 3)
        survive = (self.cells == 1) & (nbrs == 2)

        self.cells = (birth | survive).astype(np.uint8)

    def update(self) -> None:
        if self.paused:
            return
        self.run_gen()

    def draw(self, scr: pg.Surface) -> None:
        pixels = (self.cells * 255).astype(np.uint32)
        rgb_pixels = (pixels << 16) | (pixels << 8) | pixels
        img_data = np.repeat(
            np.repeat(rgb_pixels, WN_W // self.w, axis=1),
            WN_H // self.h, axis=0
        )
        pg.surfarray.blit_array(scr, img_data.T)

def main():
    pg.init()
    screen = pg.display.set_mode((WN_W, WN_H))
    pg.display.set_caption("Conway's Game of Life in CPuth (R - Reset, Space - Pause/Unpause)")
    grid = Grid(SIM_W, SIM_H)
    clock = pg.time.Clock()

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return

            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    grid.paused = not grid.paused

                elif event.key == pg.K_r:
                    grid.reset()

        clock.tick(FPS)
        grid.update()
        grid.draw(screen)
        pg.display.flip()

if __name__ == "__main__":
    main()
