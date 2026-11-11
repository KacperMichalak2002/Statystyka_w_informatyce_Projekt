# Football statistics 2025/26

An interactive web application for exploring match statistics from the top five European football leagues in the 2025/26 season (Premier League, La Liga, Serie A, Bundesliga, Ligue 1). It shows how goals, shots, corners, fouls, cards and betting odds are distributed, how they relate to each other, and how leagues and teams compare — all through visual, picture-based charts.

Data source: [football-data.co.uk](https://www.football-data.co.uk/) (CSV files in `Data/`).

## Running locally

Requirements: Python 3.10 or newer ([python.org](https://www.python.org/downloads/)).

### Windows

Double-click `run.bat`, or run it from the project folder in the command prompt:

```bat
run
```

On the first run it creates a local environment (`.venv`) and installs the dependencies, which takes a few minutes. The app then opens in the browser at http://localhost:8501.

### macOS / Linux

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app.py
```
