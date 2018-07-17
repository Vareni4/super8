import logging

from .Scraper import MatchTitleInfo


logger = logging.getLogger(__name__)

logger_formatter = logging.Formatter(fmt='%(asctime)-15s %(name)s %(levelname)s: %(message)s')

logger_handler = logging.StreamHandler()
logger_handler.setFormatter(logger_formatter)

logger.addHandler(logger_handler)

logger.setLevel(logging.DEBUG)

class Parser:

    def parse_upcoming_matches_ids(self, upcoming_matches_raw_page_text):

        sep = "¬~"

        res = []

        tournament_name = None
        country_name = None
        tournament_encoded = None
        tournament_stage_encoded = None

        for raw_info in upcoming_matches_raw_page_text.split(sep):
            if raw_info.startswith("QA") or raw_info.startswith("SA"):
                continue

            if raw_info.startswith("ZA"): #tournament entry

                tournament_raw = raw_info

                dct = dict(tuple(item.split("÷")) for item in tournament_raw.split("¬") if item)

                tournament_name = dct['ZA']
                country_name = dct['ZY']
                tournament_encoded = dct['ZE']
                tournament_stage_encoded = dct['ZC']

            elif raw_info.startswith("AA"): #match entry

                match_raw = raw_info

                dct = dict(tuple(item.split("÷")) for item in match_raw.split("¬") if item)

                home_team_name = dct['WU']
                guest_team_name = dct['WV']
                match_id = dct["AA"]

                res.append(MatchTitleInfo(match_id,
                                          country_name,
                                          tournament_name,
                                          tournament_encoded,
                                          tournament_stage_encoded,
                                          home_team_name,
                                          guest_team_name))


        return res
