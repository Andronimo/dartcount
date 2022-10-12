from tkinter import *
from threading import Condition
import dartConstants

class AskFrame(Frame):
    instance = False
    
    def cb(self, e):

        if ("Escape" == e.keysym):
            self.root.unbind("<KeyPress>")
            self.place_forget()  
            AskFrame.instance = False
        else:
            if (e.char != ""):
                self.answers.append(e.char)
                self.lastQuestion += 1

                if self.lastQuestion < len(self.questions):
                    self.questionLabeltext.set(self.questions[self.lastQuestion])
                else:
                    self.userCb(self.answers)
                    self.root.unbind("<KeyPress>")
                    self.place_forget()  
                    AskFrame.instance = False

        return "break"
            
    def __init__(self, questions, root, userCb):
        Frame.__init__(self, root, bg="#bae3d2")

        if False == AskFrame.instance:
            self.place(relx = 0, rely = 0.7, relwidth = 1, relheight = 0.3)

            AskFrame.instance = True

            self.questions = questions
            self.answers = []
            self.lastQuestion = 0
            self.userCb = userCb
            self.root = root

            self.questionLabeltext = StringVar()
            self.questionLabeltext.set(questions[0])

            label = Label(self, textvariable=self.questionLabeltext, font = (dartConstants.DART_FONT, 80), bg="#bae3d2")
            label.place(relx=0.5, rely=0.5,anchor="center")
            
            root.bind("<KeyPress>", lambda e:self.cb(e))