from tkinter import *

class TextLabel(Canvas):

    def __init__(self, parent, bg="white", text="0", textVariable=None, width=28, height=33, font=('Calibri', 30), fixY=0, mode=0):
        Canvas.__init__(self, parent, bg=bg, highlightbackground=bg)

        self.parent = parent
        self.initWidth = width
        self.initHeight = height
        self.mode = mode

        self.txt = self.create_text(0, fixY, text=text, fill='black', font=font, anchor='nw')    
        self.findXCenter(self.txt)
        
        if mode==1:
            coords = self.bbox(self.txt)
            self.configure(width=(coords[2] - coords[0]), height=height)  
        else:
            self.configure(width=width, height=height)    

        if not textVariable == None:
            textVariable.trace_variable('w', self.on_change)

    def on_change(self, varname, index, mode):
        self.itemconfigure(self.txt, text=self.parent.getvar(varname))
        self.findXCenter(self.txt)

    def findXCenter(self, item):
        if self.mode==0:
            coords = self.bbox(item)
            xOffset = (self.initWidth / 2) - ((coords[2] - coords[0]) / 2)

            self.move(self.txt, xOffset - coords[0], 0)