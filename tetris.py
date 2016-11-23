import tkinter as tk
import random
import pygame as pg
from matrix_rotation import rotate_array as ra

class Tetris:
    def __init__(self, parent):
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
        self.parent.bind('<Down>', self.down)
        
    def tick(self):
        if not self.piece_is_active:
            self.spawn()
            self.piece_is_active = not self.piece_is_active
        
        #self.parent.after(self.tickrate, self.tick)
    
    def down(self, event=None):
        if not self.piece_is_active:
            return
        r = self.active_piece['row']
        c = self.active_piece['column']
        l = len(self.active_piece['shape'])
        w = len(self.active_piece['shape'][0])
        # use event.keysym to check event/direction
        if r+l >= self.board_height:
            self.settle()
            return
        self.board[r][c:c+w] = [''] * w
        self.active_piece['row'] += 1
        r += 1
        for squares, row in zip(self.active_piece['shape'],
                                range(r, r+l)):
            self.board[row][c:c+w] = squares
        for id,coords_idx in zip(self.active_piece['piece'], range(len(self.active_piece['coords']))):
            x1,y1,x2,y2 = self.active_piece['coords'][coords_idx]
            y1 += self.square_width
            y2 += self.square_width
            self.active_piece['coords'][coords_idx] = x1,y1,x2,y2
            self.canvas.coords(id, self.active_piece['coords'][coords_idx])
    
    def shift(self, direction):
        pass
    
    def rotate(self, direction):
        pass
    
    def settle(self):
        pass # this will check for loss by checking the height of the board content
        # size is 10x20, extra space giving 10x24
        self.piece_is_active = not self.piece_is_active
        print('clonk')
        
    def spawn(self):
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