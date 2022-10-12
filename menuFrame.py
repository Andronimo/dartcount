from tkinter import *
from askFrame import AskFrame
import platform
import dartConstants

KEYCODES = {
  90: 0,
  87: 1,
  88: 2,
  89: 3,
  83: 4,
  84: 5,
  85: 6,
  79: 7,
  80: 8,
  81: 9
}

class MenuFrame(Frame):
    instance = False
    
    def getNum(self, keycode):
        return KEYCODES[keycode]

    def cb(self, e):

        self.root.unbind("<KeyPress>")
        self.place_forget()  
        AskFrame.instance = False

        number = e.keycode
        if platform.system() == "Linux":
            if e.keycode in KEYCODES:
                number = KEYCODES[e.keycode]

        if platform.system() == "Windows":
            number = e.keycode - 96

        if number >= 0 and number <= 9:
            self.userCb(self.answers[number])
        else:
            self.userCb("cancel")

        return "cancel"
            
    def __init__(self, shortcuts, root, userCb):
        Frame.__init__(self, root, bg="white", borderwidth=2, relief="groove")

        if False == AskFrame.instance:
            self.place(relx = 0.25, rely = 0.3, relwidth = 0.5, relheight = 0.4)

            AskFrame.instance = True

            numpad = [7,8,9,4,5,6,1,2,3,0]
            self.answers = [""] * 10
            self.shortcuts = shortcuts
            self.userCb = userCb
            self.root = root
            self.grid_columnconfigure(0, weight=1)
            self.grid_columnconfigure(1, weight=1)

            self.grid_rowconfigure(0, weight=1)
            self.grid_rowconfigure(1, weight=1)
            self.grid_rowconfigure(2, weight=1)
            self.grid_rowconfigure(3, weight=1)

            for i, s in enumerate(shortcuts):
                text = ""

                if isinstance(s, list):
                    self.answers[numpad[i]] = s[1]
                    text = s[0]
                else:
                    self.answers[numpad[i]] = s
                    text = s

                while len(text) < 3:
                    text = " {}".format(text)
                label = Label(self, borderwidth=2, relief="groove", bg="#fff3bf", text="{}: {}".format(numpad[i], text), font = (dartConstants.DART_FONT, 30))
                label.grid(column=i%3, row=int(i/3), sticky="nesw")
            
            root.bind("<KeyPress>", lambda e:self.cb(e))