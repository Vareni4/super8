import requests
import re
import sqlite3
from bs4 import BeautifulSoup
from collections import namedtuple
from objects.Match import Match
from objects.Team import Team
from exceptions import MatchPageParseException


def generate_headers():
    headers = {"x-fsign": "SW9D1eZo"}

    return headers


def extract_team(match_page_soup, home=True):

    team = "home" if home else "away"
    try:
        team_tds = [td for td in match_page_soup.findAll("td") if f"tname-{team}" in td.attrs.get('class', [])]

        team_td = team_tds[0]

        team_str = team_td.find('a')
        team_link = re.findall("/team/.*/[a-zA-Z0-9]+", team_str.attrs['onclick'])[0]

        team_id = team_link.split("/")[-1]
        team_name = team_str.text

    except Exception as err:
        raise MatchPageParseException(f"Unable to parse {team} team.\n"
                                      f"Cause - {err}")


    return Team(s24_id=team_id, name=team_name, link=team_link)


def parse_match_result(match_id):

    match = Match(match_id)

    headers = generate_headers()

    match_page = f"https://www.soccer24.com/match/{match_id}"

    for _ in range(3):
        req = requests.get(match_page, headers=headers)

        if req.status_code == 200:
            break

    if req.status_code != 200:
        raise MatchPageParseException(f"Unable to parse match page. "
                                      f"Request status code - {req.status_code}. \n "
                                      f"Match id - {match_id} \n"
                                      f"Match page - {match_page}")


    match_page_text = req.text
    match_page_soup = BeautifulSoup(match_page_text, 'html.parser')

    match.home_team = extract_team(match_page_soup)
    match.guest_team = extract_team(match_page_soup, home=False)



    r = requests.get(f"https://d.soccer24.com/x/feed/d_su_{match_id}_en_2", headers=headers)

    match_page_text = r.text

    match_page_soup = BeautifulSoup(match_page_text, 'html.parser')

    print(match_page_soup.find('div').find('table').prettify())

    table = match_page_soup.find('div').find('table').find('tbody')

    [ch.attrs for ch in table.children]

    for ch in list(table.children):

        home_event = ch.find('td', attrs={"class": ["summary-vertical fl"]})
        guest_event = ch.find('td', attrs={"class": ["summary-vertical fr"]})

        if home_event is None and guest_event is None:
            continue

        event_team = None

        if home_event.find('div', attrs={"class": "time-box"}) is not None:
            event_team = 'h'
            event = home_event

        if guest_event.find('div', attrs={"class": "time-box"}) is not None:
            assert event_team is None
            event_team = 'g'
            event = guest_event

        if ch.find('span', attrs={"class": "p1_home"}) is not None:
            first_half_home_score = ch.find('span', attrs={"class": "p1_home"})
            match.result.first_half_home_score = first_half_home_score.text

        if ch.find('span', attrs={"class": "p1_away"}) is not None:
            first_half_away_score = ch.find('span', attrs={"class": "p1_away"})
            match.result.first_half_away_score = first_half_away_score.text

        if ch.find('span', attrs={"class": "p2_home"}) is not None:
            second_half_home_score = ch.find('span', attrs={"class": "p2_home"})
            match.result.second_half_home_score = second_half_home_score.text

        if ch.find('span', attrs={"class": "p2_away"}) is not None:
            second_half_away_score = ch.find('span', attrs={"class": "p2_away"})
            match.result.second_half_away_score = second_half_away_score.text

        time = event.find('div', attrs={"class": "time-box"}).text
        time = int(re.findall('[0-9]+', time)[0])

        if event.find('span', attrs={"class": "substitution-in-name"}) is not None:
            player_in_str = event.find('span', attrs={"class": "substitution-in-name"}).find('a')

            player_in_link = re.findall("/player/.*/.*/", player_in_str.attrs['onclick'])[0]
            player_in_id = player_in_link.split("/")[-2]
            player_in_name = player_in_str.text

            player_in = Player(s24_id=player_in_id, name=player_in_name, link=player_in_link)

            player_out_str = event.find('span', attrs={"class": "substitution-out-name"}).find('a')

            player_out_link = re.findall("/player/.*/.*/", player_out_str.attrs['onclick'])[0]
            player_out_id = player_out_link.split("/")[-2]
            player_out_name = player_out_str.text

            player_out = Player(s24_id=player_out_id, name=player_out_name, link=player_out_link)

            event_obj = Substitution(time, player_in=player_in, player_out=player_out)

            match.add_event(event_obj, event_team)

        if event.find('span', attrs={"class": "participant-name"}) is not None:

            event_div = event.find('span', attrs={"class": "participant-name"})
            player_str = event_div.find('a')

            player_link = re.findall("/player/.*/.*/", player_str.attrs['onclick'])[0]
            player_id = player_link.split("/")[-2]
            player_name = player_str.text

            player = Player(s24_id=player_id, name=player_name, link=player_link)

            if any('r-card' in div.attrs['class'] for div in event.find_all('div')):
                event_obj = RedCard(time, player=player)

            if any('y-card' in div.attrs['class'] for div in event.find_all('div')):
                event_obj = YellowCard(time, player=player)

            if any('soccer-ball' in div.attrs['class'] for div in event.find_all('div')):
                event_obj = Goal(time, player_scored=player)

            event_obj = Goal(time, player_scored=player)

            match.add_event(event_obj, event_team)

    r = requests.get(f"https://d.soccer24.com/x/feed/d_st_{match_id}_en_2", headers=headers)

    match_page_text = r.text

    match_page_soup = BeautifulSoup(match_page_text, 'html.parser')

    stat_rows = match_page_soup.find('div', attrs={"id": "tab-statistics-0-statistic"}).findAll('tr')

    app = "Full Time "
    for stat_row in stat_rows:
        stat_name = app + stat_row.find('td', attrs={'class': "score stats"}).text

        home_stat = stat_row.find('td', attrs={'class': "summary-vertical fl"}).findAll('div')[0].text
        guest_stat = stat_row.find('td', attrs={'class': "summary-vertical fr"}).findAll('div')[-1].text

        print(stat_name, home_stat, guest_stat)

        match.add_stat(stat_name, home_stat, 'h')
        match.add_stat(stat_name, guest_stat, 'g')

    stat_rows = match_page_soup.find('div', attrs={"id": "tab-statistics-1-statistic"}).findAll('tr')

    app = "First Half "
    for stat_row in stat_rows:
        stat_name = app + stat_row.find('td', attrs={'class': "score stats"}).text

        home_stat = stat_row.find('td', attrs={'class': "summary-vertical fl"}).findAll('div')[0].text
        guest_stat = stat_row.find('td', attrs={'class': "summary-vertical fr"}).findAll('div')[-1].text

        print(stat_name, home_stat, guest_stat)

        match.add_stat(stat_name, home_stat, 'h')
        match.add_stat(stat_name, guest_stat, 'g')

    stat_rows = match_page_soup.find('div', attrs={"id": "tab-statistics-2-statistic"}).findAll('tr')

    app = "Second Half "
    for stat_row in stat_rows:
        stat_name = app + stat_row.find('td', attrs={'class': "score stats"}).text

        home_stat = stat_row.find('td', attrs={'class': "summary-vertical fl"}).findAll('div')[0].text
        guest_stat = stat_row.find('td', attrs={'class': "summary-vertical fr"}).findAll('div')[-1].text

        print(stat_name, home_stat, guest_stat)

        match.add_stat(stat_name, home_stat, 'h')
        match.add_stat(stat_name, guest_stat, 'g')
