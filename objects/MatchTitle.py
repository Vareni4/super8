from collections import namedtuple

MatchTitleInfo = namedtuple("MatchTitleInfo", ['s24_id',
                                               'country',
                                               'tournament',
                                               'tournament_encoded',
                                               'tournament_stage_encoded',
                                               'home_team_name',
                                               'guest_team_name'])
