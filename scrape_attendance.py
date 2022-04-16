import requests
import pandas as pd
import typer


def get_schedule_url(sport_id:int, season:int = 2022):
    return f'https://statsapi.mlb.com/api/v1/schedule?language=en&sportId={sport_id}&season={season}&sortBy=gameDate&hydrate=gameInfo'


fieldnames = ['gameType', 'officialDate', 'dayNight',
 'teams.away.team.id', 'teams.away.team.name', 'teams.home.team.id',
 'teams.home.team.name', 'gameInfo.attendance']

today = str(pd.Timestamp.today().date())

def get_attendance_df(sport_id:int, season:int = 2022):
    sch = requests.get(get_schedule_url(sport_id, season)).json()
    df = pd.json_normalize(sch['dates'], record_path=['games']).set_index('gamePk')
    return df

def write_output(df: pd.DataFrame, output_file: str):
    df_out = df[fieldnames].query('officialDate < @today').sort_values('officialDate', ascending=False)
    df_out['dayOfWeek'] = pd.to_datetime(df_out['officialDate']).dt.day_name()
    df_out.to_csv(output_file)

def main(season:int = 2022):
    # Each MILB level has its own sport_id, so iterate over them
    att = pd.concat([get_attendance_df(sport_id, season) for sport_id in [11, 12, 13, 14]])
    write_output(att, f'attendance_{season}.txt')    
    

if __name__ == "__main__":
    typer.run(main) # typer will enable user to set the season from the command line with --season