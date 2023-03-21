from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import scrape_attendance as sa

app = FastAPI()

@app.get("/team_map", response_class=HTMLResponse)
# Merge the teams with league data to get additional information (level, sortOrder)
def generate_team_map(season: int = 2022) -> HTMLResponse:
    df = sa.generate_team_map(season)
    html = df.to_html()
    return HTMLResponse(content=html)
