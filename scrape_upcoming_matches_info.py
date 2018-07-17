import logging

from objects.MatchInfoType import MatchInfoType
from parsers.Scraper import Scraper
from parsers.Parser import Parser
from scipy.stats import norm
import time

logger = logging.getLogger(__name__)

logger_formatter = logging.Formatter(fmt='%(asctime)-15s %(name)s %(levelname)s: %(message)s')

logger_handler = logging.StreamHandler()
logger_handler.setFormatter(logger_formatter)

logger.addHandler(logger_handler)

logger.setLevel(logging.INFO)

if __name__ == '__main__':

    scraper = Scraper()
    parser = Parser()

    matches_list_path = scraper.scrape_upcoming_matches_list()
    matches_lst_raw_text = open(matches_list_path, 'r').read()

    matches_lst = parser.parse_upcoming_matches_ids(matches_lst_raw_text)

    for i, match_title in enumerate(matches_lst):

        try:
            logger.info(msg=f'Scraping {i} out of {len(matches_lst)} match.')

            scraper.scrape_upcoming_match_info(match_title, info_types=[MatchInfoType.H2H,
                                                                        MatchInfoType.ODDS,
                                                                        MatchInfoType.STANDINGS,
                                                                        MatchInfoType.DRAW])

            logger.info(msg=f'Match {match_title.s24_id} scraped and saved.')
        except Exception:
            raise