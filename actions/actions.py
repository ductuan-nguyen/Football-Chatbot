# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from typing import Any, Text, Dict, List

from dateutil import tz
from fuzzywuzzy import fuzz
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from actions.get_data import *
from datetime import datetime
from prettytable import PrettyTable

teams_name = {"Arsenal FC": "Arsenal",
              "Aston Villa FC": "Aston Villa",
              "Chelsea FC": "Chelsea",
              "Everton FC": "Everton",
              "Liverpool FC": "Liverpool",
              "Manchester City FC": "Man City",
              "Manchester United FC": "Man United",
              "Newcastle United FC": "Newcastle",
              "Norwich City FC": "Norwich",
              "Tottenham Hotspur FC": "Tottenham",
              "Wolverhampton Wanderers FC": "Wolverhampton",
              "Burnley FC": "Burnley",
              "Leicester City FC": "Leicester",
              "Southampton FC": "Southampton",
              "Leeds United FC": "Leeds United",
              "Watford FC": "Watford",
              "Crystal Palace FC": "Crystal Palace",
              "Brighton & Hove Albion FC": "Brighton",
              "Brentford FC": "Brentford",
              "West Ham United FC": "West Ham"}

countries_name = {"Côte d’Ivoire": "Bờ Biển Ngà",
                  "Morocco": "Maroc",
                  "England": "Anh",
                  "Portugal": "Bồ Đào Nha",
                  "Korea Republic": "Hàn Quốc",
                  "Sweden": "Thụy Điển",
                  "Austria": "Áo",
                  "United States": "Mỹ",
                  "Turkey": "Thổ Nhĩ Kì",
                  "Spain": "Tây Ban Nha",
                  "Congo DR": "Congo",
                  "France": "Pháp",
                  "Greece": "Hy Lạp",
                  "North Macedonia": "Bắc Macedonia",
                  "Poland": "Ba Lan",
                  "Denmark": "Đan Mạch",
                  "Switzerland": "Thụy Sĩ",
                  "Egypt": "Ai Cập",
                  "Netherlands": "Hà Lan",
                  "Czech Republic": "CH Séc",
                  "Norway": "Na Uy",
                  "South Africa": "Nam Phi",
                  "Northern Ireland": "Bắc Ireland",
                  "Wales": "Xứ Wales",
                  "Japan": "Nhật Bản",
                  "Germany": "Đức",
                  "Belgium": "Bỉ",
                  "Republic of Ireland": "CH Ireland"}

tla = {"Arsenal FC": "ARS",
       "Aston Villa FC": "AST",
       "Chelsea FC": "CHE",
       "Everton FC": "EVE",
       "Liverpool FC": "LIV",
       "Manchester City FC": "MCI",
       "Manchester United FC": "MUN",
       "Newcastle United FC": "NEW",
       "Norwich City FC": "NOR",
       "Tottenham Hotspur FC": "TOT",
       "Wolverhampton Wanderers FC": "WOL",
       "Burnley FC": "BUR",
       "Leicester City FC": "LEI",
       "Southampton FC": "SOU",
       "Leeds United FC": "LEE",
       "Watford FC": "WAT",
       "Crystal Palace FC": "CRY",
       "Brighton & Hove Albion FC": "BHA",
       "Brentford FC": "BRE",
       "West Ham United FC": "WHU"}


def utc_to_local_time(utc_time_str):
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    utc_time = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%SZ")
    utc = utc_time.replace(tzinfo=from_zone)
    local_time = utc.astimezone(to_zone)
    return local_time


def find_player_by_name(name, need_detail=True):
    data = get_players_data()
    detail = data['detail']
    basic = data['basic']
    players_basic = []
    players_detail = []
    if need_detail:
        for player in detail['players']:
            full_name = player['first_name'] + ' ' + player['second_name']
            short_name = player['web_name']

            if fuzz.WRatio(name, full_name) >= 97:
                return [player]
            if fuzz.WRatio(name, full_name) > 85:
                players_detail.append(player)
                continue
            if fuzz.token_sort_ratio(name, short_name) > 85:
                players_detail.append(player)

        return players_detail

    else:
        print(name)
        for player in basic['players']:
            if fuzz.token_set_ratio(name, player['name']) == 100:
                return [player]
            if fuzz.token_set_ratio(name, player['name']) >= 90:
                players_basic.append(player)

        return players_basic


def find_team_by_name(name):
    data = get_data('teams')
    teams = []

    for team in data['teams']:
        if fuzz.WRatio(name, team['shortName']) == 100 or fuzz.WRatio(name, team['name']) == 100:
            return [team]
        if fuzz.WRatio(name, team['shortName']) > 80:
            teams.append(team)
            continue
        if fuzz.WRatio(name, team['tla']) > 80:
            teams.append(team)
    return teams


def find_manager_by_name(name):
    data = get_managers_data()
    managers = []
    for manager in data['managers']:
        if fuzz.WRatio(name, manager['firstname'] + " " + manager['lastname']) > 70:
            managers.append(manager)
    return managers


class GetGeneralInformation(Action):

    def name(self) -> Text:
        return "action_provide_general_infor"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        entities = tracker.latest_message['entities']

        if len(entities) == 0:
            message = tracker.latest_message['text']
            for word in message.split(" "):
                players = find_player_by_name(word)
                if len(players) > 0:
                    buttons = []
                    for player in players:
                        player_name = player['first_name'] + ' ' + player['second_name']
                        buttons.append(
                            {"payload": "/ask_about_a_name{\"player_name\":\"" + player_name + "\"}",
                             "title": player_name})
                    dispatcher.utter_message(text="Có phải bạn muốn thông tin về:\n", buttons=buttons)
                    return []

                managers = find_manager_by_name(word)
                if len(managers) > 0:
                    buttons = []
                    for manager in managers:
                        manager_name = manager['name']
                        buttons.append(
                            {"payload": "/ask_about_a_name{\"manager_name\":\"" + manager_name + "\"}",
                             "title": manager_name})
                        dispatcher.utter_message(text="Có phải bạn muốn thông tin về:\n", buttons=buttons)
                    return []

                teams = find_team_by_name(word)
                if len(teams) > 0:
                    buttons = []
                    for team in teams:
                        team_name = team['shortName']
                        buttons.append(
                            {"payload": "/ask_about_a_name{\"club_name\":\"" + team_name + "\"}", "title": team_name})
                    dispatcher.utter_message(text="Có phải bạn muốn thông tin về:\n", buttons=buttons)
                    return []
            dispatcher.utter_message(response="utter_not_know")
            return []

        type_name = (entities[0])['entity']
        name = (entities[0])['value']
        print("name: " + name)

        if type_name == 'player_name':
            players = find_player_by_name(name)
            if len(players) >= 2:
                buttons = []
                for player in players:
                    player_name = player['first_name'] + ' ' + player['second_name']
                    buttons.append(
                        {"payload": "/ask_about_a_name{\"player_name\":\"" + player_name + "\"}", "title": player_name})
                dispatcher.utter_message(text="Ý của bạn là\n", buttons=buttons)
            elif len(players) < 1:
                dispatcher.utter_message(response="utter_not_know")
            else:
                image_url = "https://resources.premierleague.com/premierleague/photos/players/110x140/p{picture_id}.png"
                player = find_player_by_name(name, need_detail=False)
                if len(player) == 0:
                    dispatcher.utter_message(response="utter_not_know")
                    return []
                team = player[0]['team']
                player_name = player[0]['name']
                print("find: " + name + ", found: " + player_name)
                bd_year = (player[0]['dateOfBirth'])[:4]
                age = datetime.now().year - int(bd_year)
                pic_id = players[0]['photo'][:-4]
                nation = player[0]['nationality']
                message = "{name}, quốc tịch {nationality}\nTuổi: {age}\nCâu lạc bộ hiện tại: {team}\nVị trí: {role}"
                roles = {"Midfielder": "Tiền vệ", "Attacker": "Tiền đạo", "Defender": "Hậu vệ", "Goalkeeper": "Thủ môn"}
                dispatcher.utter_message(image=image_url.format(picture_id=pic_id),
                                         text=message.format(name=player_name,
                                                             nationality=countries_name.get(nation, nation),
                                                             age=age, team=team, role=roles[player[0]['position']]))
        if type_name == 'club_name':
            teams = find_team_by_name(name)
            if len(teams) >= 2:
                buttons = []
                for team in teams:
                    team_name = team['shortName']
                    buttons.append(
                        {"payload": "/ask_about_a_name{\"club_name\":\"" + team_name + "\"}", "title": team_name})
                dispatcher.utter_message(text="Ý của bạn là\n", buttons=buttons)
            elif len(teams) < 1:
                dispatcher.utter_message(response="utter_not_know")
            else:
                team = teams[0]
                message = "Câu lạc bộ: {team_name}\nNăm thành lập: {founded}\nSân nhà: {stdium_name}\nHuấn luyện viên " \
                          "hiện tại: {manager_name} "
                manager_data = get_managers_data()
                managers = manager_data['managers']
                manager_name = ""
                for manager in managers:
                    if team['name'][:-3] == manager['team']['name']:
                        manager_name = manager['firstname'] + " " + manager['lastname']

                dispatcher.utter_message(text=message.format(team_name=team['name'], founded=team['founded'],
                                                             stdium_name=team['venue'], manager_name=manager_name))

        if type_name == 'manager_name':
            managers = find_manager_by_name(name)
            if len(managers) >= 2:
                buttons = []
                for manager in managers:
                    manager_name = manager['firstname'] + " " + manager['lastname']
                    buttons.append(
                        {"payload": "/ask_about_a_name{\"manager_name\":\"" + manager_name + "\"}",
                         "title": manager_name})
                    dispatcher.utter_message(text="Ý của bạn là\n", buttons=buttons)
            elif len(managers) < 1:
                dispatcher.utter_message(response="utter_not_know")
            else:
                manager_name = managers[0]['firstname'] + " " + managers[0]['lastname']
                age = managers[0]['age']
                message = "{manager_name} là huấn luyện viên người {nation}\nTuổi: {age}\nCLB hiện tại: {team_name}"
                dispatcher.utter_message(image=managers[0]['photo'],
                                         text=message.format(manager_name=manager_name,
                                                             nation=countries_name.get(managers[0]['nationality'],
                                                                                       managers[0]['nationality']),
                                                             age=age,
                                                             team_name=managers[0]['team']['name']))


class GetTeamOfPlayer(Action):

    def name(self) -> Text:
        return "action_provide_player_team"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        entities = tracker.latest_message['entities']
        if len(entities) == 0:
            dispatcher.utter_message("utter_not_know")
            return []
        name = entities[0]['value']

        players = find_player_by_name(name)
        if len(players) >= 2:
            buttons = []
            for player in players:
                player_name = player['first_name'] + ' ' + player['second_name']
                buttons.append(
                    {"payload": "/ask_about_a_name{\"player_name\":\"" + player_name + "\"}", "title": player_name})
                dispatcher.utter_message(text="Ý của bạn là\n", buttons=buttons)
        elif len(players) < 1:
            dispatcher.utter_message(response="utter_not_know")
        else:
            player = find_player_by_name(players[0]['web_name'], need_detail=False)
            team = player[0]['team']
            player_name = player[0]['name']
            message = "{name} hiện đang chơi cho {team}"
            dispatcher.utter_message(text=message.format(name=player_name, team=team))


class GetPlayerGoalscored(Action):
    def name(self) -> Text:
        return "action_provide_player_goalscored"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        entities = tracker.latest_message['entities']
        if len(entities) == 0:
            name = tracker.get_slot('player_name')
            if name is None:
                dispatcher.utter_message(response="utter_not_know")
                return []
        else:
            name = entities[0]['value']
        players = find_player_by_name(name)
        if len(players) >= 2:
            buttons = []
            for player in players:
                player_name = player['first_name'] + ' ' + player['second_name']
                buttons.append(
                    {"payload": "/ask_about_a_name{\"player_name\":\"" + player_name + "\"}", "title": player_name})
            dispatcher.utter_message(text="Ý của bạn là\n", buttons=buttons)
        elif len(players) < 1:
            dispatcher.utter_message(response="utter_not_know")
        else:
            player_name = players[0]['web_name']
            goals = players[0]['goals_scored']
            message = "Số bàn thắng hiện tại của {name}: {goals_scored}"
            dispatcher.utter_message(text=message.format(name=player_name, goals_scored=goals))
            if players[0]['element_type'] == 1:
                dispatcher.utter_message(text="Thủ môn mà cũng hỏi bao nhiêu bàn 😐")


class GetPlayerAssists(Action):
    def name(self) -> Text:
        return "action_provide_player_assist"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        entities = tracker.latest_message['entities']
        if len(entities) == 0:
            name = tracker.get_slot('player_name')
            if name is None:
                dispatcher.utter_message(response="utter_not_know")
                return []
        else:
            name = entities[0]['value']
        players = find_player_by_name(name)
        if len(players) >= 2:
            buttons = []
            for player in players:
                player_name = player['first_name'] + ' ' + player['second_name']
                buttons.append(
                    {"payload": "/ask_about_a_name{\"player_name\":\"" + player_name + "\"}", "title": player_name})
                dispatcher.utter_message(text="Ý của bạn là\n", buttons=buttons)
        elif len(players) < 1:
            dispatcher.utter_message(response="utter_not_know")
        else:
            player_name = players[0]['web_name']
            assists = players[0]['assists']
            message = "Số kiến tạo của {name}: {assists}"
            dispatcher.utter_message(text=message.format(name=player_name, assists=assists))
            if players[0]['element_type'] == 1:
                dispatcher.utter_message(text="Thủ môn mà cũng hỏi kiến tạo 😂")


class GetPlayerCleanSheets(Action):
    def name(self) -> Text:
        return "action_provide_player_cleansheet"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        entities = tracker.latest_message['entities']
        if len(entities) == 0:
            name = tracker.get_slot('player_name')
            if name is None:
                dispatcher.utter_message(response="utter_not_know")
                return []
        else:
            name = entities[0]['value']
        players = find_player_by_name(name)
        if len(players) >= 2:
            buttons = []
            for player in players:
                player_name = player['first_name'] + ' ' + player['second_name']
                buttons.append(
                    {"payload": "/ask_about_a_name{\"player_name\":\"" + player_name + "\"}", "title": player_name})
            dispatcher.utter_message(text="Ý của bạn là\n", buttons=buttons)
        elif len(players) < 1:
            dispatcher.utter_message(response="utter_not_know")
        else:
            player_name = players[0]['web_name']
            cleansheets = players[0]['clean_sheets']
            message = "Số trận giữ sạch lưới của {name}: {cleansheets}"
            dispatcher.utter_message(text=message.format(name=player_name, cleansheets=cleansheets))
            if players[0]['element_type'] > 2:
                dispatcher.utter_message(text="Tôi nghĩ cái này chỉ hỏi cho thủ môn hay hậu vệ thôi chứ nhỉ 🤨")


class GetTeamOfManager(Action):
    def name(self) -> Text:
        return "action_provide_manager_team"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        entities = tracker.latest_message['entities']
        if len(entities) == 0:
            dispatcher.utter_message(response="utter_not_know")
            return []
        name = (entities[0])['value']

        managers = find_manager_by_name(name)
        if len(managers) >= 2:
            buttons = []
            for manager in managers:
                manager_name = manager['firstname'] + " " + manager['lastname']
                buttons.append(
                    {"payload": "/ask_about_a_name{\"manager_name\":\"" + manager_name + "\"}", "title": manager_name})
                dispatcher.utter_message(text="Ý của bạn là\n", buttons=buttons)
        elif len(managers) < 1:
            dispatcher.utter_message(response="utter_not_know")
        else:
            manager_name = managers[0]['firstname'] + " " + managers[0]['lastname']
            message = "{manager_name} là huấn luyện viên của câu lạc bộ {team_name}"
            dispatcher.utter_message(text=message.format(manager_name=manager_name, team_name=managers[0]['team']['name']))


# action get team infor
class GetManagerOfTeam(Action):
    def name(self) -> Text:
        return "action_provide_team_manager"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        entities = tracker.latest_message['entities']
        if len(entities) == 0:
            dispatcher.utter_message(response="utter_not_know")
            return []
        name = (entities[0])['value']
        teams = find_team_by_name(name)
        if len(teams) >= 2:
            buttons = []
            for team in teams:
                team_name = team['shortName']
                buttons.append(
                    {"payload": "/ask_about_a_name{\"club_name\":\"" + team_name + "\"}", "title": team_name})
                dispatcher.utter_message(text="Ý của bạn là\n", buttons=buttons)
        elif len(teams) < 1:
            dispatcher.utter_message(response="utter_not_know")
        else:
            team = teams[0]
            data = get_managers_data()
            team_name = team['name']
            for manager in data['managers']:
                if team_name[:-3] == manager['team']['name']:
                    manager_name = manager['firstname'] + " " + manager['lastname']
                    country = manager['nationality']

            message = "Huấn luyện viên của {team_name} là {manager_name}, một HLV người {country_name}"

            dispatcher.utter_message(
                text=message.format(team_name=teams_name[team_name], manager_name=manager_name,
                                    country_name=countries_name.get(country, country)))


class GetRanking(Action):
    def name(self) -> Text:
        return "action_provide_ranking"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        entities = tracker.latest_message['entities']
        if len(entities) == 0:
            # print the whole standings table
            standings_data = get_data('standings')['standings']
            table = (standings_data[0])['table']
            data = []
            ranking_table = PrettyTable(['Pos', 'Team', 'Pts'])
            for row in table:
                ranking_table.add_row([row['position'], teams_name[row['team']['name']], row['points']])

            ranking_table.border = False
            # print(ranking_table)

            message = "Bảng xếp hạng hiện tại:\n"
            dispatcher.utter_message(text=message)
            dispatcher.utter_message(text=ranking_table.get_string())
            return []

        name = (entities[0])['value']

        teams = find_team_by_name(name)
        if len(teams) >= 2:
            buttons = []
            for team in teams:
                team_name = team['shortName']
                buttons.append(
                    {"payload": "/ask_about_a_name{\"club_name\":\"" + team_name + "\"}", "title": team_name})
                dispatcher.utter_message(text="Ý của bạn là\n", buttons=buttons)
        elif len(teams) < 1:
            dispatcher.utter_message(response="utter_not_know")
        else:
            team_id = teams[0]['id']
            team_name = teams[0]['shortName']
            standings_data = get_data('standings')['standings']
            table = (standings_data[0])['table']
            for row in table:
                if row['team']['id'] == team_id:
                    message = 'Xếp hạng của câu lạc bộ {team_name}: {pos}\nĐiểm: {point}\nSố trận đã chơi: {' \
                              'games}\nThắng: {won}, Thua: {lost}, Hòa: {draw} '
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

        print("get here")
        entities = tracker.latest_message['entities']
        if len(entities) == 0:
            dispatcher.utter_message(response="utter_not_know")
            return []
        name = (entities[0])['value']
        teams = find_team_by_name(name)
        print("found: " + str(len(teams)))
        if len(teams) >= 2:
            buttons = []
            for team in teams:
                team_name = team['shortName']
                buttons.append(
                    {"payload": "/ask_about_a_name{\"club_name\":\"" + team_name + "\"}", "title": team_name})
            dispatcher.utter_message(text="Ý của bạn là\n", buttons=buttons)
        elif len(teams) < 1:
            dispatcher.utter_message(response="utter_not_know")
        else:
            team_id = teams[0]['id']
            print("team id: " + str(team_id))
            matches_data = get_data('matches')
            matches = matches_data['matches']
            current_matchday = (matches[0])['season']['currentMatchday']
            print('current_matchday = ' + str(current_matchday))
            if current_matchday < 38:
                for i in range((current_matchday - 1) * 10, (current_matchday + 1) * 10):
                    match = matches[i]
                    # tpl = (match['homeTeam']['id'], match['awayTeam']['id'])
                    # print(tpl)
                    if match['status'] == 'SCHEDULED' and team_id in (match['homeTeam']['id'], match['awayTeam']['id']):
                        print("found match")
                        utc_time_str = match['utcDate']
                        local_time = utc_to_local_time(utc_time_str)
                        local_time_str = datetime.strftime(local_time, "%H:%M ngày %d/%m/%Y")

                        home_team_name = match['homeTeam']['name']
                        home_team = find_team_by_name(home_team_name)
                        print(home_team[0]['name'])
                        stadium = home_team[0]['venue']

                        message = 'Trận tiếp theo: {home} vs {away}\nDiễn ra vào lúc {time} trên SVĐ {std_name}'
                        dispatcher.utter_message(
                            text=message.format(home=teams_name[match['homeTeam']['name']],
                                                away=teams_name[match['awayTeam']['name']],
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
                        stadium = home_team[0]['venue']

                        message = 'Trận tiếp theo: {home} vs {away}\nDiễn ra vào lúc {time} trên SVĐ {std_name}'
                        dispatcher.utter_message(
                            text=message.format(home=match['homeTeam']['name'], away=match['awayTeam']['name'],
                                                time=local_time_str, std_name=stadium))
                if not found:
                    dispatcher.utter_message(text=teams[0]['shortName'] + " đã đá tất cả các trận mùa này")


class GetTopScorers(Action):
    def name(self) -> Text:
        return "action_provide_topscorer_list"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="Top cầu thủ ghi bàn nhiều nhất:\n")
        data = get_players_data()
        players = data['detail']['players']
        scorer_list = []
        for player in players:
            scorer_list.append(player)

        num = 0
        message = "{order}. {name}: {goals} bàn\n"
        for player in sorted(scorer_list, key=lambda p: p.get('goals_scored'), reverse=True):
            player_name = player['first_name'] + ' ' + player['second_name']
            basic = find_player_by_name(player_name, need_detail=False)
            print(len(basic))
            num += 1
            if num == 1:
                top_name = player_name
            if num > 5:
                break
            dispatcher.utter_message(
                text=message.format(order=num, name=player_name, team=basic[0]['team'], goals=player['goals_scored']))

        dispatcher.utter_message(text="Vua phá lưới hiện tại: {name}".format(name=top_name))
        return []


class GetTopAssist(Action):
    def name(self) -> Text:
        return "action_provide_topassist_list"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="Top cầu thủ kiến tạo nhiều nhất:\n")
        data = get_players_data()
        players = data['detail']['players']
        assist_list = []
        for player in players:
            assist_list.append(player)

        num = 0
        message = "{order}. {name}: {assists} kiến tạo\n"
        for player in sorted(assist_list, key=lambda p: p.get('assists'), reverse=True):
            player_name = player['first_name'] + ' ' + player['second_name']
            basic = find_player_by_name(player_name, need_detail=False)
            print(len(basic))
            num += 1
            if num == 1:
                top_name = player_name
            if num > 5:
                break
            dispatcher.utter_message(
                text=message.format(order=num, name=player_name, team=basic[0]['team'], assists=player['assists']))

        dispatcher.utter_message(text="\nVua kiến tạo hiện tại: {name}".format(name=top_name))
        return []


class GetTopGoalkeepers(Action):
    def name(self) -> Text:
        return "action_provide_topgk_list"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="Top thủ môn giữ sạch lưới nhiều nhất:\n")
        data = get_players_data()
        players = data['detail']['players']
        gk_list = []
        for player in players:
            if player['element_type'] == 1:
                gk_list.append(player)

        num = 0
        message = "{order}. {name}: {cleansheet} trận \n"
        for player in sorted(gk_list, key=lambda p: p.get('clean_sheets'), reverse=True):
            player_name = player['first_name'] + ' ' + player['second_name']
            basic = find_player_by_name(player_name, need_detail=False)
            print(len(basic))
            num += 1
            if num == 1:
                top_name = player_name
            if num > 5:
                break
            dispatcher.utter_message(
                text=message.format(order=num, name=player_name, team=basic[0]['team'],
                                    cleansheet=player['clean_sheets']))

        dispatcher.utter_message(text="\nThủ môn xuất sắc nhất hiện tại: {name}".format(name=top_name))
        return []


class GetSchedule(Action):
    def name(self) -> Text:
        return "action_provide_schedule"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        entities = tracker.latest_message['entities']
        _round = 0

        for entity in entities:
            if entity['entity'] == 'round':
                _round = int(entity['value'])

        matches_data = get_data('matches')
        matches = matches_data['matches']
        current_matchday = (matches[0])['season']['currentMatchday']
        match_day = current_matchday

        if _round > 0:
            if _round > 38:
                dispatcher.utter_message(text="Giải đấu có 38 vòng thôi bạn ơi :D")
                return []
            elif _round < current_matchday:
                dispatcher.utter_message(text="Vòng đấu đã kết thúc, bạn có muốn xem kết quả?",
                                         buttons=[{"payload": "/affirm{\"round\":" + str(_round) + "}", "title": "Có"},
                                                  {"payload": "/deny", "title": "Không"}])
                return []
            else:
                match_day = _round

        message = "Lịch thi đấu vòng " + str(match_day) + ":\n"

        for i in range((match_day - 1) * 10, match_day * 10):
            match = matches[i]
            utc_time_str = match['utcDate']
            local_time = utc_to_local_time(utc_time_str)
            local_time_str = datetime.strftime(local_time, "%H:%M ngày %d/%m/%Y")

            match_detail = '<b>{home} {h}{notation}{a} {away}</b> {time}'
            h_score = ""
            a_score = ""
            notation = "vs"
            if match['status'] == "FINISHED":
                h_score = str(match['score']['fullTime']['homeTeam'])
                a_score = str(match['score']['fullTime']['awayTeam'])
                notation = ":"
            message = message + match_detail.format(home=teams_name[match['homeTeam']['name']], h=h_score,
                                                    notation=notation, a=a_score,
                                                    away=teams_name[match['awayTeam']['name']],
                                                    time=local_time_str) + "\n"
        dispatcher.utter_message(json_message={'text': message, 'parse_mode': 'html'})

        return []


class GetResult(Action):
    def name(self) -> Text:
        return "action_provide_league_result"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        _round = 0
        entities = tracker.latest_message["entities"]
        for entity in entities:
            if entity['entity'] == 'round':
                _round = int(entity['value'])

        matches_data = get_data('matches')
        matches = matches_data['matches']
        current_matchday = (matches[0])['season']['currentMatchday']
        match_day = current_matchday

        if _round > 0:
            if _round > 38:
                dispatcher.utter_message(text="Giải đấu có 38 vòng thôi bạn ơi :D")
                return []
            elif _round > current_matchday:
                dispatcher.utter_message(text="Vòng đấu chưa diễn ra, bạn có muốn xem lịch thi đấu?",
                                         buttons=[{"payload": "/affirm{\"round\":" + str(_round) + "}", "title": "Có"},
                                                  {"payload": "/deny", "title": "Không"}])
                return []
            else:
                match_day = _round

        message = "Kết quả vòng " + str(match_day) + ":\n"
        finished_matches = ""
        scheduled_matches = ""
        match_detail = '<b>{home} {h}{notation}{a} {away}</b> {time}'
        for i in range((match_day - 1) * 10, match_day * 10):
            match = matches[i]

            utc_time_str = match['utcDate']
            local_time = utc_to_local_time(utc_time_str)
            local_time_str = datetime.strftime(local_time, "%H:%M ngày %d/%m/%Y")

            h_score = ""
            a_score = ""
            notation = "vs"
            if match['status'] == "FINISHED":
                h_score = str(match['score']['fullTime']['homeTeam'])
                a_score = str(match['score']['fullTime']['awayTeam'])
                notation = ":"
                finished_matches += match_detail.format(home=teams_name[match['homeTeam']['name']],
                                                        h=h_score, notation=notation, a=a_score,
                                                        away=teams_name[match['awayTeam']['name']],
                                                        time=local_time_str) + "\n"
            else:
                scheduled_matches += match_detail.format(home=teams_name[match['homeTeam']['name']],
                                                         h=h_score, notation=notation, a=a_score,
                                                         away=teams_name[match['awayTeam']['name']],
                                                         time=local_time_str) + "\n"

        if finished_matches == "":
            dispatcher.utter_message(text="Vòng đấu chưa diễn ra, bạn có muốn xem lịch thi đấu?",
                                     buttons=[{"payload": "/affirm{\"round\":" + str(_round) + "}", "title": "Có"},
                                              {"payload": "/deny", "title": "Không"}])
            return []
        else:
            message += finished_matches
            if scheduled_matches != "":
                message += "Các trận đấu chưa diễn ra:\n"
                message += scheduled_matches
        dispatcher.utter_message(json_message={'text': message, 'parse_mode': 'html'})

        return []


class GetMatch(Action):
    def name(self) -> Text:
        return "action_provide_match_infor"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # print("in GetMatch.run")
        entities = tracker.latest_message['entities']
        teams_set = set()
        for entity in entities:
            if entity['entity'] == "club_name":
                teams_set.add(entity['value'])
        print(len(teams_set))
        if len(teams_set) < 2 or len(teams_set) > 2:
            dispatcher.utter_message(text="Xin lỗi, tôi không hiểu ý của bạn. Nếu bạn muốn thông tin về trận đấu, "
                                          "hãy cho tôi tên của đúng 2 đội bóng")
            return []

        teams_list = list(teams_set)
        team1 = find_team_by_name(teams_list[0])
        team2 = find_team_by_name(teams_list[1])

        if len(team1) < 1 or len(team2) < 1:
            dispatcher.utter_message(text="Bạn xem lại tên đội bóng giúp mình với :^")

        team_name1 = team1[0]['name']
        team_name2 = team2[0]['name']

        print("name: " + team_name1 + ", " + team_name2)
        matches_data = get_data('matches')
        matches = matches_data['matches']
        found = 0
        for match in matches:
            if (match['homeTeam']['name'] == team_name1 and match['awayTeam']['name'] == team_name2) or (
                    match['homeTeam']['name'] == team_name2 and match['awayTeam']['name'] == team_name1):
                found += 1
                utc_time_str = match['utcDate']
                local_time = utc_to_local_time(utc_time_str)
                local_time_str = datetime.strftime(local_time, "%H:%M ngày %d/%m/%Y")

                message = '{home} {h}{notation}{a} {away}  {time}'
                h_score = ""
                a_score = ""
                notation = "vs"
                if match['status'] == "FINISHED":
                    h_score = str(match['score']['fullTime']['homeTeam'])
                    a_score = str(match['score']['fullTime']['awayTeam'])
                    notation = ":"
                dispatcher.utter_message(text=message.format(home=teams_name[match['homeTeam']['name']],
                                                             h=h_score, notation=notation, a=a_score,
                                                             away=teams_name[match['awayTeam']['name']],
                                                             time=local_time_str))
                if found == 2:
                    break
