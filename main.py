import random

GOAL = 100 #points
# 2 player
# starting player order is decided randomly
# 1 lose points from this turn
ROLL = "roll"
ENDTURN = "endTurn"


class DiceGamePig:

    def __init__(self):
        self.scores = [0,0] # 2 players
        self.currentPlayer = random.randint(0,1) # choose starting player at random
        self.turnTotal = 0 # points in current turn for the current player
        self.win = False # no winner at the start

    def roll(self):
        dice = random.randint(1,6)
        if dice == 1:
            self.switchCurrentPlayer()
        else:
            self.turnTotal += dice

    def switchCurrentPlayer(self):
        self.turnTotal = 0
        self.currentPlayer = (self.currentPlayer + 1) % 2

        
    def endTurn(self):
        self.scores[self.currentPlayer] += self.turnTotal
        if self.scores[self.currentPlayer] >= GOAL: # game can only be won if the player ends the turn
            self.win = True
        self.switchCurrentPlayer()

    def turn(self, action):
        if action == ROLL:
            self.roll()
        if action == ENDTURN:
            self.endTurn()



game = DiceGamePig()
while game.win == False:
    game.turn(random.choice([ROLL, ENDTURN]))
print(game.scores,game.win)









