import asyncio
import curses
import time

from itertools import cycle
from random import randint, choice
from canvas_tools import draw_frame, read_controls, get_frame_size


TIC_TIMEOUT = 0.1


def draw(canvas):
  curses.curs_set(False)
  canvas.border()
  canvas.refresh()
  canvas.nodelay(True)
  
  height, width = canvas.getmaxyx()
  stars_quantity = 200
  frames = open_frames()
  coroutines = []
  coroutines.append(fire(canvas, height-1, width//3))
  rocket = fly_rocket(canvas, height//2, width//2, frames)
  coroutines.append(rocket)
         
  for i in range(stars_quantity):
    symbol = choice("+*.:")
    row = randint(1, height-2)
    column = randint(1, width-2)
    coroutine = blink(canvas, row, column, symbol)
    coroutines.append(coroutine)

  while True:
    try:
      for coroutine in coroutines:
        coroutine.send(None)
        canvas.refresh()
      time.sleep(TIC_TIMEOUT)
    except StopIteration:
      coroutines.remove(coroutine)


async def blink(canvas, row, column, symbol):
    while True:
      delay = randint(1, 20)
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


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot, direction and speed can be specified."""

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


def open_frames():
    with open("figures/rocket_frame_1.txt") as f:
        frame1 = f.read()
    with open("figures/rocket_frame_2.txt") as f:
        frame2 = f.read()
    return frame1, frame2
  
        
async def fly_rocket(canvas, row, column, frames):
    for frame in cycle(frames):
      rows_dir, columns_dir, _ = read_controls(canvas)
      row += rows_dir
      column += columns_dir
      draw_frame(canvas, row, column, frame)
      await asyncio.sleep(0)
      draw_frame(canvas, row, column, frame, negative=True)
        
      
if __name__ == '__main__':

  curses.update_lines_cols()
  curses.wrapper(draw)
    
