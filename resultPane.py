from tkinter import *
from random import *
from textLabel import *
import dartConstants

TEXTSIZE = 30

class ResultPane(Frame):

    def keydown(self, cmd):
        
        if cmd == "KP_Down":
            self.looseFocus()
            self.gf.setCurrentFocus(0)

        if cmd == "KP_Left":
            self.focusLeft()

        if cmd == "KP_Right":
            self.focusRight()

    def looseFocus(self):
        self.focusColor = "#ffd79c"
        self.focus(self.gf.currentSet,self.gf.currentLeg)
        self.unbind("<KeyPress>")

    def takeFocus(self):
        self.focusColor = "lightgreen"
        self.focus(self.gf.currentSet,self.gf.currentLeg)
        self.focus_set()
        self.bind("<KeyPress>", lambda e:self.keydown(e.keysym))

    def changeGfLeg(self):
        self.gf.currentSet = self.lastFocus[0]
        self.gf.currentLeg = self.lastFocus[1]
        self.gf.setScoreEntries()

    def focusRight(self):
        nextFocus = self.lastFocus.copy()
        nextFocus[1] += 1

        if len(self.labels[nextFocus[0]]) <= nextFocus[1]:
            nextFocus[0] += 1
            nextFocus[1] = 0
            if len(self.labels) <= nextFocus[0]:
                nextFocus = self.lastFocus.copy()

        self.focus(nextFocus[0],nextFocus[1])
        self.changeGfLeg()        

    def focusLeft(self):

        nextFocus = self.lastFocus.copy()
        nextFocus[1] -= 1

        if nextFocus[1] < 0:
            nextFocus[0] -= 1
            if nextFocus[0] < 0:
                nextFocus = self.lastFocus.copy()
            else:
                nextFocus[1] = len(self.labels[nextFocus[0]]) - 1

        self.focus(nextFocus[0],nextFocus[1])
        self.changeGfLeg()

    def focus(self, set, leg):
        if len(self.labels) > set and len(self.labels[set]) > leg:
            self.labels[self.lastFocus[0]][self.lastFocus[1]].configure(bg="white")
            self.labels[set][leg].configure(bg=self.focusColor)
            self.lastFocus[0] = set
            self.lastFocus[1] = leg

    def __init__(self, gf):
        Frame.__init__(self, gf, bg="#e8e8e8")

        players = len(gf.game.players)
        self.labels = []
        self.lastFocus = [0,0]
        self.gf = gf
        self.focusColor = "#ffd79c"
        self.igw = True
        self.averageScores = []
        
        self.history = Frame(self, bg="#000cd9",borderwidth=1, relief="solid")
        self.history.pack(side="left", fill="y")
        self.history.grid_rowconfigure(0,weight = 1)

        self.addStats(players)

        results = []
        for player in range(0,players):          
            results.append(0)

        for i, set in enumerate(gf.game.sets):
            self.labels.append([])
            self.addSet(set, i, results)

        self.addResult(results, 0, 1)
        self.focus(self.gf.currentSet,self.gf.currentLeg)

    def setStats(self, player, tag, value):
        if tag == 3:
            self.averageScores[player][tag].set("{:.1f}".format(value))
        else:
            self.averageScores[player][tag].set("{:.0f}".format(value))

    def addStats(self, players):
        self.stats = Frame(self, bg="white",borderwidth=1, relief="solid")
        self.stats.pack(side="right", fill="y")
        titles = ["180", "HF", "SL", "AVG"]
        widths = [42, 42, 42, 100]

        for player in range(players):
            for col in range(4):
                self.averageScores.append([])
                self.stats.grid_rowconfigure(player, weight = 1)

                tmp = Frame(self.stats, bg="white",borderwidth=1, relief="solid")
                tmp.grid(row=player, column=col, sticky="nesw")

                averageScore = StringVar(tmp)
                averageScore.set('0.0')

                #titLabel = Label(tmp, text=titles[col], fg="black", bg="white", font=(dartConstants.DART_FONT,8))
                titLabel = TextLabel(tmp, text=titles[col], height=14, font=(dartConstants.DART_FONT,10), width=widths[col])
                titLabel.pack() #grid(row=0, column=0)
                #tmp.grid_rowconfigure(0, weight = 1)

                avgLabel = TextLabel(tmp, textVariable=averageScore, width=widths[col], text="0") #, textvariable=averageScore, fg="black", bg="white", font=(dartConstants.DART_FONT,20))
                avgLabel.pack() # grid(row=1, column=0)
                #tmp.grid_rowconfigure(1, weight = 1)

                self.averageScores[player].append(averageScore)

    def addResult(self, res, col, borderwidth=0):
        tmp = Frame(self.history, bg="#00fcd9",borderwidth=borderwidth, relief="solid")
        
        
        tmp.grid(row=0, column=col, sticky="nesw")
        
        for player, score in enumerate(res):
            
            tmp.grid_rowconfigure(player, weight = 1)
            nameLabel = Label(tmp, fg="black", bg="white",borderwidth=1, relief="solid", font=(dartConstants.DART_FONT,TEXTSIZE), text=self.gf.game.players[player].name)
            nameLabel.grid(row=player, column=0, sticky="nesw")
            allLabel = Label(tmp, fg="red", bg="#e8e8e8",borderwidth=1, relief="solid", font=(dartConstants.DART_FONT,TEXTSIZE), text=score)
            allLabel.grid(row=player, column=1, sticky="nesw")

    def addSet(self, set, setCount, oar):
        tmp = Frame(self.history,borderwidth=1, relief="solid", bg="#fffcd9")
        tmp.grid(row=0, column=setCount+2, sticky="nesw")
        self.history.grid_rowconfigure(0, weight = 1)

        results = []
        for player in self.gf.game.players:
            
            results.append(0)

        for i, leg in enumerate(set.legs):
            winner = leg.getWinner()
            text = "läuft"
            row = 0

            if winner != -1:
                results[winner] += 1
                text = leg.getWinDarts(winner)
                row = winner
                if results[winner] == set.nLegs:
                    oar[winner] += 1   
                else:
                    winner = -1    
            
            for player in range(0,len(results)):
                tmp.grid_rowconfigure(player,weight = 1)

            label = Label(tmp, bg="white", font=(dartConstants.DART_FONT,TEXTSIZE), text=text)

            label.grid(row=row, column=i, sticky="nesw")
            self.labels[setCount].append(label)     

        for player in range(0,len(results)):
            fg = "black"
            if player == winner:
                fg = "red"
            allLabel = Label(tmp, fg = fg, bg="white",borderwidth=1, relief="solid", font=(dartConstants.DART_FONT,TEXTSIZE), text=results[player])
            allLabel.grid(row=player, column=len(set.legs), sticky="nesw")
