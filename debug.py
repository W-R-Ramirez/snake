import Tkinter

def key(event):
    print repr(event.keycode)

top = Tkinter.Tk()

board = Tkinter.Canvas(top)

board.bind("<Key>", key)
board.focus_set()
board.pack()
top.mainloop()


