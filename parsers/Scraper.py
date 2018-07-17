import os
import requests
import time
from scipy.stats import expon
from exceptions import PageParseException, PageNotFoundException
import datetime as dt

from objects.MatchTitle import MatchTitleInfo
from objects.MatchInfoType import MatchInfoType
import logging

logger = logging.getLogger(__name__)

logger_formatter = logging.Formatter(fmt='%(asctime)-15s %(name)s %(levelname)s: %(message)s')

logger_handler = logging.StreamHandler()
logger_handler.setFormatter(logger_formatter)

logger.addHandler(logger_handler)

logger.setLevel(logging.INFO)


class Scraper():

    def scrape_upcoming_matches_list(self, days_after_today=1, hours_after_gmt=0):

        path = self._get_tommorow_day_folder_path() + "/raw_upcoming_matches.txt"

        url = f"https://d.soccer24.com/x/feed/f_1_{days_after_today}_{hours_after_gmt}_en_2"

        try:
            self._scrape_and_persist(url, path)
            logger.info(msg="Tommorow upcoming matches list scraped.")
        except PageParseException:
            raise

        return path

    def scrape_upcoming_match_info(self, match_title: MatchTitleInfo, info_types=None):

        _info_types = info_types if info_types else (MatchInfoType.MATCH_SUMMARY,)

        path = self._get_tommorow_day_folder_path() + "/" + "/".join([match_title.country,
                                                                match_title.tournament,
                                                                " - ".join([match_title.home_team_name,
                                                                            match_title.guest_team_name,
                                                                            match_title.s24_id])
                                                                ])

        match_id = match_title.s24_id

        for info_type in _info_types:
            page_url = self._generate_info_url(match_title, info_type)

            try:
                self._scrape_and_persist(page_url, path + f"/{info_type.name.lower()}.txt")

                logger.info(msg=f"Match {info_type.name} info scraped and persisted. "
                                 f"Match id: {match_id}, "
                                 f"Match Title: {match_title.home_team_name} - {match_title.guest_team_name}.")



            except PageParseException as e:
                raise PageParseException(f"Unable to scrape match {info_type.name} information. "
                                         f"Match id: {match_id}, "
                                         f"Match Title :{match_title.home_team_name} - {match_title.guest_team_name}."
                                         f"Cause: {e.args[0]}.")
            except Exception:
                raise


    def _generate_info_url(self, match_title : MatchTitleInfo, info_type : MatchInfoType):

        match_id = match_title.s24_id

        if info_type is MatchInfoType.H2H:
            return f"https://d.soccer24.com/x/feed/d_hh_{match_id}_en_2"
        elif info_type is MatchInfoType.ODDS:
            return f"https://d.soccer24.com/x/feed/d_od_{match_id}_en_2"
        elif info_type is MatchInfoType.STANDINGS:
            return f"https://d.soccer24.com/x/feed/ss_2_{match_title.tournament_encoded}_" \
                   f"{match_title.tournament_stage_encoded}_table_overall"
        elif info_type is MatchInfoType.DRAW:
            return f"https://d.soccer24.com/x/feed/ss_2_{match_title.tournament_encoded}_" \
                   f"{match_title.tournament_stage_encoded}_draw_"


    def _get_tommorow_day_folder_path(self):

        tommorow_date_str = (dt.date.today() + dt.timedelta(days=1)).strftime("%Y_%m_%d")
        path = f"/home/oleg/PycharmProjects/super8/data/{tommorow_date_str}"

        return path

    def _scrape_and_persist(self, url, file_path):
        if os.path.exists(file_path):
            logger.info(msg=f"File {file_path} already exists. Page {url} have been scraped already.")
            return

        try:
            text = self._scrape_page(url)
        except PageNotFoundException:
            logger.warning(msg=f"Page {url} doesn't exist.")
            return
        self._persist_scraped_text(text, file_path)


    def _scrape_page(self, url):

        time_pause = expon.rvs(loc=0, scale=20)
        time.sleep(time_pause)

        headers = self._generate_headers()

        req = None

        for _ in range(3):

            req = requests.get(url, headers=headers)

            if req.status_code == 200:
                break


        if req.status_code == 404:
            raise PageNotFoundException(f"Page not found. "
                                     f"Request status code: {req.status_code}. "
                                     f"URL: {url}")

        if req.status_code != 200:
            raise PageParseException(f"Unable to parse page. "
                                     f"Request status code: {req.status_code}. "
                                     f"URL: {url}")

        return req.text

    def _persist_scraped_text(self, text, file_path):
        file_dir_spl = file_path.rsplit("/", 1)
        if len(file_dir_spl) == 2 and not os.path.exists(file_dir_spl[0]):
            os.makedirs(file_dir_spl[0], exist_ok=True)

        open(file_path, 'w').write(text)


    def _generate_headers(self):
        headers = {"x-fsign": "SW9D1eZo"}

        return headers


if __name__ == '__main__':
    prs = Scraper()
    try:
        path = prs.scrape_upcoming_matches_list()
    except Exception:
        raise
