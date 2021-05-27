from datetime import datetime
import json
import http.client
import time
import requests

def check_for_updating(data, frequency = True):
    if 'lastUpdated' not in data:
        return True

    last_updated_str = data['lastUpdated']
    last_updated = datetime.strptime(last_updated_str, "%Y-%m-%dT%H:%M:%SZ")
    time_delta = datetime.utcnow() - last_updated
    if frequency == True and time_delta.seconds > 60*60:
        return True
    
    if frequency == False and time_delta.seconds > 60*60*24*30:
        return True
    return False

def get_data(type_of_data):

    if type_of_data not in ('teams', 'matches', 'standings'):
        print('invalid parameter')
        return None

    file_names = {'teams': 'crawl-data/teams.json', 
                'standings': 'crawl-data/standings.json',
                'matches': 'crawl-data/matches.json'}
    
    urls = {'teams': '/v2/competitions/2021/teams',
          'standings': '/v2/competitions/2021/standings',
          'matches': '/v2/competitions/2021/matches'}

    file_name = file_names[type_of_data]
    url = urls[type_of_data]

    with open(file_name, 'r') as f:
        old_data = json.load(f)

    if check_for_updating(old_data):
        #data from football-data.org api
        connection = http.client.HTTPConnection('api.football-data.org')
        headers = { 'X-Auth-Token': '102c4db9986d4763828187e1369bbdb9' }
        connection.request('GET', url, None, headers )
        data = json.loads(connection.getresponse().read().decode())

        #save last update time
        now = datetime.utcnow()
        data['lastUpdated'] = now.strftime("%Y-%m-%dT%H:%M:%SZ")

        #save data
        with open(file_name, 'w') as f:
            json.dump(data, f)
        
        return data
    
    else:
        return old_data

def get_players_data():
    file_name = 'crawl-data/players.json'

    with open(file_name, 'r') as f:
        old_data = json.load(f)
        old_players_detail = old_data['detail'] 
        old_players_basic = old_data['basic']
   
    if check_for_updating(old_players_detail):
        #data from fpl api
        url = 'https://fantasy.premierleague.com/api/bootstrap-static/'
        response = requests.get(url)
        fpl_data = json.loads(response.content.decode())
        players_detail = fpl_data['elements']

        new_players_detail = {'players': players_detail}

        #save last update time
        now = datetime.utcnow()
        new_players_detail['lastUpdated'] = now.strftime("%Y-%m-%dT%H:%M:%SZ")

    else:
        new_players_detail = old_players_detail
    
    if check_for_updating(old_players_basic, frequency=False):
        #data from football-data.org api
        teams_data = get_data("teams")
        teams = teams_data['teams']
        
        connection = http.client.HTTPConnection('api.football-data.org')
        headers = { 'X-Auth-Token': '102c4db9986d4763828187e1369bbdb9' }
        players_basic = [] 
        count = 0
        for team in teams:
            url = '/v2/teams/{id}'
            team_id = team['id']
            print("team_id: " + str(team_id))
            connection.request('GET', url.format(id = team_id), None, headers)
            response_data = json.loads(connection.getresponse().read().decode())
            count += 1
            for member in response_data['squad']:
                if member['role'] == 'PLAYER':
                    member['team'] = response_data['name']
                    players_basic.append(member)
                
            if count == 10:
                time.sleep(60)
        
        new_players_basic = {'players': players_basic}
        #save last update time
        now = datetime.utcnow()
        new_players_basic['lastUpdated'] = now.strftime("%Y-%m-%dT%H:%M:%SZ")

    else:
        new_players_basic = old_players_basic
    
    new_data = {"basic": new_players_basic, "detail": new_players_detail}
    
    with open(file_name, 'w') as f:
        json.dump(new_data, f)
    
    return new_data

def get_managers_data():

    file_name = 'crawl-data\managers.json'
    with open(file_name, 'r') as f:
        old_data = json.load(f)
    
    if check_for_updating(old_data, frequency=False):
        #data from football-data.org api
        teams_data = get_data("teams")
        teams = teams_data['teams']
        
        connection = http.client.HTTPConnection('api.football-data.org')
        headers = { 'X-Auth-Token': '102c4db9986d4763828187e1369bbdb9' }
        managers = []
        count = 0
        for team in teams:
            url = '/v2/teams/{id}'
            team_id = team['id']
            print("team_id: " + str(team_id))
            connection.request('GET', url.format(id = team_id), None, headers)
            response_data = json.loads(connection.getresponse().read().decode())
            count += 1
            for member in response_data['squad']:
                if member['role'] == 'COACH':
                    member['team'] = response_data['name']
                    member['shortNameTeam'] = response_data['shortName']
                    managers.append(member)
            
            if count == 10:
                time.sleep(60)
        
        data = {'managers': managers}
        #save last update time
        now = datetime.utcnow()
        data['lastUpdated'] = now.strftime("%Y-%m-%dT%H:%M:%SZ")

        with open(file_name, 'w') as f:
            json.dump(data, f)
        
        return data
    
    else:
        return old_data
    
