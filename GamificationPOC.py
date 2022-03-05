import time

class User:
    def __init__(self, id, name, points, streak, rank=None) -> None:
        self.id = id
        self.name = name
        self.points = points
        self.rank = rank
        self.streak = streak

    def gainPoints(self):
        self.points += (10 * (self.streak / 10)) + (50 / self.rank)
        # self.streak += 1

    def increaseRank(self):
        self.rank += 1

    def getRank(self):
        return self.rank

    def getPoints(self):
        return int(self.points)

    def getStreak(self):
        return self.streak



if __name__ == "__main__":
    bob = User(1, "Bob", 0, 10, 2)
    alexa = User(2, "Alexa", 0, 30, 7)
    echo = User(3, "Echo", 0, 30, 10)

    while True:
        bob.gainPoints()
        alexa.gainPoints()
        echo.gainPoints()
        print(f"Bob: {bob.getStreak()} {bob.getPoints()}")
        print(f"Alexa: {alexa.getStreak()} {alexa.getPoints()}")
        print(f"Echo: {echo.getStreak()} {echo.getPoints()}")
        time.sleep(1)