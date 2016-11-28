import tkinter as tk
import random
import pygame as pg
from matrix_rotation import rotate_array as ra

class Tetris:
    def __init__(self, parent):
        parent.title('T3tris')
        self.parent = parent
        self.board_width = 10
        self.board_height = 24
        self.board = [['' for column in range(self.board_width)]
                        for row in range(self.board_height)]
        self.width = 300
        self.height = 720
        self.square_width = self.width//10
        self.canvas = tk.Canvas(root, width=self.width, height=self.height)
        self.canvas.grid(row=0, column=0)
        self.separator = self.canvas.create_line(0,
                                                 self.height//6,
                                                 self.width,
                                                 self.height//6,
                                                 width=2)
        self.tickrate = 1000
        self.piece_is_active = False
        self.parent.after(self.tickrate, self.tick)
        self.shapes = {'s':[['*', ''],
                            ['*', '*'],
                            ['', '*']],
                       'z':[['', '*'],
                            ['*', '*'],
                            ['*', '']],
                       'r':[['*', '*'],
                            ['*', ''],
                            ['*', '']],
                       'L':[['*', ''],
                            ['*', ''],
                            ['*', '*']],
                       'o':[['*', '*'],
                            ['*', '*']],
                       'I':[['*'],
                            ['*'],
                            ['*'],
                            ['*']],
                       'T':[['*', '*', '*'],
                            ['', '*', '']]
                      }
        self.parent.bind('<Down>', self.shift)
        self.parent.bind('<Left>', self.shift)
        self.parent.bind('<Right>', self.shift)
        
    def tick(self):
        if not self.piece_is_active:
            self.spawn()
        
        #self.parent.after(self.tickrate, self.tick)
    
    def shift(self, event=None):
        if not self.piece_is_active:
            return
        r = self.active_piece['row']
        c = self.active_piece['column']
        l = len(self.active_piece['shape'])
        w = len(self.active_piece['shape'][0])
        direction = (event and event.keysym) or 'Down'
        # use event.keysym to check event/direction
        if direction == 'Down':
            if r+l >= self.board_height:
                self.settle()
                return
            rt = r+1 # row, temporary
            ct = c # column, temporary
        elif direction == 'Left':
            if not c:
                return
            rt = r
            ct = c-1
        elif direction == 'Right':
            if c+w >= self.board_width:
                return
            rt = r
            ct = c+1
        # checks for collision with existing pieces
        for row, squares in zip(range(rt, rt+l),
                                self.active_piece['shape']
                                ):
            for column, square in zip(range(ct, ct+w), squares):
                if square and self.board[row][column] == 'x':
                    print(row, column, square, self.board[row][column])
                    if direction == 'Down':
                        self.settle()
                    return
        # remove shape from board
        for row in self.board:
            row[:] = ['' if cell=='*' else cell for cell in row]
        if direction == 'Down':
            self.active_piece['row'] += 1 # increment piece's row
            r += 1 # increment piece's row
        elif direction == 'Left':
            self.active_piece['column'] -= 1 # decrement piece's column
            c -= 1 # decrement piece's column
        elif direction == 'Right':
            self.active_piece['column'] += 1 # increment piece's column
            c += 1 # increment piece's column
        # put shape onto board
        for row, squares in zip(range(r, r+l),
                                self.active_piece['shape']
                                ):
            for column, square in zip(range(c, c+w), squares):
                if square:
                    self.board[row][column] = square
        # move piece on canvas
        for id,coords_idx in zip(self.active_piece['piece'], range(len(self.active_piece['coords']))):
            x1,y1,x2,y2 = self.active_piece['coords'][coords_idx]
            if direction == 'Down':
                y1 += self.square_width
                y2 += self.square_width
            elif direction == 'Left':
                x1 -= self.square_width
                x2 -= self.square_width
            elif direction == 'Right':
                x1 += self.square_width
                x2 += self.square_width
            self.active_piece['coords'][coords_idx] = x1,y1,x2,y2
            self.canvas.coords(id, self.active_piece['coords'][coords_idx])
    
    def rotate(self, direction):
        pass
    
    def settle(self):
        pass # this will check for loss by checking the height of the board content
        # size is 10x20, extra space giving 10x24
        self.piece_is_active = False
        print('clonk')
        for row in self.board:
            row[:] = ['x' if cell=='*' else cell for cell in row]
            print(row)
        self.parent.after(self.tickrate, self.spawn())
        
    def spawn(self):
        self.piece_is_active = True
        shape = self.shapes[random.choice('szrLoIT')]
        shape = ra(shape, random.choice((0, 90, 180, 270)))
        width = len(shape[0])
        start = (10-width)//2
        self.active_piece = {'shape':shape, 'piece':[], 'row':0, 'column':start, 'coords':[]}
        for y,row in enumerate(shape):
            self.board[y][start:start+width] = shape[y]
            for x,cell in enumerate(row, start=start):
                if cell:
                    self.active_piece['coords'].append((self.square_width*x,
                                                 self.square_width*y,
                                                 self.square_width*(x+1),
                                                 self.square_width*(y+1)))
                    self.active_piece['piece'].append(
                    self.canvas.create_rectangle(self.active_piece['coords'][-1]))
        for row in self.board:
            print(row)
    
    def new(self):
        pass
    
    def lose(self):
        pass
        
    def clear(self):
        pass
    
root = tk.Tk()
tetris = Tetris(root)
root.mainloop()