import Tkinter
from time import sleep
"""
Snake. I'm thinking a square class, a food class, a snake class(which might be a sub/superclass of square), something clever to sense the arrow movements
but it seems pretty simple. Goes until it turns. Something to sense collision.
"""

class square():
    def __init__(self, board, boo, pos):
        self.board = board
        self.pos = pos
        self.x1, self.y1, self.x2, self.y2 = self.pos
        if boo == False:
            self.board.create_rectangle(self.x1,self.y1,self.x2,self.y2, fill = "black")
        if boo == True:
            self.board.create_rectangle(self.x1,self.y1,self.x2,self.y2, fill = "green")
    def remove(self):
        self.board.create_rectangle(self.x1,self.y1,self.x2,self.y2, fill = "white", outline = "white")
    def add(self, pos):
        self.x1, self.y1, self.x2, self.y2 = self.pos
        self.board.create_rectangle(self.x1,self.y1,self.x2,self.y2, fill = "black")
        

class snake():
    def __init__(self, board, head, head_direction, end, end_direction):
        self.board = board
        self.length = 3
        self.end = end
        self.head = head

        self.head.x1, self.head.y1, self.head.x2, self.head.y2 = self.head.pos

        self.board.create_rectangle(self.head.x1,self.head.y1,self.head.x2,self.head.y2, fill = "black")
    

    def add(self):
        self.length = self.length + 2
    def update(self):
        self.end.remove()
        end_pos = self.end.x1, self.end.y1, self.end.x2, self.end.y2
        end_pos = self.end.x1, self.end.y1, self.end.x2, self.end.y2
        self.end = square(board, True, end_pos)

        head_pos = self.head.x1, self.head.y1, self.head.x2, self.head.y2
        #self.head.x1
        head_pos = self.head.x1, self.head.y1, self.head.x2, self.head.y2
        self.head = square(board, True, head_pos)
        #self.end.x1, self.end.y1, self.end.x2, self.end.y2 = self.end.x1+10, self.end.y+10, self.end.x2+10, self.end.y2
"""
if direction == "Left":
            return 
        elif direction == "Right":
        elif direction == "Up":
        elif direction == "Down":
"""

top = Tkinter.Tk()

board = Tkinter.Canvas(top, width = 450, height = 550, bg = "white")


pos = 10,10,20,20
    

def key(event):
	if repr(event.keycode) == "111": #Down
	    square.remove()
	    x1,y1,x2,y2 = square.pos
	    y1,y2 = y1-10,y2-10
	    square.pos = x1,y1,x2,y2
	    square.add(pos)
	elif repr(event.keycode) == "113": #Left
	    square.remove()
	    x1,y1,x2,y2 = square.pos
	    x1,x2 = x1-10,x2-10
	    square.pos = x1,y1,x2,y2
	    square.add(pos)
	elif repr(event.keycode) == "116": #Up
	    square.remove()
	    x1,y1,x2,y2 = square.pos
	    y1,y2 = y1+10,y2+10
	    square.pos = x1,y1,x2,y2
	    square.add(pos)
	elif repr(event.keycode) == "114":  #Right
	    square.remove()
	    x1,y1,x2,y2 = square.pos
	    x1,x2 = x1+10,x2+10
	    square.pos = x1,y1,x2,y2
	    square.add(square.pos)

square = square(board, False, pos)

board.bind("<Key>", key)
board.focus_set()
board.pack()

top.mainloop()

