from utils import low_split
from objects import Team, Event


class Match():

    def __init__(self, match_id):
        self.match_id = match_id
        self.home_team = None
        self.guest_team = None
        self.result = MatchResult()
        self.events = {'h': [], 'g': []}
        self.stats = {'h': dict(), 'g': dict()}

    def add_event(self, event, team):
        assert team in ('h', 'g')
        self.events[team].append(event)

    def add_stat(self, stat_name, stat_val, team):
        assert team in ('h', 'g')
        self.stats[team][team + "_" + low_split(stat_name)] = stat_val

    def __repr__(self):
        s = f"Match: {self.home_team.name} - {self.guest_team.name}\n"
        s = f"Match id - {self.match_id}\n"
        s += f"Result: {repr(self.result)}\n"
        s += f"Events:\n"
        events = [("Home Team:", event) for event in self.events['h']] + \
                 [("Guest Team:", event) for event in self.events['g']]

        for team, event in sorted(events, key=lambda e: e[1].time):
            s += " " * 4 + team + " " + repr(event) + "\n"

        s += 'Stats:\n'

        for name, val in self.stats["h"].items():
            s += " " * 4 + name + " - " + val + "\n"

        for name, val in self.stats["g"].items():
            s += " " * 4 + name + " - " + val + "\n"

        return s


class MatchResult():

    def __init__(self):
        self.first_half_home_score = 0
        self.first_half_away_score = 0
        self.second_half_home_score = 0
        self.second_half_away_score = 0

    def __repr__(self):
        g_1 = sum(map(int, [self.first_half_home_score, self.second_half_home_score]))
        g_2 = sum(map(int, [self.first_half_away_score, self.second_half_away_score]))

        s = f"{g_1}-{g_2}({self.first_half_home_score}-{self.first_half_away_score},{self.second_half_home_score}-{self.second_half_away_score})"

        return s
