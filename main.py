from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import scrape_attendance as sa

app = FastAPI()

@app.get("/team_map", response_class=HTMLResponse)
def generate_team_map(season: int = 2022) -> HTMLResponse:
    df = sa.generate_team_map(season)
    html = df.to_html()
    return HTMLResponse(content=html)

@app.get("/summary_report", response_class=HTMLResponse)
def generate_summary_report(season: int = 2022) -> HTMLResponse:
    att = sa.get_attendance_all_levels(season)
    df = sa.generate_summary_report(att)
    html = df.to_html()
    return HTMLResponse(content=html)