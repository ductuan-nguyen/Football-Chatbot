# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from actions.get_data import *
from translate import Translator
from datetime import datetime


def _translate(text):
    translator = Translator(to_lang="vi", from_lang="en")
    translation = translator.translate(text)
    return translation


def find_player_by_name(name):
    data = get_players_data()
    detail = data['detail']
    basic = data['basic']
    players_basic = []
    players_detail = []
    for player in detail['players']:
        full_name = player['first_name'] + ' ' + player['second_name']
        short_name = player['web_name']
        if name.lower() in (full_name.lower(), short_name.lower()):
            player_detail = player
            player_detail['full_name'] = full_name
            players_detail.append(player_detail)
            # print('found')

    for player_detail in players_detail:
        find_name = (
        player_detail['full_name'].lower(), player_detail['web_name'].lower(), player_detail['first_name'].lower(),
        player_detail['second_name'].lower())
        for player in basic['players']:
            if player['name'].lower() in find_name:
                player_basic = player
                players_basic.append(player_basic)

    return players_basic, players_detail


def find_team_by_name(name):
    data = get_data('teams')
    teams = data['teams']

    for team in teams:
        if name.lower() in (team['name'].lower(), team['shortName'].lower(), team['tla'].lower()):
            return team


def find_manager_by_name(name):
    data = get_managers_data()
    managers = data['managers']
    for manager in managers:
        if manager['name'] == name:
            return manager


class GetGeneralInformation(Action):

    def name(self) -> Text:
        return "action_provide_general_infor"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        entities = tracker.latest_message['entities']
        type_name = (entities[0])['entity']
        name = (entities[0])['value']
        if type_name == 'player_name':
            pass
        if type_name == 'club_name':
            team = find_team_by_name(name)
            message = "Câu lạc bộ: {team_name}\nNăm thành lập: {founded}\nSân nhà: {stdium_name}\nHuấn luyện viên hiện tại: {manager_name}"
            manager_data = get_managers_data()
            managers = manager_data['managers']
            for manager in managers:
                if team['name'] == manager['team']:
                    manager_name = manager['name']

            dispatcher.utter_message(image=team['crestUrl'],
                                     text=message.format(team_name=team['name'], founded=team['founded'],
                                                         stdium_name=team['venue'], manager_name=manager_name))


class GetTeamOfPlayer(Action):

    def name(self) -> Text:
        return "action_provide_player_team"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        entities = tracker.latest_message['entities']
        player_name = (entities[0])['value']

        players_basic, players_detail = find_player_by_name(player_name)


# actions get manager infor
class GetTeamOfManager(Action):
    def name(self) -> Text:
        return "action_provide_manager_team"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        entities = tracker.latest_message['entities']
        manager_name = (entities[0])['value']

        manager = find_manager_by_name(manager_name)

        message = "{manager_name} là huấn luyện viên của câu lạc bộ {team_name}"
        dispatcher.utter_message(text=message.format(manager_name=manager_name, team_name=manager['team']))


# action get team infor
class GetManagerOfTeam(Action):
    def name(self) -> Text:
        return "action_provide_team_manager"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        entities = tracker.latest_message['entities']
        team_name = (entities[0])['value']

        data = get_managers_data()
        for manager in data['managers']:
            if team_name.lower() in (manager['team'].lower(), manager['shortNameTeam'].lower()):
                manager_name = manager['name']
                country = manager['nationality']

        message = "Huấn luyện viên của {team_name} là {manager_name}, một HLV người {country_name}"

        dispatcher.utter_message(
            text=message.format(team_name=team_name, manager_name=manager_name, country_name=_translate(country)))


class GetTeamRanking(Action):
    def name(self) -> Text:
        return "action_provide_team_ranking"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        entities = tracker.latest_message['entities']
        team_name = (entities[0])['value']

        team = find_team_by_name(team_name)
        team_id = team['id']
        standings_data = get_data('standings')['standings']
        table = (standings_data[0])['table']
        for row in table:
            if row['team']['id'] == team_id:
                message = 'Xếp hạng của câu lạc bộ {team_name}: {pos}\nĐiểm: {point}\nSố trận đã chơi: {games}\nThắng: {won}, Thua: {lost}, Hòa: {draw}'
                dispatcher.utter_message(
                    text=message.format(team_name=team_name, pos=row['position'], point=row['points'],
                                        games=row['playedGames'],
                                        won=row['won'], lost=row['lost'], draw=row['draw']))
                if row['position'] == 1:
                    dispatcher.utter_message(text='Chắc là vô địch rồi :v')
                elif row['position'] <= 4:
                    dispatcher.utter_message(text='Được đá C1 rồi :v')
                elif row['position'] == 5:
                    dispatcher.utter_message(text='Uống C2 rồi :v')
                elif row['position'] >= 18:
                    dispatcher.utter_message(text='Đá kém, xuống hạng thôi :v')
                break


class GetTeamNextMatch(Action):
    def name(self) -> Text:
        return "action_provide_team_next_match"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        entities = tracker.latest_message['entities']
        team_name = (entities[0])['value']
        team = find_team_by_name(team_name)
        team_id = team['id']

        matches_data = get_data('matches')
        matches = matches_data['matches']
        current_matchday = (matches[0])['season']['currentMatchday']
        if current_matchday < 38:
            for i in range((current_matchday - 1) * 10, (current_matchday + 1) * 10):
                match = matches[i]
                if match['status'] == 'SCHEDULE' and team_id in (match['homeTeam']['id'], match['awayTeam']['id']):
                    utc_time_str = match['utcDate']
                    utc_time = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%SZ")
                    timestamp = float(utc_time.strftime("%s"))
                    local_time = datetime.fromtimestamp(timestamp)
                    local_time_str = datetime.strftime(local_time, "%H:%M ngày %d/%m/%Y")

                    home_team_name = match['homeTeam']['name']
                    home_team = find_team_by_name(home_team_name)
                    stadium = home_team['venue']

                    message = 'Trận tiếp theo: {home} vs {away}\nDiễn ra vào lúc {time} trên SVĐ {std_name}'
                    dispatcher.utter_message(
                        text=message.format(home=match['homeTeam']['name'], away=match['awayTeam']['name'],
                                            time=local_time_str, std_name=stadium))
                    break
        else:
            found = False
            for i in range(370, 380):
                match = matches[i]
                if match['status'] == 'SCHEDULE' and team_id in (match['homeTeam']['id'], match['awayTeam']['id']):
                    found = True
                    utc_time_str = match['utcDate']
                    utc_time = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%SZ")
                    timestamp = float(utc_time.strftime("%s"))
                    local_time = datetime.fromtimestamp(timestamp)
                    local_time_str = datetime.strftime(local_time, "%H:%M ngày %d/%m/%Y")

                    home_team_name = match['homeTeam']['name']
                    home_team = find_team_by_name(home_team_name)
                    stadium = home_team['venue']

                    message = 'Trận tiếp theo: {home} vs {away}\nDiễn ra vào lúc {time} trên SVĐ {std_name}'
                    dispatcher.utter_message(
                        text=message.format(home=match['homeTeam']['name'], away=match['awayTeam']['name'],
                                            time=local_time_str, std_name=stadium))
            if not found:
                dispatcher.utter_message(text=team_name + " đã đá tất cả các trận mùa này")
