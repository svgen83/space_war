import time
import curses
import asyncio
from random import randint, choice


TIC_TIMEOUT = 0.1


def draw(canvas):
    
  curses.curs_set(False)
  canvas.border()
  canvas.refresh()
  height, width = canvas.getmaxyx()
  stars_quantaty = 200 
  coroutines = []
  coroutines.append(fire(canvas, height-1, 10))
  for column in range(stars_quantaty):
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
    if len(coroutines) == 0:
        break
   
      #canvas.refresh()
    # canvas.addstr(row, column, '*', curses.A_DIM)
    # canvas.refresh()
    # time.sleep(2)
    # canvas.addstr(row, column, '*')
    # canvas.refresh()
    # time.sleep(0.3)
    # canvas.addstr(row, column, '*', curses.A_BOLD)
    # canvas.refresh()
    # time.sleep(0.5)
    # canvas.addstr(row, column, '*')
    # canvas.refresh()
    


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

      
if __name__ == '__main__':
  curses.update_lines_cols()
  curses.wrapper(draw)
    
