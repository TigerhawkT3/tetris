import tkinter as tk
import random
import time
try:
    import pygame as pg
except ImportError:
    audio = None
else:
    audio = True
import sys
from matrix_rotation import rotate_array as ra

class Shape:
    def __init__(self, shape, key, piece, row, column, coords):
        self.shape = shape
        self.key = key
        self.piece = piece
        self._row = row
        self._rotation_index = 0
        self.column = column
        self.coords = coords
        self.hover_time = self.spin_time = time.perf_counter()
    @property
    def row(self):
        return self._row
    @row.setter
    def row(self, x):
        if x != self._row:
            self._row = x
            self.hover_time = time.perf_counter()
    @property
    def rotation_index(self):
        return self._rotation_index
    @rotation_index.setter
    def rotation_index(self, x):
        self._rotation_index = x
        self.spin_time = time.perf_counter()
    @property
    def hover(self):
        return time.perf_counter() - self.hover_time < 0.5
    @property
    def spin(self):
        return time.perf_counter() - self.spin_time < 0.5
        
class Tetris:
    def __init__(self, parent, audio):
        self.debug = 'debug' in sys.argv[1:]
        self.random = 'random' in sys.argv[1:]
        self.hover = 'nohover' not in sys.argv[1:]
        self.spin = 'spin' in sys.argv[1:]
        self.kick = 'kick' in sys.argv[1:]
        parent.title('T3tris')
        self.parent = parent
        self.audio = audio
        if self.audio: # if the import succeeded
            pg.mixer.init(buffer=512)
            try:
                self.sounds = {name:pg.mixer.Sound(name)
                                for name in ('music.ogg',
                                             'settle.ogg',
                                             'clear.ogg',
                                             'lose.ogg')}
            except pg.error as e:
                self.audio = None
                print(e)
            else:
                self.audio = {'m':True, 'f':True}
                for char in 'mMfF':
                    self.parent.bind(char, self.toggle_audio)
        self.board_width = 10
        self.board_height = 24
        self.high_score = 0
        self.high_score_lines = 0
        self.width = 300
        self.height = 720
        self.square_width = self.width//10
        self.max_speed_score = 1000
        self.speed_factor = 50
        
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
        self.colors = {'s':'green',
                       'z':'yellow',
                       'r':'turquoise',
                       'L':'orange',
                       'o':'blue',
                       'I':'red',
                       'T':'violet'}
        for key in ('<Down>', '<Left>', '<Right>', 'a', 'A', 's', 'S', 'd', 'D'):
            self.parent.bind(key, self.shift)
        for key in ('q', 'Q', 'e', 'E', '<Up>', 'w', 'W'):
            self.parent.bind(key, self.rotate)
        for key in ('<space>', '<End>', '<Control_R>', 'z', 'Z', '0', 'c', 'C'):
            self.parent.bind(key, self.snap)
        self.parent.bind('<Escape>', self.pause)
        self.parent.bind('<Control-n>', self.draw_board)
        self.parent.bind('<Control-N>', self.draw_board)
        self.parent.bind('g', self.toggle_guides)
        self.parent.bind('G', self.toggle_guides)
        self.canvas = None
        self.preview_canvas = None
        self.ticking = None
        self.spawning = None
        self.guide_fill = ''
        self.score_var = tk.StringVar()
        self.high_score_var = tk.StringVar()
        self.high_score_var.set('High Score:\n0 (0)')
        self.preview_label = tk.Label(root,
                                      text='Next Piece:',
                                      width=15,
                                      font=('Arial Black', 12))
        self.preview_label.grid(row=0, column=1, sticky='S')
        self.score_label = tk.Label(root,
                                    textvariable=self.score_var,
                                    width=15,
                                    height=5,
                                    font=('Arial Black', 12))
        self.score_label.grid(row=2, column=1, sticky='S')
        self.high_score_label = tk.Label(root,
                                         textvariable=self.high_score_var,
                                         width=15,
                                         height=5,
                                         font=('Arial Black', 12))
        self.high_score_label.grid(row=3, column=1, stick='N')
        self.draw_board()
    
    def draw_board(self, event=None):
        if self.ticking:
            self.parent.after_cancel(self.ticking)
        if self.spawning:
            self.parent.after_cancel(self.spawning)
        self.score_var.set('Score:\n0')
        self.board = [['' for column in range(self.board_width)]
                        for row in range(self.board_height)]
        self.field = [[None for column in range(self.board_width)]
                        for row in range(self.board_height)]
        if self.canvas:
            self.canvas.destroy()
        self.canvas = tk.Canvas(root, width=self.width, height=self.height)
        self.canvas.grid(row=0, column=0, rowspan=4)
        self.h_separator = self.canvas.create_line(0,
                                                 self.height//6,
                                                 self.width,
                                                 self.height//6,
                                                 width=2)
        self.v_separator = self.canvas.create_line(self.width,
                                                   0,
                                                   self.width,
                                                   self.height,
                                                   width=2)
        if self.preview_canvas:
            self.preview_canvas.destroy()
        self.preview_canvas = tk.Canvas(root,
                                        width=5*self.square_width,
                                        height=5*self.square_width)
        self.preview_canvas.grid(row=1, column=1)
        self.tickrate = 1000
        self.score = 0
        self.score_lines = 0
        self.piece_is_active = False
        self.paused = False
        self.bag = []
        self.preview()
        self.guides = [self.canvas.create_line(0, 0, 0, self.height),
                       self.canvas.create_line(self.width,
                                               0,
                                               self.width,
                                               self.height)
                        ]
        self.spawning = self.parent.after(self.tickrate, self.spawn)
        self.ticking = self.parent.after(self.tickrate*2, self.tick)
        if self.audio and self.audio['m']:
            self.sounds['music.ogg'].play(loops=-1)
    
    def toggle_guides(self, event=None):
        self.guide_fill = '' if self.guide_fill else 'black'
        self.canvas.itemconfig(self.guides[0], fill=self.guide_fill)
        self.canvas.itemconfig(self.guides[1], fill=self.guide_fill)
    
    def toggle_audio(self, event=None):
        if not event:
            return
        key = event.keysym.lower()
        self.audio[key] = not self.audio[key]
        if key == 'm':
            if not self.audio['m']:
                self.sounds['music.ogg'].stop()
            else:
                self.sounds['music.ogg'].play(loops=-1)
        
    def pause(self, event=None):
        if self.piece_is_active and not self.paused:
            self.paused = True
            self.piece_is_active = False
            self.parent.after_cancel(self.ticking)
        elif self.paused:
            self.paused = False
            self.piece_is_active = True
            self.ticking = self.parent.after(self.tickrate, self.tick)
    
    def print_board(self):
        for row in self.board:
            print(*(cell or ' ' for cell in row), sep='')
    
    def check(self, shape, r, c, l, w):
        for row, squares in zip(range(r, r+l), shape):
            for column, square in zip(range(c, c+w), squares):
                if (row not in range(self.board_height)
                    or
                    column not in range(self.board_width)
                    or
                    (square and self.board[row][column] == 'x')
                    ): # also, make sure it's on the board
                    return
        return True
    
    def move(self, shape, r, c, l, w):
        square_idxs = iter(range(4)) # iterator of 4 indices
        
        # remove shape from board
        for row in self.board:
            row[:] = ['' if cell=='*' else cell for cell in row]
        # put shape onto board and piece onto canvas
        for row, squares in zip(range(r, r+l), shape):
            for column, square in zip(range(c, c+w), squares):
                if square:
                    self.board[row][column] = square
                    square_idx = next(square_idxs)
                    coord = (column*self.square_width,
                             row*self.square_width,
                             (column+1)*self.square_width,
                             (row+1)*self.square_width)
                    self.active_piece.coords[square_idx] = coord
                    self.canvas.coords(self.active_piece.piece[square_idx],
                                            coord)
        self.active_piece.row = r
        self.active_piece.column = c
        self.active_piece.shape = shape
        self.move_guides(c, c+w)
        if self.debug:
            self.print_board()
        return True
        
    def check_and_move(self, shape, r, c, l, w):
        return self.check(shape, r, c, l, w
            ) and self.move(shape, r, c, l, w)
        
    def rotate(self, event=None):
        if not self.piece_is_active:
            return
        if len(self.active_piece.shape) == len(self.active_piece.shape[0]):
            self.active_piece.rotation_index = self.active_piece.rotation_index
            return
        r = self.active_piece.row
        c = self.active_piece.column
        l = len(self.active_piece.shape)
        w = len(self.active_piece.shape[0])
        x = c + w//2 # center column for old shape
        y = r + l//2 # center row for old shape
        direction = event.keysym
        if direction in {'q', 'Q'}:
            shape = ra(self.active_piece.shape, -90)
            # 4 is a magic number, number of sides of a rectangle
            rotation_index = (self.active_piece.rotation_index - 1) % 4
            rx,ry = self.active_piece.rotation[rotation_index]
            rotation_offsets = -rx,-ry
        elif direction in {'e', 'E', '0', 'Up', 'w', 'W'}:
            shape = ra(self.active_piece.shape, 90)
            rotation_index = self.active_piece.rotation_index
            rotation_offsets = self.active_piece.rotation[rotation_index]
            rotation_index = (rotation_index + 1) % 4

        l = len(shape) # length of new shape
        w = len(shape[0]) # width of new shape
        rt = y - l//2 # row of new shape
        ct = x - w//2 # column of new shape
        x_correction,y_correction = rotation_offsets
        rt += y_correction
        ct += x_correction
        
        if self.check_and_move(shape, rt, ct, l, w):
            self.active_piece.rotation_index = rotation_index
            return
        
        if self.kick:
            for a,b in zip((0, 0,-1, 0,0,-2,-1,-1),
                           (-1,1, 0,-2,2, 0,-1, 1)):
                if self.check_and_move(shape, rt+a, ct+b, l, w):
                    self.active_piece.rotation_index = rotation_index
                    return
                    
    def tick(self):
        if self.piece_is_active and not (self.spin and self.active_piece.spin):
            self.shift()
        self.ticking = self.parent.after(self.tickrate, self.tick)
    
    def shift(self, event=None):
        down = {'Down', 's', 'S'}
        left = {'Left', 'a', 'A'}
        right = {'Right', 'd', 'D'}
        if not self.piece_is_active:
            return
        r = self.active_piece.row
        c = self.active_piece.column
        l = len(self.active_piece.shape)
        w = len(self.active_piece.shape[0])
        direction = (event and event.keysym) or 'Down'
        # use event.keysym to check event/direction
        if direction in down:
            rt = r+1 # row, temporary
            ct = c # column, temporary
        elif direction in left:
            rt = r
            ct = c-1
        elif direction in right:
            rt = r
            ct = c+1
        
        success = self.check_and_move(self.active_piece.shape, rt, ct, l, w)
        
        if direction in down and not success and not (self.hover and self.active_piece.hover):
            self.settle()
    
    def settle(self):
        self.piece_is_active = False
        for row in self.board:
            row[:] = ['x' if cell=='*' else cell for cell in row]
        for (x1,y1,x2,y2),id in zip(self.active_piece.coords, self.active_piece.piece):
            self.field[y1//self.square_width][x1//self.square_width] = id
        indices = [idx for idx,row in enumerate(self.board) if all(row)]
        if indices: # clear rows, score logic, etc.
            self.score += (1, 2, 5, 10)[len(indices)-1]
            self.score_lines += len(indices)
            self.clear(indices)
            if all(not cell for row in self.board for cell in row):
                self.score += 10
            self.high_score = max(self.score, self.high_score)
            self.high_score_lines = max(self.score_lines, self.high_score_lines)
            self.score_var.set('Score:\n{} ({})'.format(self.score, self.score_lines))
            self.high_score_var.set('High Score:\n{} ({})'.format(self.high_score, self.high_score_lines))
            if self.score <= self.max_speed_score:
                self.tickrate = 1000 // (self.score//self.speed_factor + 1)
        if any(any(row) for row in self.board[:4]):
            self.lose()
            return
        if self.audio and self.audio['f'] and not indices:
            self.sounds['settle.ogg'].play()
        self.spawning = self.parent.after(500 if indices and self.tickrate<500 else self.tickrate, self.spawn)
    
    def preview(self):
        self.preview_canvas.delete(tk.ALL)
        if not self.bag:
            if self.random:
                self.bag.append(random.choice('szrLoIT'))
            else:
                self.bag = random.sample('szrLoIT', 7)
        key = self.bag.pop()
        shape = ra(self.shapes[key], random.choice((0, 90, 180, 270)))
        self.preview_piece = Shape(shape, key, [], 0, 0, [])
        width = len(shape[0])
        half = self.square_width//2
        for y,row in enumerate(shape):
            for x,cell in enumerate(row):
                if cell:
                    self.preview_piece.coords.append((self.square_width*x+half,
                                                 self.square_width*y+half,
                                                 self.square_width*(x+1)+half,
                                                 self.square_width*(y+1)+half))
                    self.preview_piece.piece.append(
                    self.preview_canvas.create_rectangle(self.preview_piece.coords[-1],
                                                 fill=self.colors[key],
                                                 width=3))
        
        self.preview_piece.rotation_index = 0
        self.preview_piece.i_nudge = (len(shape) < len(shape[0])
                                    ) and 4 in (len(shape), len(shape[0]))
        self.preview_piece.row = self.preview_piece.i_nudge
        if 3 in (len(shape), len(shape[0])):
            self.preview_piece.rotation = [(0,0),
                                          (1,0),
                                          (-1,1),
                                          (0,-1)]
        else:
            self.preview_piece.rotation = [(1,-1),
                                          (0,1),
                                          (0,0),
                                          (-1,0)]
        if len(shape) < len(shape[0]): # wide shape
            self.preview_piece.rotation_index += 1
    
    def move_guides(self, left, right):
        left *= self.square_width
        right *= self.square_width
        self.canvas.coords(self.guides[0], left, 0,
                                           left, self.height)
        self.canvas.coords(self.guides[1], right, 0,
                                           right, self.height)
    
    def spawn(self):
        self.piece_is_active = True
        self.active_piece = self.preview_piece
        self.preview()
        width = len(self.active_piece.shape[0])
        start = (10-width)//2
        self.active_piece.column = start
        self.active_piece.start = start
        self.active_piece.coords = []
        self.active_piece.piece = []
        for y,row in enumerate(self.active_piece.shape):
            self.board[y+self.active_piece.i_nudge][start:start+width] = self.active_piece.shape[y]
            for x,cell in enumerate(row, start=start):
                if cell:
                    self.active_piece.coords.append((self.square_width*x,
                                                 self.square_width*(y+self.active_piece.i_nudge),
                                                 self.square_width*(x+1),
                                                 self.square_width*(y+self.active_piece.i_nudge+1)))
                    self.active_piece.piece.append(
                    self.canvas.create_rectangle(self.active_piece.coords[-1],
                                                 fill=self.colors[self.active_piece.key],
                                                 width=3))
        self.move_guides(start, start+width)

        if self.debug:
            self.print_board()
    
    def lose(self):
        self.piece_is_active = False
        if self.audio and self.audio['f']:
            self.sounds['lose.ogg'].play()
        if self.audio and self.audio['m']:
            self.sounds['music.ogg'].stop()
        self.parent.after_cancel(self.ticking)
        self.parent.after_cancel(self.spawning)
        self.clear_iter(range(len(self.board)))
    
    def snap(self, event=None):
        down = {'space', 'End'}
        left = {'Control_R', 'z', 'Z'}
        right = {'0', 'c', 'C'}
        if not self.piece_is_active:
            return
        r = self.active_piece.row
        c = self.active_piece.column
        l = len(self.active_piece.shape)
        w = len(self.active_piece.shape[0])
        
        direction = event.keysym
        # use event.keysym to check event/direction
        
        while 1:
            if self.check(self.active_piece.shape,
                              r+(direction in down),
                              c+(direction in right)-(direction in left),
                              l, w):
                r += direction in down
                c += (direction in right) - (direction in left)
            else:
                break
        
        self.move(self.active_piece.shape, r, c, l, w)
        
        if direction in down:
            self.settle()
    
    def clear(self, indices):
        if self.audio and self.audio['f']:
            self.sounds['clear.ogg'].play()
        for idx in indices:
            self.board.pop(idx)
            self.board.insert(0, ['' for column in range(self.board_width)])
        self.clear_iter(indices)
    
    def clear_iter(self, indices, current_column=0):
        for row in indices:
            if row%2:
                cc = current_column
            else:
                cc = self.board_width - current_column - 1
            id = self.field[row][cc]
            self.field[row][cc] = None
            self.canvas.delete(id)
        if current_column < self.board_width-1:
            self.parent.after(50, self.clear_iter, indices, current_column+1)
        else:
            for idx,row in enumerate(self.field):
                offset = sum(r > idx for r in indices)*self.square_width
                for square in row:
                    if square:
                        self.canvas.move(square, 0, offset)
            for row in indices:
                self.field.pop(row)
                self.field.insert(0, [None for x in range(self.board_width)])
                
    
root = tk.Tk()
tetris = Tetris(root, audio)
root.mainloop()