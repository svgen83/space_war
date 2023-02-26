import asyncio
import curses
import os
import time

from itertools import cycle
from random import randint, choice
from canvas_tools import draw_frame, read_controls, get_frame_size
from physics import update_speed


STARS_QUANTITY = 100
TIC_TIMEOUT = 0.1
BORDER_THICKNESS = 1
MIN_HEIGHT, MIN_WIDTH = 1, 1
MIN_DELAY, MAX_DELAY = 1, 20
coroutines = []


def draw(canvas):
    curses.curs_set(False)
    canvas.border()
    canvas.nodelay(True)

    window_height, window_width = canvas.getmaxyx()
    max_height = window_height - 1
    max_width = window_width - 1

    global coroutines
    frames = get_rocket_frames()
    rocket = fly_rocket(canvas, max_height//2, max_width//2, frames)
    coroutines.append(rocket)

    garbage_frames = get_garbage_frames()
    garbage_coroutine = fill_orbit_with_garbage(canvas, garbage_frames)
    coroutines.append(garbage_coroutine)
    
    for star in range(STARS_QUANTITY):
        symbol = choice("+*.:")
        row = randint(MIN_HEIGHT, max_height - BORDER_THICKNESS)
        column = randint(MIN_WIDTH, max_width - BORDER_THICKNESS)
        coroutine = blink(canvas, row, column, symbol,
                          randint(MIN_DELAY, MAX_DELAY))
        coroutines.append(coroutine)

    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        canvas.refresh()
        time.sleep(TIC_TIMEOUT)


async def blink(canvas, row, column, symbol, delay):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await sleep(delay)

        canvas.addstr(row, column, symbol)
        await sleep(delay)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await sleep(delay)

        canvas.addstr(row, column, symbol)
        await sleep(delay)


async def fire(canvas, start_row, start_column,
               rows_speed=-0.3, columns_speed=0):
    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed
    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1
    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


def get_rocket_frames():
    path_1 = os.path.join("figures",
                          "rocket_frame_1.txt")
    path_2 = os.path.join("figures",
                          "rocket_frame_2.txt")
    with open(path_1) as f:
        frame1 = f.read()
    with open(path_2) as f:
        frame2 = f.read()
    return frame1, frame2


def get_garbage_frames():
    garbage_frames = []
    garbage_figures = ["duck.txt","lamp.txt","hubble.txt",
                       "trash_large.txt","trash_small.txt","trash_xl.txt"]
    for figure in garbage_figures:
        path = os.path.join("figures", figure)
        with open(path) as f:
            frame = f.read()
        garbage_frames.append(frame)
    return garbage_frames


async def fly_rocket(canvas, row, column, frames):
    global coroutines
    frame1, frame2 = frames
    window_height, window_width = canvas.getmaxyx()
    max_height = window_height - 1
    max_width = window_width - 1
    row_speed = column_speed = 0

    for frame in cycle([frame1, frame1, frame2, frame2]):
        frame_rows, frame_columns = get_frame_size(frame)
        rows_dir, columns_dir, space_pressed = read_controls(canvas)
        row_increment = row + row_speed
        column_increment = column + column_speed
        row_speed, column_speed = update_speed(
                                  row_speed, column_speed,
                                  rows_dir, columns_dir)
        if space_pressed:                  
            coroutines.append(fire(canvas, row, column))

        if MIN_HEIGHT < row_increment < max_height - frame_rows:
            row = row_increment

        if MIN_WIDTH < column_increment < max_width - frame_columns:
            column = column_increment

        draw_frame(canvas, row, column, frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, frame, negative=True)


async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    """Animate garbage, flying from top to bottom. Сolumn position will stay same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - 1)

    row = 0

    while row < rows_number:
        draw_frame(canvas, row, column, garbage_frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, garbage_frame, negative=True)
        row += speed
        
        
async def fill_orbit_with_garbage(canvas, garbage_frames):
    global coroutines
    _, window_width = canvas.getmaxyx()
    max_width = window_width - 1
    while True:
        garbage_frame = choice(garbage_frames)
        column = randint(MIN_WIDTH, max_width - BORDER_THICKNESS)
        coroutines.append(fly_garbage(canvas, column, garbage_frame))
        await sleep(10)


async def sleep(delay):
    for i in range(delay):
        await asyncio.sleep(0)

     


def main():
    curses.update_lines_cols()
    curses.wrapper(draw)


if __name__ == '__main__':
    main()
