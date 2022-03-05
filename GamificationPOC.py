import time
import random

def switchRank(user1, user2):
    temp = user1.getRank()
    user1.setRank(user2.getRank())
    user2.setRank(temp)

class User:
    def __init__(self, id, name, points, streak, rank=None) -> None:
        self.id = id
        self.name = name
        self.points = points
        self.rank = rank
        self.streak = streak

    def addPoints(self, points):
        self.points += (points * (self.streak / 10)) + (50 / self.rank)
        # self.streak += 1

    def deductPoints(self, points):
        self.points -= (points * (self.streak / 10)) + (50 / self.rank)

    def increaseRank(self):
        self.rank += 1

    def getRank(self):
        return self.rank

    def setRank(self, rank):
        self.rank = rank

    def getPoints(self):
        return int(self.points)

    def getStreak(self):
        return self.streak



if __name__ == "__main__":
    bob = User(1, "Bob", 1000, 1, 1)
    alexa = User(2, "Alexa", 1000, 1, 2)
    echo = User(3, "Echo", 1000, 1, 3)

    users = [bob, alexa, echo]
    possiblePoints = [10, 20, 50, 100]

    while True:
        future = random.randrange(2)
        if future == 0:
            bob.addPoints(possiblePoints[random.randrange(4)])
        else: 
            bob.deductPoints(possiblePoints[random.randrange(4)])

        future = random.randrange(2)
        if future == 0: 
            alexa.addPoints(possiblePoints[random.randrange(4)])
        else: 
            alexa.deductPoints(possiblePoints[random.randrange(4)])


        future = random.randrange(2)
        if future == 0:
            echo.addPoints(possiblePoints[random.randrange(4)])
        else: 
            echo.deductPoints(possiblePoints[random.randrange(4)])

        for userTop in users:
            for userBottom in users:
                if userTop.getPoints() < userBottom.getPoints():
                    if userTop.getRank() < userBottom.getRank():
                        switchRank(userTop, userBottom)

        print(f"Bob: {bob.getPoints()}, Rank: {bob.getRank()}")
        print(f"Alexa: {alexa.getPoints()}, Rank: {alexa.getRank()}")
        print(f"Echo: {echo.getPoints()}, Rank: {echo.getRank()}")
        print("-" * 20)
        time.sleep(1)