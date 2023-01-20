import asyncio
import curses
import os
import time

from itertools import cycle
from random import randint, choice
from canvas_tools import draw_frame, read_controls, get_frame_size


STARS_QUANTITY = 100
TIC_TIMEOUT = 0.1
BORDER_THICKNESS = 1
MIN_HEIGHT, MIN_WIDTH = 1, 1
MIN_DELAY, MAX_DELAY = 1, 20


def draw(canvas):
    curses.curs_set(False)
    canvas.border()
    canvas.nodelay(True)

    window_height, window_width = canvas.getmaxyx()
    max_height = window_height - 1
    max_width = window_width - 1

    frames = get_rocket_frames()
    coroutines = []
    coroutines.append(fire(canvas, max_height, max_width//3))
    rocket = fly_rocket(canvas, max_height//2, max_width//2, frames)
    coroutines.append(rocket)

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
        for i in range(delay):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for i in range(delay):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for i in range(delay):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for i in range(delay):
            await asyncio.sleep(0)


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


async def fly_rocket(canvas, row, column, frames):
    frame1, frame2 = frames
    window_height, window_width = canvas.getmaxyx()
    max_height = window_height - 1
    max_width = window_width - 1

    for frame in cycle([frame1, frame1, frame2, frame2]):
        frame_rows, frame_columns = get_frame_size(frame)
        rows_dir, columns_dir, _ = read_controls(canvas)
        row_increment = row + rows_dir
        column_increment = column + columns_dir

        if MIN_HEIGHT < row_increment < max_height - frame_rows:
            row = row_increment

        if MIN_WIDTH < column_increment < max_width - frame_columns:
            column = column_increment

        draw_frame(canvas, row, column, frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, frame, negative=True)


def main():
    curses.update_lines_cols()
    curses.wrapper(draw)


if __name__ == '__main__':
    main()
