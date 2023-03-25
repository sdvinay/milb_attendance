from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from timing_asgi import TimingMiddleware, TimingClient
from timing_asgi.integrations import StarletteScopeToName
import scrape_attendance as sa

class PrintTimings(TimingClient):
    def timing(self, metric_name, timing, tags):
        print(metric_name, timing, tags)


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

@app.get("/gbg_report", response_class=HTMLResponse)
def generate_gbg_report(season: int = 2022) -> HTMLResponse:
    att = sa.get_attendance_all_levels(season)
    df = sa.generate_gbg_report(att)
    html = df.to_html()
    return HTMLResponse(content=html)

app.add_middleware(
    TimingMiddleware,
    client=PrintTimings(),
    metric_namer=StarletteScopeToName(prefix="myapp", starlette_app=app)
)