# src/services/economy.py

TAVERN_TABLE = {
    1: {"base": 5, "min": 2, "slots": 3},
    2: {"base": 7, "min": 4, "slots": 4},
    3: {"base": 8, "min": 5, "slots": 4},
    4: {"base": 9, "min": 6, "slots": 5},
    # می‌تونی بعداً tier 5 و 6 رو اضافه کنی
}

class Tavern:
    def __init__(self):
        self.tier = 1
        self.discount = 0

    def upgrade_cost(self):
        if self.tier >= len(TAVERN_TABLE):
            return 0  # نمی‌تونه بیشتر آپگرید بشه
        data = TAVERN_TABLE[self.tier]
        return max(data["base"] - self.discount, data["min"])

    def end_turn(self):
        if self.tier < len(TAVERN_TABLE):
            data = TAVERN_TABLE[self.tier]
            if data["base"] - self.discount > data["min"]:
                self.discount += 1

    def upgrade(self):
        if self.tier < len(TAVERN_TABLE):
            self.tier += 1
            self.discount = 0
            return True
        return False

    def get_shop_slots(self):
        return TAVERN_TABLE.get(self.tier, {"slots": 5})["slots"]


class Economy:
    MAX_GOLD = 10

    def __init__(self):
        self.turn = 1
        self.gold = 3
        self.tavern = Tavern()

    def start_turn(self):
        self.turn += 1
        # طلا هر turn +1 می‌شه تا حداکثر 10
        self.gold = min(self.gold + self.turn, self.MAX_GOLD)  # در بازی واقعی turn 1: 3, turn 2: 4, ..., turn 8: 10
        self.tavern.end_turn()
        print(f"Turn {self.turn} started | Gold: {self.gold} | Tier: {self.tavern.tier}")

    def can_spend(self, amount):
        return self.gold >= amount

    def spend(self, amount):
        if self.can_spend(amount):
            self.gold -= amount
            return True
        return False

    def gain(self, amount):
        self.gold = min(self.gold + amount, self.MAX_GOLD)

    def upgrade_tavern(self):
        cost = self.tavern.upgrade_cost()
        if self.gold < cost:
            print(f"Not enough gold! Need {cost}, have {self.gold}")
            return False

        self.gold -= cost
        self.tavern.upgrade()
        print(f"Tavern upgraded to Tier {self.tavern.tier}! Cost: {cost} | Gold left: {self.gold}")
        return True