import requests
import pandas as pd


def get_schedule_url(sport_id, season=2022):
    return f'https://statsapi.mlb.com/api/v1/schedule?language=en&sportId={sport_id}&season={season}&sortBy=gameDate&hydrate=gameInfo'


fieldnames = ['gamePk', 'gameType', 'officialDate', 'dayNight',
 'teams.away.team.id', 'teams.away.team.name', 'teams.home.team.id',
 'teams.home.team.name', 'gameInfo.attendance']

today = str(pd.Timestamp.today().date())

def get_attendance_df(sport_id, season = 2022):
    sch = requests.get(get_schedule_url(sport_id, season)).json()
    df = pd.json_normalize(sch['dates'], record_path=['games'])[fieldnames].set_index('gamePk').query('officialDate < @today')
    df['dayOfWeek'] = pd.to_datetime(df['officialDate']).dt.day_name()
    return df

def main(season = 2022):
    # Each MILB level has its own sport_id, so iterate over them
    att = pd.concat([get_attendance_df(sport_id, season) for sport_id in [11, 12, 13, 14]])
    att.sort_values('officialDate', ascending=False).to_csv(f'attendance_{season}.txt')
    

if __name__ == "__main__":
    main()