#!/usr/bin/python3
# -*- coding: utf-8 -*-

from random import randint

class InputError(BaseException):
    pass

class Grid:

    ALIVE = 'X'
    DEAD = ' '

    def __init__(self, x, y, extra=1):
        """x = visible width.
        y = visible height.
        extra = number of extra rows and columns outside visible field,
        defaults to 1."""

        self.visible_height = y
        self.visible_width = x
        self.total_height = y + (extra*2)
        self.total_width = x + (extra*2)
        self.visible_start = extra
        self.vis_end_y = extra + self.visible_height
        self.vis_end_x = extra + self.visible_width
    
        self.empty_grid = [[self.DEAD for i in range(self.total_width)]
                for j in range(self.total_height)]
        self.grid = self.new_empty_grid()
   
    def new_empty_grid(self):
        return [row[:] for row in self.empty_grid[:]]

    def empty_self(self):
        self.grid = self.new_empty_grid()

    def populate(self, percent):
        start = self.visible_start
        x, y = self.vis_end_x, self.vis_end_y
        total = self.visible_height * self.visible_width
        to_alloc = int(total * (percent / 100))
        while to_alloc:
            rand_x, rand_y = randint(start, x), randint(start, y)
            if not self.is_alive(rand_x, rand_y):
                self.set_tile(rand_x, rand_y, True)
                to_alloc -= 1

    def get_tile(self, x, y):
        try:
            return self.grid[y][x]
        except IndexError:
            return self.DEAD

    def set_tile(self, x, y, val):
        """val = True sets tile to occupied, False sets to vacant"""
        self.grid[y][x] = (self.ALIVE if val else self.DEAD)

    def is_alive(self, x, y):
        return self.get_tile(x, y) == self.ALIVE

    def get_neighbors(self, x, y):
        return [self.get_tile(x, y) for x, y in
                [[x-1, y-1], [x, y-1], [x+1, y-1], [x-1, y+1],
                 [x, y+1], [x+1, y+1], [x-1, y], [x+1, y]]] 

    def get_visible(self):
        return [line[self.visible_start:self.vis_end_x] for line in
            self.grid[self.visible_start:self.vis_end_y]]

class Game:

    def __init__(self, x, y, percent, extra=1):
        
        self.grid = Grid(x, y, extra)
        self.grid_buffer = Grid(x, y, extra)
        
        self.grid.populate(percent)

    def generation(self):
        self.grid_buffer.empty_self()
        for y in range(self.grid.visible_start, self.grid.vis_end_y):
            for x in range(self.grid.visible_start, self.grid.vis_end_x):
                alive = self.grid.is_alive(x, y)
                live_neighbors = self.grid.get_neighbors(x, y).count(self.grid.ALIVE)
                if alive:
                    if live_neighbors > 1 and live_neighbors < 4:
                        self.grid_buffer.set_tile(x, y, True)
                    else:
                        self.grid_buffer.set_tile(x, y, False)
                else:
                    if live_neighbors == 3:
                        self.grid_buffer.set_tile(x, y, True)
                    else:
                        self.grid_buffer.set_tile(x, y, False)
        self.grid.grid = self.grid_buffer.grid

    def display(self):
        """Return the current grid as a list of strings."""
        vis = self.grid.get_visible()
        return [''.join(row) for row in vis]



############################

import curses

class CursesInterface:

    def __init__(self):

        self.stdscr = curses.initscr()

        max_size = self.stdscr.getmaxyx()
        self.row_max = max_size[0] - 4
        self.col_max = max_size[1] - 4
        
        self.row_prompt = 'Enter number of rows in grid (between 1 and %d):' % self.row_max
        self.col_prompt = 'Enter number of columns in grid (between 1 and is %d):' % self.col_max
        self.pop_prompt = 'Enter starting percentage of grid alive at start (between 1 and 100):'

        self.opts = {
                'r': self.setup,
                ' ': self.next_gen,
                'q': self.quit
                }

        self.setup()
        self.print_grid()
        self.mainloop()

    def setup(self):

        # Get info for setting up CGOL
        curses.echo()
        y = self.get_num(1, 1, self.row_prompt, 1, self.row_max, int)
        x = self.get_num(1, 3, self.col_prompt, 1, self.col_max, int)
        pop = self.get_num(1, 5, self.pop_prompt, 1, 100, float)
        curses.noecho()

        # Create CGOL game
        self.game = Game(x, y, pop, 4)

        # Create window for grid
        self.display = curses.newwin(y+2, x+2, 0, 0)
        self.display.box()
    
    def get_num(self, x, y,  prompt, mn, mx, typ):
        bad_input = True
        self.stdscr.addstr(y, x, prompt)
        while bad_input:
            try:
                num = typ(self.stdscr.getstr(y+1, x))
                bad_input = False
            except ValueError:
                bad_input = True
            if (mn > x) or (mx < x):
                bad_input = True
        return num


    def print_grid(self):
        buff = self.game.display()
        for row, line in enumerate(buff):
            self.display.addstr(row+1, 1, line)
        self.display.refresh()
        self.stdscr.addstr(self.game.grid.visible_height+3, 0,
                'SPACE = next generation; r = reset; q = quit')
        self.stdscr.refresh()

    def get_chosen_func(self):
        y_corner, x_corner = [i-1 for i in self.stdscr.getmaxyx()]    
        func = None
        while func is None:
            opt = chr(self.stdscr.getch(y_corner, x_corner))
            func = self.opts.get(opt, None)
        return func

    def reset(self):
        self.stdscr.clear()
        self.setup()
        self.print_grid()

    def next_gen(self):
        self.game.generation()
        self.print_grid()

    def quit(self):
        self.stdscr.keypad(0)
        curses.endwin()
        quit()
    
    def mainloop(self):
        while True:
            func = self.get_chosen_func()
            func()

if __name__ == '__main__':
    CursesInterface()
