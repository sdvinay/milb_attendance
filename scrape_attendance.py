import requests
import numpy as np
import pandas as pd
import typer
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')


def get_schedule_url(sport_id: int, season: int = 2022) -> str:
    return f'https://statsapi.mlb.com/api/v1/schedule?language=en&sportId={sport_id}&season={season}&sortBy=gameDate&hydrate=gameInfo'


def get_attendance_sport_id(sport_id: int, season: int = 2022) -> pd.DataFrame:
    schedule_url = get_schedule_url(sport_id, season)
    schedule_data = requests.get(schedule_url).json()
    all_gms = pd.json_normalize(schedule_data['dates'], record_path=['games']).set_index('gamePk')
    played_gms = all_gms.dropna(subset=['isTie']).copy() # filter to include only completed/current games
    logging.info(f'get_attendance_sport_id sport_id={sport_id} season={season};  returning {len(played_gms)} games')

    return played_gms

def get_attendance_all_levels(season: int = 2022) -> pd.DataFrame:
    # Each MILB level has its own sport_id, so iterate over them
    milb_sport_ids = [11, 12, 13, 14, 23]
    df = pd.concat([get_attendance_sport_id(id, season) for id in milb_sport_ids])
    logging.info(f'get_attendance_all_levels season={season};  returning {len(df)} games')
    return df

def write_gbg_output(gms: pd.DataFrame, output_file: str) -> None:
    df_out = generate_gbg_report(gms)
    write_report_out(df_out, output_file)
    
def generate_gbg_report(gms: pd.DataFrame) -> pd.DataFrame:
    output_fields = ['officialDate','teams.home.team.name', 'abbreviation','league.name',
       'gameInfo.attendance', 'dayNight', 'dayOfWeek', 'teams.away.team.name']

    df_out = gms
    df_out['dayOfWeek'] = pd.to_datetime(df_out['officialDate']).dt.day_name()
    df_out['gameInfo.attendance'] = df_out['gameInfo.attendance'].fillna(0).apply(int)

    team_map = pd.read_csv('output/tm_to_league.csv').set_index('id')
    df_out = pd.merge(left=df_out, right=team_map, left_on='teams.home.team.id', right_index=True)
    df_out = df_out.sort_values(by=['officialDate', 'sortOrder', 'league.id'], ascending=[False, True, True])[output_fields]
    logging.info(f'generate_gbg_report returning report {len(df_out)} games')
    return df_out

def write_report_out(df_out: pd.DataFrame, output_file: str) -> None:
    df_out.to_csv(output_file)
    df_out.to_html(f'{output_file}.html')

def write_summary_report(gms: pd.DataFrame, output_file: str) -> None:
    df_out = generate_summary_report(gms)
    write_report_out(df_out, output_file)


def generate_summary_report(gms: pd.DataFrame) -> pd.DataFrame:
    output_fields = ['teams.home.team.name', 'abbreviation','league.name', 'num_games', 'total_att', 'avg_att']
    totals = gms.groupby(['teams.home.team.id', 'teams.home.team.name']).agg(num_games=('gameInfo.attendance', len), total_att=('gameInfo.attendance', sum),  avg_att=('gameInfo.attendance', np.mean))
    team_map = pd.read_csv('output/tm_to_league.csv').set_index('id')
    df_out = pd.merge(left=totals.reset_index().set_index('teams.home.team.id'), right=team_map, left_index=True, right_index=True)
    for col in ['total_att', 'avg_att']:
        df_out[col] = df_out[col].astype(int)
    df_out = df_out.sort_values(by=['sortOrder', 'league.id', 'avg_att'], ascending=[True, True, False])[output_fields]
    logging.info(f'generate_summary_report returning report {len(df_out)} teams')
    return df_out

def generate_team_map(season: int = 2022) -> pd.DataFrame:
    TEAMS_URL = f'https://statsapi.mlb.com/api/v1/teams?season={season}'
    SPORTS_URL = f'https://statsapi.mlb.com/api/v1/sports?season={season}'

    r_tms = requests.get(TEAMS_URL).json()['teams']
    r_sports = requests.get(SPORTS_URL).json()['sports']
    tms = pd.json_normalize(r_tms).set_index('id')[['name', 'league.name', 'league.id', 'sport.id']]
    levels = pd.json_normalize(r_sports).set_index('id')[['abbreviation', 'sortOrder']]
    team_map = tms.merge(right=levels, left_on=['sport.id'], right_index=True)
    logging.info(f'generate_team_map season={season} reporting {len(team_map)} teams')
    return team_map.sort_index()

def main(season: int = 2022) -> None:
    att = get_attendance_all_levels(season)
    write_gbg_output(att, f'output/attendance_{season}.txt')    
    write_summary_report(att, f'output/attendance_summary_{season}.txt')    
    

if __name__ == "__main__":
    
    typer.run(main) # typer will enable user to set the season from the command line with --season