from leg import Leg

class Set:
    def __init__(self, legs, players, options, points, start):
        self.nLegs = legs
        self.points = points
        self.options = options
        self.nPlayers = players
        self.start = start
        self.legs = [Leg(self.points, self.nPlayers, self.options, self.start)]
        self.currentLeg = 0

    def addScore(self, score):
        self.legs[self.currentLeg].addScore(score)

    def addNewScore(self, player, row, score):
        self.legs[self.currentLeg].addNewScore(player, row, score)

    def result(self):
        res = ""
        for leg in self.legs:
            res += leg.result() + "\n"
        return res

    def changeScore(self, leg, player, rnd, score):
        self.legs[leg].changeScore(player, rnd, score)

    def score(self, player):
        score = 0
        for leg in self.legs:
            if leg.getWinner() == player:
                score += 1
        return score

    def getWinner(self):

        for player in range(0, self.nPlayers):
            if self.score(player) == self.nLegs:
                return player
        return -1

    def checkFinished(self, nextLeg=False):
        
        if self.legs[self.currentLeg].checkFinished():
   
            for player in range(0, self.nPlayers):
                if self.score(player) == self.nLegs:
                    return True

            if nextLeg:
                startPlayer = (self.start + len(self.legs)) % self.nPlayers
                self.legs.append(Leg(self.points, self.nPlayers, self.options, startPlayer))
                self.currentLeg += 1

        return False

    def getRestScore(self, player, row):
        return self.legs[self.currentLeg].getRestScore(player, row)

    def getLegs(self, player):
        legs = 0

        for i in range(0, self.currentLeg):
            if self.legs[i].allPoints(player) == self.points:
                legs += 1

        return legs

    def getCurrentPosition(self):
        position = [self.currentLeg]
        position.extend(self.legs[self.currentLeg].getCurrentPosition())
        return position

    def getCurrentLeg(self):
        return self.legs[self.currentLeg]

    def getLeg(self, leg):
        return self.legs[leg]

    def getScoreInRange(self, player, minS, maxS, checkout):
        scores = 0

        for leg in self.legs:
            scores += leg.getScoreInRange(player, minS, maxS, checkout)

        return scores

    def getData(self, player, rnd):
        darts = 0
        points = 0

        for leg in self.legs:
            data = leg.getData(player, rnd)
            darts += data[0]
            points += data[1]

        return [darts, points]

    def getBestLeg(self, player):
        bestLeg = -1

        for leg in self.legs:
            darts = leg.getWinDarts(player)
            if bestLeg == -1 or (darts != -1 and darts < bestLeg):
                bestLeg = darts

        return bestLeg

    def getLastLeg(self):
        return len(self.legs) - 1