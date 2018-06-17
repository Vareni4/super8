class Event():

    def __init__(self, time):
        self.time = time

    def __repr__(self):
        return self.__class__.__name__ + f" {self.time} "


class Substitution(Event):

    def __init__(self, time, **kwargs):
        super().__init__(time)
        self.player_in = kwargs.get("player_in", None)
        self.player_out = kwargs.get("player_out", None)

    def __repr__(self):
        return super().__repr__() + f" {self.player_out.name} --> {self.player_in.name}"


class Goal(Event):

    def __init__(self, time, **kwargs):
        super().__init__(time)
        self.player_scored = kwargs.get("player_scored", None)

    def __repr__(self):
        return super().__repr__() + f" {self.player_scored.name} "


class YellowCard(Event):

    def __init__(self, time, **kwargs):
        super().__init__(time)
        self.player = kwargs.get("player", None)

    def __repr__(self):
        return super().__repr__() + f" {self.player.name} "


class RedCard(Event):

    def __init__(self, time, **kwargs):
        super().__init__(time)
        self.player = kwargs.get("player", None)

    def __repr__(self):
        return super().__repr__() + f" {self.player.name} "
