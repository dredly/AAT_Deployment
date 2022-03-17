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
        self.points += points + (points * (self.streak / 10)) + (50 / self.rank)
        # self.streak += 1

    def deductPoints(self, points):
        self.points -= points + (50 / self.rank)

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

    def setStreak(self, streak):
        self.streak = streak



if __name__ == "__main__":
    bob = User(1, "Bob", 1000, 1, 1)
    alexa = User(2, "Alexa", 1000, 1, 2)
    echo = User(3, "Echo", 1000, 1, 3)

    users = [bob, alexa, echo]
    possiblePoints = [10, 20, 50, 100]

    while True:
        # 70% chance of user losing streak
        streaker = random.randrange(10)
        if streaker > 2:
            bob.setStreak(bob.getStreak() + 1)
            if bob.getStreak() > 7:
                with open("aat/legendary_gamification/awards.txt", "a") as f:
                    f.write(f"Bob has earned Loyalty\n")
        else:
            bob.setStreak(1)

        streaker = random.randrange(10)
        if streaker > 2:
            alexa.setStreak(alexa.getStreak() + 1)
            if alexa.getStreak() > 7:
                with open("aat/legendary_gamification/awards.txt", "a") as f:
                    f.write(f"Alexa has earned Loyalty\n")
        else:
            alexa.setStreak(1)

        streaker = random.randrange(10)
        if streaker > 2:
            echo.setStreak(echo.getStreak() + 1)
            if echo.getStreak() > 7:
                with open("aat/legendary_gamification/awards.txt", "a") as f:
                    f.write(f"Echo has earned Loyalty\n")
        else:
            echo.setStreak(1)

        # 50% chance of answer being right
        future = random.randrange(2)
        if future == 0:
            bob.addPoints(possiblePoints[random.randrange(4)])
            if bob.getPoints() >= 1200:
                with open("aat/legendary_gamification/awards.txt", "a") as f:
                    f.write(f"Bob has earned the achievement 'Would you like some py?'\n")
        else: 
            bob.deductPoints(possiblePoints[random.randrange(4)])
            if bob.getPoints() <= 900:
                with open("aat/legendary_gamification/awards.txt", "a") as f:
                    f.write(f"Bob has earned the achievement 'Snaking my way downtown'\n")

        future = random.randrange(2)
        if future == 0: 
            alexa.addPoints(possiblePoints[random.randrange(4)])
            if alexa.getPoints() >= 1200:
                with open("aat/legendary_gamification/awards.txt", "a") as f:
                    f.write(f"Alexa has earned the achievement 'Would you like some py?'\n")
        else: 
            alexa.deductPoints(possiblePoints[random.randrange(4)])
            if alexa.getPoints() <= 900:
                with open("aat/legendary_gamification/awards.txt", "a") as f:
                    f.write(f"Alexa has earned the achievement 'Snaking my way downtown'\n")

        future = random.randrange(2)
        if future == 0:
            echo.addPoints(possiblePoints[random.randrange(4)])
            if echo.getPoints() >= 1200:
                with open("aat/legendary_gamification/awards.txt", "a") as f:
                    f.write(f"Echo has earned the achievement 'Would you like some py?'\n")
        else: 
            echo.deductPoints(possiblePoints[random.randrange(4)])
            if echo.getPoints() <= 900:
                with open("aat/legendary_gamification/awards.txt", "a") as f:
                    f.write(f"Echo has earned the achievement 'Snaking my way downtown'\n")


        for userTop in users:
            for userBottom in users:
                if userTop.getPoints() < userBottom.getPoints():
                    if userTop.getRank() < userBottom.getRank():
                        switchRank(userTop, userBottom)

        with open("aat/legendary_gamification/ranks.txt", "w") as f:
            f.write(f"{bob.getRank()}:Bob:{bob.getPoints()}\n{alexa.getRank()}:Alexa:{alexa.getPoints()}\n{echo.getRank()}:Echo:{echo.getPoints()}")

        print(f"Bob: {bob.getPoints()}, Rank: {bob.getRank()}, Streak: {bob.getStreak()}")
        print(f"Alexa: {alexa.getPoints()}, Rank: {alexa.getRank()}, Streak: {alexa.getStreak()}")
        print(f"Echo: {echo.getPoints()}, Rank: {echo.getRank()}, Streak: {echo.getStreak()}")
        print("-" * 20)
        time.sleep(1)