# NHL Analytics Hub

API-driven hockey data pipeline: NHL public API → PostgreSQL → SQL analysis → Streamlit dashboard.

**Database:** PostgreSQL
**Connector library:** psycopg2 (data loading) + SQLAlchemy (Streamlit app)

## Project Structure

## Setup

### 1. Install PostgreSQL and create the database

```bash
brew install postgresql@16
brew services start postgresql@16
psql -U <your_user> -h localhost -d postgres -c "CREATE DATABASE nhl_analytics;"
```

### 2. Install Python dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Run the data collection notebook

Open `notebooks/01_data_collection.ipynb` and run all cells top to bottom. This:
- Fetches team, standings, roster, and schedule data live from the NHL public API
- Loads provided datasets (`game_stats.json`, `skater_season_stats.json`, `goalie_season_stats.json`) for per-game and season stats
- Creates all 7 database tables and populates them

**Note:** rows referencing players no longer on any current roster are skipped during loading, since they would violate the foreign key constraint on `players`.

### 4. Run the SQL analysis queries

Open `sql/analysis_queries.sql` in pgAdmin's Query Tool, or run individual queries via the Streamlit app's SQL Query page.

### 5. Launch the dashboard

```bash
streamlit run app/app.py
```

## Database Schema

7 tables: `teams`, `standings`, `players`, `games`, `game_stats`, `skater_season_stats`, `goalie_season_stats`.

- `team_id` is auto-generated (`SERIAL`) since the NHL API only provides team abbreviations, not numeric IDs.
- `player_id` and `game_id` are used as-is from the NHL API (not auto-generated).
- The `position` column is quoted (`"position"`) throughout, since `POSITION` is a reserved keyword in PostgreSQL.

## Dashboard Pages

- **Home** — league-wide KPIs and highlights (top scorer, best save %, league leader)
- **Standings** — full league standings, filterable by conference
- **Team Info** — team details and roster lookup
- **Player Search** — search players by name, view season stats
- **Game Results** — browse games, filterable by team and game state
- **Leaderboards** — top scorers, penalty minutes, save %, and wins
- **SQL Query** — run custom SQL queries against the database, with pre-built examples