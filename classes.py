import json


class Projections:
    def __init__(self):
        self.nfl = 0
        self.number_fire = 0
        self.pros = 0

    def set_nfl(self, projection):
        self.nfl = float(projection)

    def set_number(self, projection):
        self.number_fire = float(projection)

    def set_pros(self, projection):
        self.pros = float(projection)

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)


class Player:
    def __init__(self, name, position, team, opponent, owner):
        self.name = name
        self.position = position
        self.team = team
        self.owner = owner
        self.opponent = opponent
        self.projections = dict()

    def get_projections(self, week):
        if self.has_week(week):
            projections = self.projections[week]
        else:
            projections = Projections()
        self.projections[week] = projections
        return projections

    def has_week(self, week):
        try:
            # noinspection PyStatementEffect
            self.projections[week]
            return True
        except KeyError:
            return False

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)
