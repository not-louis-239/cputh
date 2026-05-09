# snek.cputh
# Pygame Snek game but it's in Charlie Puth lyrics, because it's funny lol

# Compile: bin/cputh snek.cputh snek.py

from __future__ import annotations

import random

import pygame as pg
from pygame.key import ScancodeWrapper

FPS = 60
BOARD_SIZE = 41
WN_SIZE = 820
TILE_SIZE = WN_SIZE // BOARD_SIZE
MOVEMENT_INTERVAL = 0.1

def random_board_pos() -> tuple[int, int]:
    x = random.randint(0, BOARD_SIZE - 1)
    y = random.randint(0, BOARD_SIZE - 1)
    return (x, y)

class Food:
    def __init__(self, pos: tuple[int, int]) -> None:
        self.pos = pos

    def overlaps(self, snake: Snek) -> bool:
        """Checks if the Food overlaps with any part of the Snake."""
        return self.pos in snake.parts

class Snek:
    def __init__(self, start_pos: tuple[int, int]) -> None:
        """Init method for Snek. Sets the starting position and initialises the movement direction and length."""
        self.movement_dir = 0  # 0 = north, 1 = east, 2 = south, 3 = west
        self.can_turn = True
        self.length = 1
        self.parts: list[tuple[int, int]] = [start_pos]

    def reset(self, start_pos: tuple[int, int]) -> None:
        """Resets the Snek to its starting position."""
        self.movement_dir = 0
        self.length = 1
        self.parts = [start_pos]

    def move_fwd(self) -> None:
        most_recent = self.parts[-1]
        rx, ry = most_recent

        if self.movement_dir == 0:
            part = (rx, ry - 1)
        if self.movement_dir == 1:
            part = (rx + 1, ry)
        if self.movement_dir == 2:
            part = (rx, ry + 1)
        if self.movement_dir == 3:
            part = (rx - 1, ry)

        self.parts.append(part)  # type: ignore
        if len(self.parts) > self.length:
            self.parts.pop(0) # Remove the oldest part of the snake

        self.can_turn = True

    @property
    def is_alive(self) -> bool:
        # If parts overlap -> dead
        total_parts = len(self.parts)
        unique_parts = len(set(self.parts))
        if total_parts != unique_parts:
            return False

        # If most recent part out of bounds -> dead
        most_recent = self.parts[-1]
        rx, ry = most_recent
        if (
            rx < 0
            or rx >= BOARD_SIZE
            or ry < 0
            or ry >= BOARD_SIZE
        ):
            return False

        return True

class Game:
    def __init__(self) -> None:
        board_centre = (BOARD_SIZE // 2, BOARD_SIZE // 2)
        self.snek = Snek(start_pos=board_centre)
        self.game_over = False
        self.movement_cooldown: float = MOVEMENT_INTERVAL
        self.foods: list[Food] = [Food(random_board_pos())]
        self.font = pg.font.SysFont("Helvetica", 28)

    def reset(self) -> None:
        board_centre = (BOARD_SIZE // 2, BOARD_SIZE // 2)
        self.snek.reset(board_centre)
        self.game_over = False
        self.movement_cooldown = MOVEMENT_INTERVAL
        self.foods = [Food(random_board_pos())]

    def get_valid_food_spawn(self, snek: Snek, foods: list[Food]) -> tuple[int, int]:
        retries = 1_000

        for _ in range(retries):
            pos = random_board_pos()
            if (
                pos not in [food.pos for food in foods]  # pos not in food.pos for food in foods
                and pos not in snek.parts  # and pos not in snek.parts
            ):
                return pos

        # If we can't find a valid position, just return the last attempt anyway
        return pos  # type: ignore

    def update(self, dt_s: float) -> None:
        if self.game_over:
            return

        # Move snek
        self.movement_cooldown -= dt_s
        if self.movement_cooldown <= 0:
            self.movement_cooldown += MOVEMENT_INTERVAL
            self.snek.move_fwd()

        # If snek overlaps food, respawn food and increase length of snake
        for food in self.foods:
            if self.snek.parts[-1] == food.pos:
                food.pos = self.get_valid_food_spawn(snek=self.snek, foods=self.foods)
                self.snek.length += 1

        if not self.snek.is_alive:
            self.game_over = True
            return

    def take_input(self, cur_pressed: ScancodeWrapper) -> None:
        if not self.snek.is_alive:
            if cur_pressed[pg.K_SPACE]:
                self.reset()
            return

        if not self.snek.can_turn:
            return

        # Using if..elif..elif..elif instead of multiple ifs
        # so that only one turn can be processed per function call

        # North
        if cur_pressed[pg.K_w]:
            if self.snek.movement_dir == 2:
                return
            self.snek.movement_dir = 0
            self.snek.can_turn = False

        # East
        elif cur_pressed[pg.K_d]:
            if self.snek.movement_dir == 3:
                return
            self.snek.movement_dir = 1
            self.snek.can_turn = False

        # South
        elif cur_pressed[pg.K_s]:
            if self.snek.movement_dir == 0:
                return
            self.snek.movement_dir = 2
            self.snek.can_turn = False

        # West
        elif cur_pressed[pg.K_a]:
            if self.snek.movement_dir == 1:
                return
            self.snek.movement_dir = 3
            self.snek.can_turn = False

    def draw(self, wn: pg.Surface) -> None:
        wn.fill((0, 0, 0))

        if not self.snek.is_alive:
            wn.fill((128, 0, 0))

        # Draw food then snek so the snek is on top
        for food in self.foods:
            food_rect = pg.Rect(food.pos[0] * TILE_SIZE, food.pos[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pg.draw.rect(wn, (255, 0, 0), food_rect)

        # Now draw the snek
        for part in self.snek.parts:
            part_rect = pg.Rect(part[0] * TILE_SIZE, part[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pg.draw.rect(wn, (0, 255, 0), part_rect)

        # Score text
        text = self.font.render(
            f"Score: {self.snek.length}",
            True,
            (255, 255, 255)
        )
        wn.blit(text, (30, 100))

        # Game over text
        if not self.snek.is_alive:
            text = self.font.render(
                "Game Over. Press Space to restart",
                True,
                (255, 255, 255)
            )
            wn.blit(text, (30, 30))

        # Tableflip!
        # (┛ಠ_ಠ)┛彡┻━┻
        pg.display.flip()

def main() -> None:
    pg.init()

    try:
        game = Game()
        clock = pg.time.Clock()
        wn = pg.display.set_mode((WN_SIZE, WN_SIZE))
        pg.display.set_caption("Snek Game in CPuth")

        while True:
            dt_s = clock.tick(FPS) / 1_000
            events = pg.event.get()
            keys = pg.key.get_pressed()

            for event in events:
                if event.type == pg.QUIT:
                    return

            game.take_input(keys)
            game.update(dt_s)
            game.draw(wn)

    except KeyboardInterrupt:
        print("Keyboard interrupt received. Exited.")

    pg.quit()

if __name__ == "__main__":
    main()
