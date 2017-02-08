import Tkinter
import tkFont
from random import randrange
"""
Snake. I'm thinking a square class, a food class, a snake class(which might be a sub/superclass of square), something clever to sense the arrow movements
but it seems pretty simple. Goes until it turns. Something to sense collision.
"""
board_width = 480
board_height = 600

class game():
    def __init__(self, board, head_pos, head_direction, end_pos, end_direction):
        self.A = 3
        self.board = board
        self.length = 3
        self.score = 0
        self.end_pos = end_pos
        self.turn_direction = []
        self.turn_length = []
        self.turn = []
        self.future_turns = []
        self.head_pos = head_pos
        self.turning = False
        self.eaten = False
        self.remove = True
        self.end_direction = end_direction
        self.head_x1, self.head_y1, self.head_x2, self.head_y2 = self.head_pos
        self.head_direction = head_direction
        self.board.create_rectangle(self.head_x1,self.head_y1,self.head_x2,self.head_y2, fill = "black", outline = "white")
        self.board.create_rectangle(self.head_x1,self.head_y1+12, self.head_x2,self.head_y2+12, fill = "black", outline = "white")
        self.board.create_rectangle(self.head_x1,self.head_y1+24, self.head_x2,self.head_y2+24, fill = "black", outline = "white")
        self.make_food()

    def stop_remove(self):
        self.A = 0
        self.make_food()

    def update_score(self):
        for i in self.board.find_withtag("Score"):
            self.board.delete(i)
        self.board.create_text(board_width/2, 10, text = "Score:" + str(self.score), tags = "Score")
        self.score = self.score + (self.length)*5

    def make_food(self):
        self.update_score()
        foodx = randrange(40)
        foody = randrange(50)
        if not self.board.find_overlapping(foodx*12, foody*12,foodx*12+12, foody*12+12):
            self.board.create_rectangle(foodx*12, foody*12,foodx*12+12, foody*12+12, fill = "green", outline = "white")
            self.board.addtag_overlapping("FOOD", foodx*12+1, foody*12+1,foodx*12+12-1, foody*12+12-1)
        else:
            self.make_food()

    def turn_snake(self, head_direction):
        if head_direction != self.head_direction and opposite[head_direction] != self.head_direction:
            if not self.turning:
                self.head_direction = head_direction
                self.turn_direction.append(self.head_direction)
                self.turn_length.append(self.length-1)
                game.turning = True
            else:
                self.future_turns.append(head_direction) 
            
        


    def update(self):
        self.turning = False
        if self.A <= 2:
            self.remove = False
            self.A = self.A + 1
            self.length = self.length + 1

        elif self.eaten:
            self.eaten = False
            self.remove = True

        else:
            self.remove = True

        
        
        if self.remove:
            self.turn = zip(self.turn_direction, self.turn_length)
            self.end_pos = move(self.end_pos, self.end_direction)
            tail1,tail2,tail3,tail4 = self.end_pos
            for i in self.board.find_overlapping(tail1+1,tail2+1,tail3-1,tail4-1):
                self.board.delete(i)
            
            if self.turn:
                for i in range(len(self.turn_length)):
                    self.turn_length[i] = self.turn_length[i]-1       
                for turn_info in self.turn:
                    direction, time_till = turn_info
                    if time_till == 0:
                        self.turn_direction.remove(self.turn_direction[0])
                        self.turn_length.remove(self.turn_length[0])
                        self.end_direction = direction

        
        self.head_pos = move(self.head_pos, self.head_direction)

        

        head1,head2,head3,head4 = self.head_pos
        for i in self.board.find_overlapping(head1+1,head2+1,head3-1,head4-1):
            if i in board.find_withtag("FOOD"):
                self.stop_remove()
                self.eaten = True
            elif i in board.find_withtag("KILL"):
                return True
       
        
        self.board.create_rectangle(self.head_pos, fill = "black", outline = "white", tags = "KILL")
        if self.future_turns:
            self.turn_snake(self.future_turns[0])
            self.future_turns.remove(self.future_turns[0])

        

def move(pos, direction):
    x1,y1,x2,y2 = pos
    if direction == "N":
        pos = x1,y1-12,x2,y2-12
    elif direction == "E":
        pos = x1+12, y1, x2+12, y2
    elif direction == "S":
        pos = x1, y1+12, x2, y2+12
    elif direction == "W":
        pos = x1-12, y1, x2-12, y2

    return pos

def key(event):
    if repr(event.keycode) == "111":
        game.turn_snake("N")
    elif repr(event.keycode) == "114":
        game.turn_snake("E")
    elif repr(event.keycode) == "113":
        game.turn_snake("W")
    elif repr(event.keycode) == "116":
        game.turn_snake("S")

    if repr(event.keycode) == "36":
        board.delete("all")
        new_game(board, pos, end_pos, board_width, board_height)
        start_game(False)

top = Tkinter.Tk()
top.title("Snake")

board = Tkinter.Canvas(top, width = board_width, height = board_height, bg = "white")

pos = 228,300,240,312
end_pos = 228,336,240,348

opposite = {"N":"S", "S":"N", "W":"E", "E":"W"}

def new_game(board, pos, end_pos, board_width, board_height):
    
    board.create_rectangle(0,-5,board_width,0, tags = "KILL")
    board.create_rectangle(-5,0,0,board_height, tags = "KILL")
    board.create_rectangle(board_width+5,0,board_width+1,board_height+1,tags = "KILL")
    board.create_rectangle(0,board_height+5,board_width+1,board_height+1, tags = "KILL")

    board.bind("<Key>", key)
    board.focus_set()
    board.pack()

font = tkFont.Font(size = 18)

game = game(board, pos, "N", end_pos, "N")

def run():
    if not game.update():
        board.after(75, run)
    else:
        board.create_text(board_width/2,board_height/2, text = "GAME OVER", font = font)
        board.create_text(board_width/2, board_height/2+35, text = "Score" + str(game.score), font = font)
        game_over = True

game_over = False
run()

new_game(board, pos, end_pos, board_width, board_height)   

top.mainloop()
