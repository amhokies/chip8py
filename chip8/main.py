"""
Hello
"""

import sys
import pygame
from pygame.locals import QUIT

from chip8 import Chip8


def main():
    """
    Main
    """
    # pygame.init()
    # screen = pygame.display.set_mode([640, 480])

    # clock = pygame.time.Clock()

    # for x_coord in range(0, 64):
    #     for y_coord in range(0, 48):
    #         for event in pygame.event.get():
    #             if event.type == QUIT:
    #                 pygame.quit()
    #                 sys.exit()

    #         screen.fill((0, 0, 0))
    #         draw_pixel(screen, x_coord, y_coord)

    #         pygame.display.update()

    #         clock.tick(60)
    #         print('FPS: {}'.format(clock.get_fps()))
    chip8 = Chip8()


def draw_pixel(screen, x_pixel, y_pixel):
    """
    Draw a "pixel" on the screen. Each pixel is 10x10.
    """
    x_start = x_pixel * 10
    y_start = y_pixel * 10

    pygame.draw.rect(screen, [255, 0, 0], [x_start, y_start, 10, 10])


if __name__ == '__main__':
    main()
