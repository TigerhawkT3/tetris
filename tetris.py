import tkinter as tk
import random
import pygame as pg

class Tetris:
    def __init__(self, parent):
        self.parent = parent
        self.canvas = tk.Canvas(root, height=600, width=400)
        self.canvas.grid(row=0, column=0)
        self.tickrate = 1000
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
        
    def tick(self):
        print('ticking')
        self.parent.after(self.tickrate, self.tick)
    
    def down(self):
        pass
    
    def shift(self, direction):
        pass
    
    def rotate(self, direction):
        pass
    
    def settle(self):
        pass
        
    def spawn(self):
        pass
    
    def new(self):
        pass
    
    def lose(self):
        pass
        
    def clear(self):
        pass
    
root = tk.Tk()
tetris = Tetris(root)
root.mainloop()