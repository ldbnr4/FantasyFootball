import json


class Player:
    def __init__(self, name, position, team, opponent, owner):
        self.name = name
        self.position = position
        self.team = team
        self.owner = owner
        self.opponent = opponent
        self.nfl = 0
        self.number_fire = 0
        self.pros = 0
        self.cbs = 0
        self.ave = 0
        self.smart_ave = 0
        self.largest_deviation = 0
        self.smart_deviation = 0

    def set_nfl(self, projection):
        self.nfl = float(projection)

    def set_number(self, projection):
        self.number_fire = float(projection)

    def set_pros(self, projection):
        self.pros = float(projection)

    def set_cbs(self, projection):
        self.cbs = float(projection)

    def set_ave(self):
        values = [self.nfl, self.number_fire, self.pros, self.cbs]
        self.ave = round(sum(values) / len(values), 2)

    def set_smart_ave(self):
        values = [self.nfl, self.number_fire, self.pros, self.cbs]
        values_over_zero = sum(num > 0 for num in values)
        if values_over_zero > 0:
            self.smart_ave = round(sum(values) / values_over_zero, 2)

    def set_smart_deviation(self):
        possibles = [self.smart_deviation]
        if self.number_fire > 0:
            possibles.append(self.number_fire - self.pros)
            possibles.append(self.number_fire - self.nfl)
            possibles.append(self.number_fire - self.cbs)

        if self.pros > 0:
            possibles.append(self.pros - self.number_fire)
            possibles.append(self.pros - self.nfl)
            possibles.append(self.pros - self.cbs)

        if self.nfl > 0:
            possibles.append(self.nfl - self.number_fire)
            possibles.append(self.nfl - self.pros)
            possibles.append(self.nfl - self.cbs)

        if self.cbs > 0:
            possibles.append(self.cbs - self.number_fire)
            possibles.append(self.cbs - self.pros)
            possibles.append(self.cbs - self.nfl)

        self.smart_deviation = round(min(possibles), 2)

    def set_deviation(self):
        possibles = [self.largest_deviation, self.number_fire - self.pros, self.number_fire - self.nfl,
                     self.number_fire - self.cbs, self.pros - self.number_fire, self.pros - self.nfl,
                     self.pros - self.cbs, self.nfl - self.number_fire,
                     self.nfl - self.pros, self.nfl - self.cbs, self.cbs - self.number_fire, self.cbs - self.pros,
                     self.cbs - self.nfl]

        self.largest_deviation = round(min([abs(number) for number in possibles]), 2)

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)
