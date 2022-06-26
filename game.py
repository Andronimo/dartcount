import dartConstants
from leg import Leg
from set import Set

class Options:
    def __init__(self, startOptions):
        self.options = startOptions

class Player:
    def __init__(self, name):
        self.name = name

class Game:
    def __init__(
        self, players, nSets=3, nLegs=3, options=dartConstants.DOUBLE_OUT, points=501
    ):
        self.nLegs = nLegs
        self.winPoints = points
        self.options = options
        self.players = []
        for player in players:
            self.players.append(Player(player))
        self.nSets = nSets
        self.sets = [Set(nLegs, len(players), options, self.winPoints, 0)]
        self.currentSet = 0

    def result(self):
        print(self.players[0].name + " " + self.players[1].name)
        print(self.sets[0].result())

    def addScore(self, score):
        self.sets[self.currentSet].addScore(score)
        self.checkFinished()

    def addNewScore(self, player, row, score):
        if not self.checkFinished():
            self.sets[self.currentSet].addNewScore(player, row, score)
            self.checkFinished()

    def changeScore(self, set, leg, player, rnd, score):
        self.sets[set].changeScore(leg, player, rnd, score)
        self.checkFinished()

    def getRestScore(self, player, row):
        return self.sets[self.currentSet].getRestScore(player, row)

    # def getLegs(self, player):
    #     return self.sets[self.currentSet].getLegs(player)

    def score(self, player):
        score = 0
        for set in self.sets:
            if set.getWinner() == player:
                score += 1
        return score

    def checkFinished(self, nextSet=False):
        if self.sets[self.currentSet].checkFinished(nextSet):

            fin = False
            for player in range(0, len(self.players)):
                if self.score(player) == self.nSets:
                    fin = True

            if fin:
                pass
            else:
                if nextSet:
                    startPlayer = len(self.sets) % len(self.players)
                    self.sets.append(Set(self.nLegs, len(self.players), self.options, self.winPoints, startPlayer))
                    self.currentSet += 1

    def getCurrentPosition(self):
        position = [self.currentSet]
        position.extend(self.sets[self.currentSet].getCurrentPosition())
        return position

    def getCurrentLeg(self):
        return self.sets[self.currentSet].getCurrentLeg()

    def getLeg(self, set, leg):
        return self.sets[set].getLeg(leg)

    def getSet(self, set):
        return self.sets[set]

    def getAverage(self, player, rnd):
        darts = 0
        points = 0

        for set in self.sets:
            data = set.getData(player, rnd)
            darts += data[0]
            points += data[1]

        if darts == 0:
            return 0

        return round(300 * points / darts) / 100

    def getScoreInRange(self, player, minS, maxS, checkout=0):
        scores = 0

        for set in self.sets:
            scores += set.getScoreInRange(player, minS, maxS, checkout)

        return scores

    def getBestLeg(self, player):
        bestLeg = -1

        for set in self.sets:
            darts = set.getBestLeg(player)
            if bestLeg == -1 or (darts != -1 and darts < bestLeg):
                bestLeg = darts

        if bestLeg == -1:
            return 0

        return bestLeg

    def getLastSet(self):
        return len(self.sets) - 1