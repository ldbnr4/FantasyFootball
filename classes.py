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
        self.deviation = 0
        self.espn = 0

    def set_nfl(self, projection):
        self.nfl = float(projection)

    def set_number(self, projection):
        self.number_fire = float(projection)

    def set_pros(self, projection):
        self.pros = float(projection)

    def set_espn(self, projection):
        self.espn = float(projection)

    def set_cbs(self, projection):
        self.cbs = float(projection)

    def set_ave(self):
        values = [self.nfl, self.number_fire, self.pros, self.cbs, self.espn]
        self.ave = round(sum(values) / len(values), 2)

    def set_smart_ave(self):
        values = [self.nfl, self.number_fire, self.pros, self.cbs, self.espn]
        values_over_zero = sum(num > 0 for num in values)
        if values_over_zero > 0:
            self.smart_ave = round(sum(values) / values_over_zero, 2)

    def set_deviation(self):
        possibles = [self.deviation]
        if self.number_fire > 0:
            possibles.append(self.number_fire - self.pros)
            possibles.append(self.number_fire - self.nfl)
            possibles.append(self.number_fire - self.cbs)
            possibles.append(self.number_fire - self.espn)

        if self.pros > 0:
            possibles.append(self.pros - self.number_fire)
            possibles.append(self.pros - self.nfl)
            possibles.append(self.pros - self.cbs)
            possibles.append(self.pros - self.espn)

        if self.nfl > 0:
            possibles.append(self.nfl - self.number_fire)
            possibles.append(self.nfl - self.pros)
            possibles.append(self.nfl - self.cbs)
            possibles.append(self.nfl - self.espn)

        if self.cbs > 0:
            possibles.append(self.cbs - self.number_fire)
            possibles.append(self.cbs - self.pros)
            possibles.append(self.cbs - self.nfl)
            possibles.append(self.cbs - self.espn)

        if self.espn > 0:
            possibles.append(self.espn - self.number_fire)
            possibles.append(self.espn - self.pros)
            possibles.append(self.espn - self.nfl)
            possibles.append(self.espn - self.cbs)

        self.deviation = round(min(possibles), 2)

    def to_json(self):
        self.set_deviation()
        self.set_ave()
        self.set_smart_ave()
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)
