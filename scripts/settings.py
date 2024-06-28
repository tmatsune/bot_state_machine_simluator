import pygame as pg
import sys, math, array
from enum import Enum
from dataclasses import dataclass

vec2 = pg.math.Vector2

WIDTH = 660
HEIGHT = 660
CENTER = vec2(WIDTH // 2, HEIGHT // 2)
HISTORY_SIZE: list = [600, 400]

CELL_SIZE = 30
ROWS = HEIGHT // CELL_SIZE
COLS = WIDTH // CELL_SIZE

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (210, 210, 220)
RED = (255, 0, 0)
BLUE = (0,0,255)
GREEN = (0, 255, 0)
TEXT_BG = (10, 10, 20)
BUTTON_COLOR = (50, 100, 160)
OUTLINE_COLOR = (210, 210, 210)
PINK = (255, 10, 80)

inf = float('inf')
n_inf = float('-inf')
false = False
true = True
NULL = None

FPS = 60
PI = math.pi
