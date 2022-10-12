from game import Game

class Command():

    def __init__(self, game, player):
        self.cmdType = None
        self.game = game
        self.player = player

    def validate(self):
        return lambda value_if_allowed : value_if_allowed == "" or (value_if_allowed.isdigit() and int(value_if_allowed) < 502)
        #return lambda value_if_allowed : value_if_allowed == "" or (value_if_allowed.isdigit() and value_if_allowed[0] != '0' and int(value_if_allowed) < 181 and self.game.getCurrentLeg().possibleScore(self.player, int(value_if_allowed)))

    def callback(self, event):
        if event.keysym == "KP_Divide":
            self.cmdType = "special"
            
        if event.keysym == "KP_Left":
            return "BackSpace"
