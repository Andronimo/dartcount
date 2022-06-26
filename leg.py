import itertools

class Leg:
    def __init__(self, points, players, options, start):
        self.winPoints = points
        self.nPlayers = players
        self.options = options
        self.start = start
        self.points = []
        self.lastDarts = []
        for i in range(0, players):
            new = []
            self.points.append(new)
            self.lastDarts.append(0)
        self.currentPlayer = start

    def changeBeginRight(self):
        self.start = (self.start + 1) % self.nPlayers
        self.nextPlayer()

    def addScore(self, score):
        self.points[self.currentPlayer].append(score)
        self.nextPlayer()

    def nextPlayer(self):
        self.currentPlayer = self.start

        self.currentPlayer = (self.start + 1) % self.nPlayers
        while self.currentPlayer != self.start:
            if len(self.points[self.currentPlayer]) < len(self.points[self.start]):
                break
            self.currentPlayer = (self.currentPlayer + 1) % self.nPlayers

    def possibleScore(self, player, score, row):

        #if self.checkFinished():
        #    return False

        if (self.getRestScore(player, row) - score) < 0:
            return False

        if (self.getRestScore(player, row) - score) == 1:
            return False
        
        if score > 180:
            return False

        if score < 0:
            return False

        if (self.getRestScore(player, row) - score) == 0:
            if score > 170:
                return False
            if score in [159, 161, 162, 163, 165, 166, 168, 169]:
                return False
        else:
            if score in [161, 163, 166, 169, 172, 173, 175, 176, 178, 179]:
                return False       

        return True

    def addNewScore(self, player, row, score):

        if len(self.points[player]) > row:
            if self.possibleScore(player, score, row-1):
                self.points[player][row] = score
                return True
        else:
            if len(self.points[player]) == row and player == self.currentPlayer:
                if self.possibleScore(player, score, -1):
                    self.points[player].append(score)
                    self.nextPlayer()
                    return True
        
        return False
        
    def allPoints(self, n):
        return sum(self.points[n])

    def result(self):
        return "{} : {}".format(self.allPoints(0), self.allPoints(1))

    def changeScore(self, player, rnd, score):
        self.points[player][rnd] = score

    def checkFinished(self):

        for p in range(0, self.nPlayers):

            if self.allPoints(p) == self.winPoints:
                return True
        
        return False

    def getRestScore(self, player, row):
        if row == -1:
            return self.winPoints - self.allPoints(player)

        rest = self.winPoints

        for num in itertools.islice(self.points[player],0,row+1):
            rest -= num

        return rest

    def getCurrentPosition(self):
        return [self.currentPlayer, len(self.points[self.currentPlayer])]
    
    def getScores(self):
        scores = []
        for player in range(0,self.nPlayers):
            rest = self.winPoints
            playerScores = []
            
            for score in self.points[player]:
                rest -= score
                playerScores.append([score, rest])

            scores.append(playerScores)

        return scores

    def getWinner(self):
        for i in range(0, len(self.points)):
            if self.allPoints(i) == self.winPoints:
                return i

        return -1

    def getWinDarts(self, player):
        if self.allPoints(player) == self.winPoints:
            return 3 * len(self.points[player]) - self.lastDarts[player]

        return -1

    def getScoreInRange(self, player, minS, maxS, checkout):
        scores = 0

        if checkout == 1:
            if self.getWinner() == player and self.points[player][len(self.points[player])-1] >= minS:
                return 1
        elif checkout == 2:
            darts = self.getWinDarts(player)
            if darts >= minS and darts <= maxS:
                return 1 
        else:
            for score in self.points[player]:
                if score >= minS and score <= maxS:
                    scores += 1 

        return scores

    def getData(self, player, rnd):
        darts = 0
        points = 0

        if rnd == -1:
            darts = 3 * len(self.points[player])
            points = self.allPoints(player)
            darts -= self.lastDarts[player]
        else:
            darts = 3 * min(rnd, len(self.points[player]))
            points = sum(itertools.islice(self.points[player], 0, rnd))
            if len(self.points[player]) == rnd:
                darts -= self.lastDarts[player]

        return [darts, points]

    def getRows(self):
        return len(self.points[0])