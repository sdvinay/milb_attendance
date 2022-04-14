import requests
import csv
import pandas as pd


def get_schedule_url(sport_id, season=2022):
    return f'https://statsapi.mlb.com/api/v1/schedule?language=en&sportId={sport_id}&season={season}&sortBy=gameDate&hydrate=gameInfo,team'

sch = requests.get(get_schedule_url(11))

def write_game_data(gm, writer):
    data = [gm['gamePk'], gm['officialDate'], gm['dayNight'], pd.Timestamp(gm['officialDate']).day_name(), 
        gm['teams']['home']['team']['league']['name'],
        gm['gameInfo']['attendance'],
        gm['teams']['home']['team']['id'], gm['teams']['home']['team']['name'], 
        gm['teams']['away']['team']['id'], gm['teams']['away']['team']['name']]
    writer.writerow(data)

season = 2022
with open(f'attendance_{season}.txt', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')

    for sport_id in [11, 12, 13, 14]:
        sch = requests.get(get_schedule_url(sport_id, season))
        for dt in sch.json()['dates']:
            for gm in dt['games']:
                if 'attendance' in gm['gameInfo']:
                    write_game_data(gm, writer)