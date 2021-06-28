from fuzzywuzzy import fuzz
from actions import get_data
# print(fuzz.ratio("henderson", "jordan henderson"))
# print(fuzz.ratio("virgil vandijk", "virgil van dik"))
# print(fuzz.ratio("jurgen kloop", "Jürgen Klopp"))

# print(fuzz.WRatio("hendrsn", "jordan henderson"))
# print(fuzz.partial_ratio("henderson", "henderson"))
# print(fuzz.partial_ratio("jurgen kloop", "Jürgen Klopp"))

# data = get_data.get_players_data()
# players = data['detail']['players']
# name = "mane"
# for player in players:
#     full_name = player['first_name'] + " " + player['second_name']
#     short_name = player['web_name']
#     if fuzz.WRatio(name, full_name) > 80:
#         print(full_name + ": " + str(fuzz.WRatio(name, full_name)))
#         continue
#     if fuzz.WRatio(name, short_name) > 80:
#         print(short_name + ": " + str(fuzz.WRatio(name, short_name)))

# data = get_data.get_players_data()
# players = data['basic']['players']
# name = "mane"
# for player in players:
#     p_name = player['name']
#     if fuzz.WRatio(name, p_name) > 70:
#         print(p_name + ": " + str(fuzz.WRatio(name, p_name)))
#         continue
#     if fuzz.WRatio(name, p_name) > 70:
#         print(p_name + ": " + str(fuzz.WRatio(name, p_name)))
# data = get_data.get_managers_data()
# managers = data['managers']
#
# f = open('match.txt', 'w')
# for manager in managers:
#     f.write('- [' + manager['name'] + '](manager_name)\n')
#
# f.close()
# name = "man city"
# data = get_data.get_data('teams')
# dict_str = "{"
# for team in data['teams']:
#     if team['id'] == 563:
#         dict_str = dict_str + '"' + team['name'] + '"' + ":" + '"' + team['tla'] + '"' + "}"
#     else:
#         dict_str = dict_str + '"' + team['name'] + '"' + ":" + '"' + team['tla'] + '"' + ", "
#
# print(dict_str)
# teams = []
#
# for team in data['teams']:
#     if fuzz.WRatio(name, team['shortName']) > 80:
#         print(team['shortName'] + ": " + str(fuzz.WRatio(name, team['shortName'])))
#         continue
#     if fuzz.WRatio(name, team['tla']) > 80:
#         print(team['tla'] + ": " + str(fuzz.WRatio(name, team['tla'])))


data = get_data.get_data('teams')
teams = []

name = "Norwich City FC"
for team in data['teams']:
    if fuzz.WRatio(name, team['shortName']) > 80:
        print(team['shortName'] + ": " + str(fuzz.WRatio(name, team['shortName'])))
        continue
    if fuzz.WRatio(name, team['tla']) > 80:
        print(team['tla'] + ": " + str(fuzz.WRatio(name, team['tla'])))

# data = get_data.get_players_data()
# countries = []
# for player in data['basic']['players']:
#     countries.append(player['nationality'])
# for country in set(countries):
#     print(country)