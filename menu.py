from tkinter import *

def keyPressed(frame, cb):
    return lambda event: cb(frame, event.char)

class MenuFrame(Frame):

    def __init__(self, root, item, cb):
        super().__init__()

        self.pack(fill=BOTH, expand=True)
        
        question = Label(self, text=item, font=("Helvetica", 70))
        question.pack(side=LEFT, padx=5, pady=5, expand=True)

        root.bind("<KeyPress>", keyPressed(self, cb))


