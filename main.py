import random

GOAL = 100 #points
# 2 player
# starting player order is decided randomly
# 1 lose points from this turn
ROLL = "roll"
ENDTURN = "endTurn"


class DiceGamePig:

    def __init__(self):
        #self.scores = [0,0] # 2 players
        #self.currentPlayer = random.randint(0,1) # choose starting player at random
        #self.turnTotal = 0 # points in current turn for the current player
        #self.win = False # no winner at the start
        self.reset()

    def getState(self):
        return (self.scores[0], self.scores[1], self.turnTotal, self.currentPlayer) # score of player 1 and 2, points in current turn of current player, current player
        # self.scores, self.turnTotal, self.currentPlayer

    def roll(self):
        dice = random.randint(1,6)
        if dice == 1:
            self.switchCurrentPlayer()
        else:
            self.turnTotal += dice
            if dice == 6:
                self.forcedRoll = True
            else:
                self.forcedRoll = False
            #if dice == 6:
            #    self.roll()

    def switchCurrentPlayer(self):
        self.turnTotal = 0
        self.forcedRoll = False
        self.currentPlayer = (self.currentPlayer + 1) % 2

        
    def endTurn(self):
        self.scores[self.currentPlayer] += self.turnTotal
        if self.scores[self.currentPlayer] >= GOAL: # game can only be won if the player ends the turn
            self.win = True
        self.switchCurrentPlayer()

    def turn(self, action):

        if self.forcedRoll or action == ROLL:
            self.roll()
        elif action == ENDTURN:
            self.endTurn()
        
        return self.getState()

    def reset(self):
        self.scores = [0,0] # 2 players
        self.currentPlayer = random.randint(0,1) # choose starting player at random
        self.turnTotal = 0 # points in current turn for the current player
        self.win = False # no winner at the start
        self.forcedRoll = False # no forced roll at the start
        return self.getState()



#game = DiceGamePig()
#while game.win == False:
#    game.turn(random.choice([ROLL, ENDTURN]))
#print(game.scores,game.win)

####

# ai was used for the following:
game = DiceGamePig()

HUMAN = 30   # you are player 0

while False:#while not game.win:
    print("\n------------------")
    print("Scores:", game.scores)
    print("Current player:", game.currentPlayer)
    print("Turn total:", game.turnTotal)

    if game.currentPlayer == HUMAN:
        action = input("Choose action (roll / endTurn): ").strip()

        while action not in [ROLL, ENDTURN]:
            action = input("Invalid. Choose (roll / endTurn): ").strip()

    else:
        action = random.choice([ROLL, ENDTURN])
        print("Opponent chooses:", action)

    game.turn(action)

#print("\nFinal scores:", game.scores)
#print("Winner is Player", 0 if game.scores[0] >= GOAL else 1)


########
from collections import defaultdict

class QLearningAgent:
    def __init__(self):
        self.Q = defaultdict(lambda: {ROLL: 0, ENDTURN: 0})
        self.alpha = 0.1
        self.gamma = 0.95
        self.epsilon = 0.1

    def chooseAction(self, state):

        if random.random() < self.epsilon:
            return random.choice([ROLL, ENDTURN])

        return max(self.Q[state], key=self.Q[state].get)

    def update(self, s, a, r, s_next):
        maxNext = max(self.Q[s_next].values())
        self.Q[s][a] += self.alpha * (
            r + self.gamma * maxNext - self.Q[s][a]
        )


def dummy(state):
    return random.choice([ROLL, ENDTURN])
    #turnTotal = state[2]
    #if turnTotal < 15:
    #    return ROLL
    #else:
    #    return ENDTURN

def train(agent, episodes):
    game = DiceGamePig()

    for _ in trange(episodes, desc="Training"):
        state = game.reset()

        while not game.win:
            currentPlayer = game.currentPlayer # because the current player may update after taking the turn
            previousScore = game.scores[0] # because the score might update

            if currentPlayer == 0: # player 0 is always our agent, but he is not always the starting player
                # because the starting player is chosen at random (either player 0 or 1)
                action = agent.chooseAction(state)
            else:
                action = dummy(state)

            nextState = game.turn(action) # here the current player might swap

            reward = 0
            if game.win:
                if game.scores[0] >= GOAL:
                    reward = 1
                else:
                    reward = -1
            else:
                reward = (game.scores[0] - previousScore) / 100 # reward for gaining points
            
            if currentPlayer == 0:
                agent.update(state, action, reward, nextState)
            

            #if game.currentPlayer == 1:  # agent just played... but the agent can do multiple actions
                #agent.update(state, action, reward, nextState)

            state = nextState


def evaluate(agent, games):
    game = DiceGamePig()
    wins = 0

    for _ in range(games):
        state = game.reset()

        while not game.win:
            if game.currentPlayer == 0:
                action = agent.chooseAction(state)
            else:
                action = dummy(state)

            state = game.turn(action)

        if game.scores[0] >= GOAL:
            wins += 1

    return wins / games

def playAgainstAgent(agent):
    game = DiceGamePig()

    while not game.win:
        print("\n------------------")
        print("Scores:", game.scores)
        print("Current player:", game.currentPlayer)
        print("Turn total:", game.turnTotal)

        if game.currentPlayer == 0:
            action = agent.chooseAction(game.getState())
            print("Agent chooses:", action)
        else:
            if game.forcedRoll: # automatically choose roll action if 6 is rolled
                print("You rolled a 6, you must roll again.")
                action = ROLL
            else:
                action = input("Choose (roll / endTurn): ").strip()
                while action not in [ROLL, ENDTURN]:
                    action = input("Invalid. Choose (roll / endTurn): ").strip()           

        game.turn(action)

    print("\nFinal scores:", game.scores)
    print("Winner is", "Agent" if game.scores[0] >= GOAL else "Human")



import pickle
import os
from tqdm import trange

def saveAgent(agent, filename):
    with open(filename, "wb") as f:
        pickle.dump(dict(agent.Q), f)

def loadAgent(agent, filename):
    with open(filename, "rb") as f:
        data = pickle.load(f)
    agent.Q = defaultdict(lambda: {ROLL: 0, ENDTURN: 0}, data)

def trainAndSave(episodesList):
    for episodes in episodesList:
        filename = f"agent_{episodes}.pkl"
        if not os.path.exists(filename):
            agent = QLearningAgent()
            train(agent, episodes)
            saveAgent(agent, filename)
            print(f"Saved {filename}")
        else:
            print(f"File {filename} already exists")




if __name__ == "__main__":
    agent = QLearningAgent()

    #train(agent, episodes=100000)
    
    #agent.epsilon = 0 # to disable exploration during evaluation
    #winrate = evaluate(agent, games=1000)
    #print("Winrate:", winrate)

    #playAgainstAgent(agent)

    episodesList = [100, 1000, 10000, 100000, 1000000, 10000000, 100000000, 1000000000 ]
    trainAndSave(episodesList) # A .pkl file is a saved Python object in binary form using the pickle module.
    # converting your Python object into bytes and saving it to disk

    for e in episodesList:
        loadAgent(agent, f"agent_{e}.pkl")
        print(evaluate(agent, 10000))

    playAgainstAgent(agent)


'''Training: 100%|██████████████████████████| 100/100 [00:00<00:00, 2743.46it/s]
Saved agent_100.pkl
Training: 100%|████████████████████████| 1000/1000 [00:00<00:00, 3049.22it/s]
Saved agent_1000.pkl
File agent_10000.pkl already exists
File agent_100000.pkl already exists
Training: 100%|██████████████████| 1000000/1000000 [02:25<00:00, 6890.10it/s]
Saved agent_1000000.pkl
Training: 100%|██████████████| 10000000/10000000 [1:05:45<00:00, 2534.82it/s]
Saved agent_10000000.pkl
File agent_10000000.pkl already exists'''