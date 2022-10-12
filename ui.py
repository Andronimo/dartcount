from tkinter import *
from game import Game
import dartConstants
from askFrame import AskFrame
from menuFrame import MenuFrame
from command import Command
from server import *
from textLabel import *
import queue, threading, json
from resultPane import ResultPane
from leg import Leg
import os
import pickle
import platform
from os.path import exists

def onFrameConfigure(canvas):
    '''Reset the scroll region to encompass the inner frame'''
    canvas.configure(scrollregion=canvas.bbox("all"))
    canvas.itemconfigure("grid", width=canvas.winfo_width()+10)

def scoreInput(gf, player, row, score, focus, checkDarts=0):
    
    if AskFrame.instance == True:
        return

    leg = gf.getCurrentLeg()
    position = [player, row]
    wasFinished = leg.checkFinished()

    if leg.addNewScore(player, row, score):
        save_object(gf.game, "autosave.dat")

    gf.setScoreEntries()

    if (not wasFinished) and leg.checkFinished():
        if checkDarts > 0:
            gf.endLeg(player, checkDarts, position)
        else:
            root.focus_set()
            AskFrame(["Checkdarts?"], root, lambda d:gf.endLeg(player, d[0], position)) 
    else:
        gf.scores(player)

        if focus:
            gf.setCurrentFocus(row)

def scoreInputFunc(gf, player, row, focus):
    gf.inputEntries[player][row].selection_clear()
    if True == gf.inputScores[player][row].get().isdigit():
        score = int(gf.inputScores[player][row].get())

        if 0 <= score <= 180:
            scoreInput(gf, player, row, score, focus)   

def changeBeginRight(gf):
    gf.getCurrentLeg().changeBeginRight()
    gf.setCurrentFocus(0)

def make_lambda(gf, i, row, focus):
    return lambda _: scoreInputFunc(gf, i, row, focus)

def make_keydown_lambda(gf, i, row):
    return lambda event: keydown(event.keysym, gf, i, row)

def evaluateMenu(cmd, gf, player, row):
    if cmd == "cancel":
        gf.inputEntries[player][row].focus_set()
    else:
        if cmd.isdigit():
            scoreInput(gf, player, row, int(cmd), True)
        else:
            keydown(cmd, gf, player, row)

def showMenu(menu, gf, player, row):
    root.focus_set()
    MenuFrame(menu, root, lambda c:evaluateMenu(c, gf, player, row))

def make_menu_lambda(menu, gf, player, row):
    return lambda event: showMenu(menu, gf, player, row)

def keydown(cmd, gf, player, row):

    if cmd == "KP_Enter":
        scoreInputFunc(gf, player, row, True)

    if cmd == "KP_Up":
        if row > 0:
            gf.inputEntries[player][row].selection_clear()
            gf.inputEntries[player][row-1].focus_set()
            gf.inputEntries[player][row-1].selection_range(0, END)
            gf.scrollToRow(row-1)
        else:
            gf.scrollToRow(0)
            gf.rp.takeFocus()
    
    if cmd == "KP_Down":
        if row < len(gf.getCurrentLeg().points[player]):
            gf.inputEntries[player][row].selection_clear()
            gf.inputEntries[player][row+1].focus_set()
            gf.inputEntries[player][row+1].selection_range(0, END)
            gf.scrollToRow(row+1)

    if cmd == "KP_Left":
        if player > 0:
            gf.inputEntries[player][row].selection_clear()
            gf.inputEntries[player-1][row].focus_set()
            gf.inputEntries[player-1][row].selection_range(0, END)

    if cmd == "KP_Right":
        if player < (len(gf.inputEntries) - 1):
            gf.inputEntries[player][row].selection_clear()
            gf.inputEntries[player+1][row].focus_set()
            gf.inputEntries[player+1][row].selection_range(0, END)

    if cmd in dartConstants.shortcuts:
        scoreInput(gf, player, row, dartConstants.shortcuts[cmd], True) 
    else:
        restScore = gf.game.getCurrentLeg().getRestScore(player,-1)

        if cmd == "F9" or cmd == "KP_Subtract":
            if False == gf.inputScores[player][row].get().isdigit():
                gf.inputEntries[player][row].focus_set()
                return
            score = int(gf.inputScores[player][row].get())
            scoreInput(gf, player, row, restScore - score, True)
        if cmd == "F10":
            scoreInput(gf, player, row, restScore, True, 1)
        if cmd == "F11":
            scoreInput(gf, player, row, restScore, True, 2)
        if cmd == "F12":
            scoreInput(gf, player, row, restScore, True, 3)
        if cmd == "newGame":
            globalShortcut()
        if cmd == "quit":
            root.destroy()  
        if cmd == "shutdown":
            os.system("shutdown -h now")     

class GameFrame(Frame):

    def getCurrentLeg(self):
        return self.game.getLeg(self.currentSet, self.currentLeg)

    def getCurrentSet(self):
        return self.game.getSet(self.currentSet)

    def endLeg(self, player, checkDarts, position):
        cDarts = checkDarts

        if isinstance(checkDarts, str):
            if checkDarts.isnumeric():
                cDarts = int(checkDarts)
            else:
                self.removeScore(position)
                return
        
        if cDarts < 1 or cDarts > 3:
            self.removeScore(position)
            return

        self.getCurrentLeg().lastDarts[player] = 3 - cDarts
        self.game.checkFinished(True)
        self.currentSet = len(self.game.sets) - 1
        self.currentLeg = len(self.game.sets[self.currentSet].legs) - 1
        self.canvas.yview_moveto(0)
        self.refreshView()
        self.scores(player)
        self.rp.grid_forget()
        self.rp.grid_remove()
        self.initGameHistory()

    def removeScore(self, position):
        self.getCurrentLeg().removeScore(position)
        self.inputScores[position[0]][position[1]].set("")
        self.restScores[position[0]][position[1]].set("")
        self.refreshView()

    def refreshView(self):
        self.setScoreEntries()
        pos = self.getCurrentLeg().getCurrentPosition()
        self.setCurrentFocus(pos[1])

    def scrollToRow(self, row):
        height = self.canvas.winfo_height()
        heightEntry = self.inputEntries[0][0].winfo_height()

        self.reset_scrollregion(0)

        if height == 1:
            height = 563        

        if row > 2:
            pos = ((row+1) * heightEntry - height) / (len(self.inputEntries[0]) * heightEntry)
            
            # print(row)
            # print(height)
            # print(pos)
            # print(len(self.inputEntries[0]))
            
            self.canvas.yview_moveto(pos)
        else:
            self.canvas.yview_moveto(0)

        while len(self.inputEntries[0]) < row+7:
            self.addScoreTableRow()  

    def grabFocus(self):
        if self.doGrabFocus:
            self.setCurrentFocus(0)
            self.doGrabFocus = False

    def setCurrentFocus(self, row):
        yes = 0
        position = self.getCurrentLeg().getCurrentPosition()

        print(position)

        while len(self.inputEntries[0]) < position[1]+4:
            self.addScoreTableRow()
            yes += 1
        
        self.setScoreEntries()

        if position[0] < len(self.inputEntries):
            if position[1] < len(self.inputEntries[position[0]]):
                self.inputEntries[position[0]][position[1]].focus_set()

        if yes > 1:
            self.doGrabFocus = True
        else:
            self.scrollToRow(position[1])

    def scores(self, player):
        self.rp.setStats(player, 0, self.game.getScoreInRange(player, 180, 180))
        self.rp.setStats(player, 1, self.game.getScoreInRange(player, 101, 170, 1))
        self.rp.setStats(player, 2, self.game.getScoreInRange(player, 9, 18, 2))
        self.rp.setStats(player, 3, self.game.getAverage(player, -1))
        #self.averageScores[player][0].set("{}".format(self.game.getAverage(player, 3)))
        #self.averageScores[player][1].set("{}".format(self.game.getAverage(player, -1)))
        #self.averageScores[player][2].set("{}".format(self.game.getBestLeg(player)))

    def setScoreEntries(self):
        scores = self.game.getLeg(self.currentSet, self.currentLeg).getScores()

        for player in range(0,len(self.game.players)):
            playerScores = scores[player]
            for row in range(0,len(self.inputScores[0])):
                if row < len(playerScores):
                    self.inputScores[player][row].set("{}".format(playerScores[row][0]))
                    self.restScores[player][row].set("{}".format(playerScores[row][1]))
                else:
                    self.inputScores[player][row].set("")
                    self.restScores[player][row].set("")

            legResultLabel = self.legResults[player]
            legResultLabel.set("{}".format(self.getCurrentSet().score(player)))

            if len(playerScores) > 0:
                self.bigScores[player].set("{}".format(playerScores[-1][1]))
            else:
                self.bigScores[player].set("{}".format(self.game.winPoints))

    def __init__(self, game):
        super().__init__(bg="white")

        self.game = game
        self.shortcuts_1 = [["1 Dart", "F10"],["2 Dart", "F11"],["3 Dart", "F12"],["Rest", "F9"],"41","45",["Neu", "newGame"],["Quit", "quit"],["Aus", "shutdown"],["Abbr","cancel"]]
        self.shortcuts_2 = ["0", "26","41","45","60","81","85","100", "180", ["Abbr","cancel"]]
        self.master.title("SDC Siegerland")
        self.currentSet = self.game.getLastSet()
        self.currentLeg = self.getCurrentSet().getLastLeg()
        self.pack(fill=BOTH, expand=True)
        self.inputScores = []
        self.inputEntries = []
        self.restScores = []
        self.restEntries = []
        self.legResults = []
        self.bigScores = []
        self.averageScores = []

        self.grid_columnconfigure(0, weight = 1)
        self.grid_rowconfigure(2, weight = 1)

        self.initArrays()
        self.initPlayerLabels()
        self.initGameHistory()
        self.initScoreTable()
        self.initBigScores()
        self.initStats()

        if self.getCurrentLeg().checkFinished():
            self.endLeg(0,3,[0,0])

        position = self.getCurrentLeg().getCurrentPosition()
        while len(self.inputEntries[0]) < position[1]+4:
            self.addScoreTableRow()

        self.setScoreEntries()
        self.doGrabFocus = True

    def initArrays(self):
        for player in self.game.players:
            self.inputScores.append([])
            self.inputEntries.append([])
            self.restScores.append([])
            self.restEntries.append([])
            self.averageScores.append([])

    def initPlayerLabels(self):
        playerLabelFrame = Frame(self)
        playerLabelFrame.grid(row=1, column=0, sticky="nesw")

        for i, player in enumerate(self.game.players):
            playerLabelFrame.grid_columnconfigure(i, weight = 1, uniform="fred")
            playerFrame = Frame(playerLabelFrame, borderwidth=2,relief="solid")
            playerFrame.grid(row=0, column=i, sticky="nesw")

            playerNameLabel = TextLabel(playerFrame, bg=playerFrame.cget("bg") ,height=100, text=player.name, font=(dartConstants.DART_FONT, 80), mode=1)
            playerNameLabel.pack(side=LEFT, padx=5, expand=False)

            legResult = StringVar()
            legResult.set("0")
            legResultLabel = TextLabel(playerFrame, bg=playerFrame.cget("bg"), textVariable=legResult, text="0", height=100, font=(dartConstants.DART_FONT, 80), mode=1)
            legResultLabel.pack(side=RIGHT, padx=5, pady=5, expand=False)
            self.legResults.append(legResult)

    def initGameHistory(self):
        self.rp = ResultPane(self)
        self.rp.grid(row=0, column=0, sticky="nesw")

        for player in range(len(self.game.players)):
            self.scores(player)

    def reset_scrollregion(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def initScoreTable(self):

        # Scoreboard with scrollbar
        scoringTable = Frame(self, width=50, bg="white")
        scoringTable.grid(row=2, column=0, sticky="nesw")

        self.canvas = Canvas(scoringTable, height=350,borderwidth=0, background="#fff3bf")
        self.scoreTableFrame = Frame(self.canvas, background="#ffffff")
        self.vsb = Scrollbar(scoringTable, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill=BOTH, expand=True)
        self.canvas.create_window((4,4), window=self.scoreTableFrame, anchor="nw", tags="grid")
        self.canvas.bind("<Configure>", lambda event, canvas=self.canvas: onFrameConfigure(self.canvas))
        self.scoreTableFrame.bind("<Configure>", self.reset_scrollregion)

        for row in range(0,self.game.getCurrentLeg().getRows()+7):
            self.addScoreTableRow()
        

    def addScoreTableRow(self):
        for column, player in enumerate(self.game.players):
            self.scoreTableFrame.grid_columnconfigure(2*column, weight = 1)
            self.scoreTableFrame.grid_columnconfigure((2*column)+1, weight = 1)

            row = len(self.inputScores[column])

            command = Command(self.game, column)
            self.inputScores[column].append(StringVar())
            entry = Entry(self.scoreTableFrame, validate="key", validatecommand=(root.register(command.validate()), '%P'), textvariable=self.inputScores[column][row], justify='center', font=(dartConstants.DART_FONT, 80))
            entry.grid(row=row, column=(2*column), sticky="nesw")
            entry.igw = True
            entry.bind('<Return>', make_lambda(self, column, row, True))
            entry.bind("<FocusOut>", make_lambda(self, column, row, False))
            entry.bind("<KeyPress>", make_keydown_lambda(self, column, row))
            entry.bind("<Key-KP_Multiply>", make_menu_lambda(self.shortcuts_2, self, column, row))
            entry.bind("<Key-KP_Divide>", make_menu_lambda(self.shortcuts_1, self, column, row))
            entry.bind("<Key-KP_Add>", lambda e: changeBeginRight(self))
            entry.bind("<Key-asterisk>", make_menu_lambda(self.shortcuts_2, self, column, row))
            entry.bind("<Key-slash>", make_menu_lambda(self.shortcuts_1, self, column, row))
            entry.bind("<Key-plus>", lambda e: changeBeginRight(self))
            self.inputEntries[column].append(entry)
            self.restScores[column].append(StringVar())
            scoreEntry = Entry(self.scoreTableFrame, textvariable=self.restScores[column][row], justify='center', font=(dartConstants.DART_FONT, 80))
            scoreEntry.grid(row=row, column=(2*column+1), sticky="nesw") 
            self.restEntries[column].append(scoreEntry) 

        self.canvas.configure(scrollregion=self.canvas.bbox("all"), height=root.winfo_height()-405)


    def initBigScores(self):
        bigScoreRowFrame = Frame(self, bg="white")
        bigScoreRowFrame.grid(row=3, column=0, sticky="nesw")

        i = 0
        for player in self.game.players:
            bigScoreRowFrame.grid_columnconfigure(i, weight = 1)

            bigScoreFrame = Frame(bigScoreRowFrame, bg="white", borderwidth=2,relief="solid")
            bigScoreFrame.grid(row=0, column=i, sticky="nesw")

            bigScore = StringVar()
            bigScore.set(self.game.winPoints)
            bigScoreLabel = TextLabel(bigScoreFrame, text=self.game.winPoints, textVariable=bigScore, font=(dartConstants.DART_FONT, 210), width=430, height=230, fixY=-6)
            bigScoreLabel.pack( anchor=CENTER)
            self.bigScores.append(bigScore)
            i += 1

    def initStats(self):
        statsRow = Frame(self, borderwidth=2,relief="solid")
        statsRow.grid(row=4, column=0, sticky="nesw")

        column = 0
        for player in self.game.players:
            # Score frame which shows the rest score
            statsRow.grid_columnconfigure(column, weight = 1)

            statsFrame = Frame(statsRow, bg="white")
            #statsFrame.grid(row=0, column=column, sticky="nesw")
            #statsFrame.grid_columnconfigure(0, weight = 1)

            stats = ["Average (3)", "Average (9)", "Best Leg"]

            for statCount, stat in enumerate(stats):
                label = Label(statsFrame, text='{}:'.format(stat), bg="white", font=(dartConstants.DART_FONT, 20))
                label.grid(row=statCount, column=0, sticky="w")
                label2 = Label(statsFrame, width=2, bg="white", font=(dartConstants.DART_FONT, 20))
                label2.grid(row=statCount, column=1, sticky="w")
                averageScore = StringVar()
                averageScore.set('0.0'.format(stat))
                avgLabel = Label(statsFrame, textvariable=averageScore, bg="white", font=(dartConstants.DART_FONT, 20))
                avgLabel.grid(row=statCount, column=2, sticky="w")
                self.averageScores[column].append(averageScore)
                
            column += 1

def globalShortcut():
    AskFrame(["Wie viele Spieler?", "Legs für Satzgewinn?"], root, initMenuCb)    

def newGame(nPLayers, legs, names=[], load=False):
    global app
    #game = Game(["Natalie", "Andre"])
    try:
        app.pack_forget()
        app.destroy() 
    except:
        pass

    game = None
    if load:
        if exists("autosave.dat"):
            game = load_object("autosave.dat")

    if game == None:
        players = []
        for i in range(0, nPLayers):
            players.append("{}".format(dartConstants.SPIELER[i]))

        if len(names) > 0:
            game = Game(names, nLegs=legs)
        else:
            game = Game(players, nLegs=legs)
    
    app = GameFrame(game)
    root.unbind("<KeyPress>")
    root.bind("<Alt-n>", lambda e: globalShortcut())

def initMenuCb(char):
    
    if True == char[0].isdigit():
        nPlayers = int(char[0])

        nLegs = 3
        if True == char[1].isdigit():
            nLegs = int(char[1])
        
        if nLegs < 1:
            nLegs = 3

        if 0 < nPlayers and 5 > nPlayers:
            newGame(nPlayers, nLegs)


def cycle():

    global app

    app.grabFocus()

    if MenuFrame.instance == False and AskFrame.instance == False and (root.focus_get() == None or not hasattr(root.focus_get(),"igw")):
        root.lift()
        root.attributes("-topmost", True)
        root.focus_force()
        root.grab_set()
        root.grab_release()
        if platform.system() == "Linux":
            os.system('./takeFocus')
        app.setCurrentFocus(0)
   
    root.after(2000, cycle)

def save_object(obj, filename):
    with open(filename, 'wb') as output:  # Overwrites any existing file.
        pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)

def load_object(filename):
    with open(filename, 'rb') as input:
        return pickle.load(input)
    return None

root = Tk()

root.attributes("-fullscreen", True)
root.geometry("1024x768+0+0")
newGame(2,["Heim","Gast"], load=True);
root.bind("<Alt-n>", lambda e: globalShortcut())

#q = queue.Queue()
#threading.Thread(target=openServer, daemon=True, args=(q,4905,)).start()

root.after(200, cycle)

root.mainloop()
