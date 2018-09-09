import logging

from objects.MatchInfoType import MatchInfoType
from parsers.Parser import Parser
from parsers.Scraper import Scraper
from utils import get_day_folder_path

logger = logging.getLogger(__name__)

logger_formatter = logging.Formatter(
    fmt='%(asctime)-15s %(name)s %(levelname)s: %(message)s')

logger_handler = logging.StreamHandler()
logger_handler.setFormatter(logger_formatter)

logger.addHandler(logger_handler)

logger.setLevel(logging.INFO)

if __name__ == '__main__':

    scraper = Scraper()
    parser = Parser()

    path = get_day_folder_path(days_diff=-1) + "/raw_upcoming_matches.txt"
    matches_lst_raw_text = open(path, 'r').read()
    prs = Parser()

    matches_lst = parser.parse_upcoming_matches_ids(matches_lst_raw_text)

    for i, match_title in enumerate(matches_lst):

        try:
            logger.info(msg=f'Scraping {i} out of {len(matches_lst)} match.')

            scraper.scrape_match_info(match_title,
                                      info_types=[MatchInfoType.RESULT,
                                                  MatchInfoType.MATCH_SUMMARY,
                                                  MatchInfoType.STATS,
                                                  MatchInfoType.LINEUPS
                                                  ],
                                      days_after_today=-1)

            logger.info(msg=f'Match {match_title.s24_id} scraped and saved.')
        except Exception:
            raise
