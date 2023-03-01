import asyncio
import curses
import os
import time

from explosion import explode
from itertools import cycle
from random import randint, choice

from canvas_tools import draw_frame, read_controls, get_frame_size
from get_frames import get_rocket_frames,get_garbage_frames,get_game_over_frame  
from physics import update_speed
from obstacles import Obstacle, show_obstacles
from game_scenario import PHRASES, get_garbage_delay_tics


STARS_QUANTITY = 100
TIC_TIMEOUT = 0.1
BORDER_THICKNESS = 1
MIN_HEIGHT, MIN_WIDTH = 1, 1
MIN_DELAY, MAX_DELAY = 1, 20

year = 1961
coroutines = []
obstacles = []
obstacles_in_last_collisions = []


def draw(canvas):
    curses.curs_set(False)
    canvas.border()
    canvas.nodelay(True)
    canvas.derwin(1, 1)

    window_height, window_width = canvas.getmaxyx()
    max_height = window_height - 1
    max_width = window_width - 1
    time_game_started = time.time()
    
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
        watch_time(canvas, time_game_started)
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
        for obstacle in obstacles:
            if obstacle.has_collision(row, column):
                obstacles_in_last_collisions.append(obstacle)
                return
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def fly_rocket(canvas, row, column, frames):
    frame1, frame2 = frames
    window_height, window_width = canvas.getmaxyx()
    max_height = window_height - 1
    max_width = window_width - 1
    row_speed = column_speed = 0
    game_over_frame = get_game_over_frame()

    for frame in cycle([frame1, frame1, frame2, frame2]):
        frame_rows, frame_columns = get_frame_size(frame)
        rows_dir, columns_dir, space_pressed = read_controls(canvas)
        row_increment = row + row_speed
        column_increment = column + column_speed
        row_speed, column_speed = update_speed(
                                  row_speed, column_speed,
                                  rows_dir, columns_dir)
        if space_pressed:                  
            coroutines.append(fire(canvas, row, column+2))

        if MIN_HEIGHT < row_increment < max_height - frame_rows:
            row = row_increment

        if MIN_WIDTH < column_increment < max_width - frame_columns:
            column = column_increment

        for obstacle in obstacles:
            if obstacle.has_collision(row, column):
                coroutines.append(show_gameover(canvas, game_over_frame))
                return

        draw_frame(canvas, row, column, frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, frame, negative=True)        


async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    """Animate garbage, flying from top to bottom. Сolumn position will stay same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - 1)
    row = 0
    rows_size, columns_size = get_frame_size(garbage_frame)
     
    obstacle = Obstacle(row, column, rows_size, columns_size)
    obstacles.append(obstacle)
##    obstacle_coroutine = show_obstacles(canvas, obstacles)
##    coroutines.append(obstacle_coroutine)
    
    while obstacle.row < rows_number:
        draw_frame(canvas, row, column, garbage_frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, garbage_frame, negative=True)
        row += speed
        obstacle.row += speed
        
        if obstacle in obstacles_in_last_collisions:
            obstacles.remove(obstacle)
            obstacles_in_last_collisions.remove(obstacle)
            await explode(canvas, obstacle.row, obstacle.column)
            return
        
     
async def fill_orbit_with_garbage(canvas, garbage_frames):
    _, window_width = canvas.getmaxyx()
    max_width = window_width - 1
    years = get_garbage_delay_tics(year)
    print(years)
    while True:
        garbage_frame = choice(garbage_frames)
        column = randint(MIN_WIDTH, max_width - BORDER_THICKNESS)
        coroutines.append(fly_garbage(canvas, column, garbage_frame))
        await sleep(years)


async def sleep(delay):
    for i in range(delay):
        await asyncio.sleep(0)


def watch_time(canvas, time_game_started):
    global year
    watch_window = canvas.derwin(0, 10)
    time_now = time.time()
    diff_time = int(time_now - time_game_started)
    if diff_time % 1.5 == 0.0:
        year += 1
    watch_window.addstr(f"{year}-{PHRASES.get(year, '')}")


async def show_gameover(canvas, frame):
    path = os.path.join("figures",
                        "game_over.txt")
    with open(path) as f:
        gameover = f.read()
        
    window_height, window_width = canvas.getmaxyx()
    frame_rows, frame_columns = get_frame_size(frame)
    row = (window_height - frame_rows) // 2
    column = (window_width - frame_columns) //2
    while True:
        draw_frame(canvas, row, column, frame)
        await asyncio.sleep(0)
     

def main():
    curses.update_lines_cols()
    curses.wrapper(draw)


if __name__ == '__main__':
    main()
