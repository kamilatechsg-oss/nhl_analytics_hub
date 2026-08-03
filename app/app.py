import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from streamlit_option_menu import option_menu

# create the connection
engine = create_engine("postgresql://kamila:1234@localhost:5432/nhl_analytics")

with st.sidebar:
    page = option_menu(
        menu_title="NHL Analytics Hub",
        options=["Home", "Standings", "Team Info", "Player Search",
                 "Game Results", "Leaderboards", "SQL Query"],
        icons=["house", "list-ol", "shield", "person-badge",
               "calendar-event", "trophy", "terminal"],
        default_index=0,
    )

# ============================================================
# HOME
# ============================================================
if page == "Home":
    st.title("🏒 NHL Analytics Hub")
    st.write("API-driven hockey data pipeline with SQL analysis and Streamlit dashboard")

    counts = pd.read_sql("""
        SELECT
            (SELECT COUNT(*) FROM teams) AS teams,
            (SELECT COUNT(*) FROM players) AS players,
            (SELECT COUNT(*) FROM games) AS games,
            (SELECT COALESCE(SUM(goals_for), 0) FROM standings) AS goals
    """, engine).iloc[0]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Teams", int(counts.teams))
    with col2:
        st.metric("Total Players", int(counts.players))
    with col3:
        st.metric("Total Games", int(counts.games))
    with col4:
        st.metric("Total Goals", int(counts.goals))

    st.divider()

    col1, col2, col3 = st.columns(3)
    with col1:
        top_scorer = pd.read_sql("""
            SELECT p.first_name, p.last_name, s.points
            FROM skater_season_stats s
            JOIN players p ON s.player_id = p.player_id
            WHERE s.points IS NOT NULL
            ORDER BY s.points DESC LIMIT 1
        """, engine).iloc[0]
        st.metric("Top Scorer", f"{top_scorer.first_name} {top_scorer.last_name}", f"{top_scorer.points} pts")

    with col2:
        best_goalie = pd.read_sql("""
            SELECT p.first_name, p.last_name, g.save_pct
            FROM goalie_season_stats g
            JOIN players p ON g.player_id = p.player_id
            WHERE g.games_played >= 10
            ORDER BY g.save_pct DESC LIMIT 1
        """, engine).iloc[0]
        st.metric("Best Save %", f"{best_goalie.first_name} {best_goalie.last_name}", f"{best_goalie.save_pct:.3f}")

    with col3:
        league_leader = pd.read_sql("""
            SELECT t.team_name, s.points
            FROM standings s
            JOIN teams t ON s.team_id = t.team_id
            ORDER BY s.points DESC LIMIT 1
        """, engine).iloc[0]
        st.metric("League Leader", league_leader.team_name, f"{league_leader.points} pts")

# ============================================================
# STANDINGS
# ============================================================
elif page == "Standings":
    st.title("League Standings")

    conference = st.selectbox("Filter by Conference", ["All", "Eastern", "Western"])

    if conference == "All":
        query = """
            SELECT t.team_name, t.conference_name, t.division_name,
                   s.wins, s.losses, s.points, s.goals_for, s.goals_against
            FROM standings s
            JOIN teams t ON s.team_id = t.team_id
            ORDER BY s.points DESC
        """
        df = pd.read_sql(query, engine)
    else:
        query = """
            SELECT t.team_name, t.conference_name, t.division_name,
                   s.wins, s.losses, s.points, s.goals_for, s.goals_against
            FROM standings s
            JOIN teams t ON s.team_id = t.team_id
            WHERE t.conference_name = %(conf)s
            ORDER BY s.points DESC
        """
        df = pd.read_sql(query, engine, params={"conf": conference})

    st.dataframe(df, use_container_width=True, hide_index=True)

# ============================================================
# TEAM INFO
# ============================================================
elif page == "Team Info":
    st.title("Team Info")

    teams_list = pd.read_sql("SELECT team_id, team_name FROM teams ORDER BY team_name", engine)
    selected_team = st.selectbox("Select Team", teams_list["team_name"])

    team_id = int(teams_list.loc[teams_list["team_name"] == selected_team, "team_id"].iloc[0])

    team_info = pd.read_sql(
        "SELECT * FROM teams WHERE team_id = %(tid)s",
        engine, params={"tid": team_id}
    ).iloc[0]

    col1, col2 = st.columns([1, 3])
    with col1:
        if team_info.logo_url:
            st.image(team_info.logo_url, width=150)
    with col2:
        st.subheader(team_info.team_name)
        st.write(f"**Conference:** {team_info.conference_name}")
        st.write(f"**Division:** {team_info.division_name}")

    st.divider()
    st.subheader("Team Roster")

    roster = pd.read_sql(
        'SELECT first_name, last_name, "position", jersey_number, shoots_catches '
        'FROM players WHERE team_id = %(tid)s ORDER BY "position", last_name',
        engine, params={"tid": team_id}
    )
    st.dataframe(roster, use_container_width=True, hide_index=True)

# ============================================================
# PLAYER SEARCH
# ============================================================
elif page == "Player Search":
    st.title("Player Search")

    search = st.text_input("Search by player name")

    if search:
        results = pd.read_sql(
            """
            SELECT p.player_id, p.first_name, p.last_name, p."position",
                   t.team_name, p.headshot_url
            FROM players p
            JOIN teams t ON p.team_id = t.team_id
            WHERE p.first_name ILIKE %(q)s OR p.last_name ILIKE %(q)s
            ORDER BY p.last_name
            """,
            engine, params={"q": f"%{search}%"}
        )

        if results.empty:
            st.info("No players found.")
        else:
            for _, p in results.iterrows():
                with st.container(border=True):
                    col1, col2 = st.columns([1, 4])
                    with col1:
                        if p.headshot_url:
                            st.image(p.headshot_url, width=100)
                    with col2:
                        st.markdown(f"### {p.first_name} {p.last_name}")
                        st.write(f"{p.position} — {p.team_name}")

                        skater_stats = pd.read_sql(
                            "SELECT * FROM skater_season_stats WHERE player_id = %(pid)s",
                            engine, params={"pid": int(p.player_id)}
                        )
                        if not skater_stats.empty:
                            s = skater_stats.iloc[0]
                            sc1, sc2, sc3, sc4 = st.columns(4)
                            sc1.metric("Goals", int(s.goals) if pd.notna(s.goals) else 0)
                            sc2.metric("Assists", int(s.assists) if pd.notna(s.assists) else 0)
                            sc3.metric("Points", int(s.points) if pd.notna(s.points) else 0)
                            sc4.metric("Games", int(s.games_played) if pd.notna(s.games_played) else 0)
                        else:
                            goalie_stats = pd.read_sql(
                                "SELECT * FROM goalie_season_stats WHERE player_id = %(pid)s",
                                engine, params={"pid": int(p.player_id)}
                            )
                            if not goalie_stats.empty:
                                g = goalie_stats.iloc[0]
                                sc1, sc2, sc3 = st.columns(3)
                                sc1.metric("Wins", int(g.wins) if pd.notna(g.wins) else 0)
                                sc2.metric("Save %", f"{g.save_pct:.3f}" if pd.notna(g.save_pct) else "-")
                                sc3.metric("Shutouts", int(g.shutouts) if pd.notna(g.shutouts) else 0)
    else:
        st.info("Enter a player name above to search.")

# ============================================================
# GAME RESULTS
# ============================================================
elif page == "Game Results":
    st.title("Game Results")

    teams_list = pd.read_sql("SELECT team_id, team_name FROM teams ORDER BY team_name", engine)

    col1, col2 = st.columns(2)
    with col1:
        team_filter = st.selectbox("Team", ["All"] + list(teams_list["team_name"]))
    with col2:
        state_filter = st.radio("Game State", ["All", "Final", "Upcoming"], horizontal=True)

    where_clauses = []
    params = {}

    if team_filter != "All":
        tid = int(teams_list.loc[teams_list["team_name"] == team_filter, "team_id"].iloc[0])
        where_clauses.append("(g.home_team_id = %(tid)s OR g.away_team_id = %(tid)s)")
        params["tid"] = tid

    if state_filter == "Final":
        where_clauses.append("g.game_state = 'FINAL'")
    elif state_filter == "Upcoming":
        where_clauses.append("g.game_state = 'FUT'")

    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

    query = f"""
        SELECT g.game_date, ht.team_name AS home_team, g.home_score,
               at.team_name AS away_team, g.away_score, g.game_state, g.venue_name
        FROM games g
        JOIN teams ht ON ht.team_id = g.home_team_id
        JOIN teams at ON at.team_id = g.away_team_id
        {where_sql}
        ORDER BY g.game_date DESC
    """
    df = pd.read_sql(query, engine, params=params if params else None)
    st.dataframe(df, use_container_width=True, hide_index=True)

# ============================================================
# LEADERBOARDS
# ============================================================
elif page == "Leaderboards":
    st.title("Leaderboards")

    tab1, tab2, tab3, tab4 = st.tabs(["Top Scorers", "Most Penalty Minutes", "Best Save %", "Most Wins"])

    with tab1:
        df = pd.read_sql("""
            SELECT p.first_name, p.last_name, t.team_name, s.points, s.goals, s.assists
            FROM skater_season_stats s
            JOIN players p ON s.player_id = p.player_id
            JOIN teams t ON s.team_id = t.team_id
            ORDER BY s.points DESC LIMIT 20
        """, engine)
        st.dataframe(df, use_container_width=True, hide_index=True)

    with tab2:
        df = pd.read_sql("""
            SELECT p.first_name, p.last_name, t.team_name, s.penalty_min
            FROM skater_season_stats s
            JOIN players p ON s.player_id = p.player_id
            JOIN teams t ON s.team_id = t.team_id
            ORDER BY s.penalty_min DESC LIMIT 20
        """, engine)
        st.dataframe(df, use_container_width=True, hide_index=True)

    with tab3:
        df = pd.read_sql("""
            SELECT p.first_name, p.last_name, t.team_name, g.save_pct, g.games_played
            FROM goalie_season_stats g
            JOIN players p ON g.player_id = p.player_id
            JOIN teams t ON g.team_id = t.team_id
            WHERE g.games_played >= 10
            ORDER BY g.save_pct DESC LIMIT 20
        """, engine)
        st.dataframe(df, use_container_width=True, hide_index=True)

    with tab4:
        df = pd.read_sql("""
            SELECT p.first_name, p.last_name, t.team_name, g.wins
            FROM goalie_season_stats g
            JOIN players p ON g.player_id = p.player_id
            JOIN teams t ON g.team_id = t.team_id
            ORDER BY g.wins DESC LIMIT 20
        """, engine)
        st.dataframe(df, use_container_width=True, hide_index=True)

# ============================================================
# SQL QUERY
# ============================================================
elif page == "SQL Query":
    st.title("SQL Query Runner")

    prebuilt = {
        "-- Select a query --": "",
        "Top team by total goals": """
            SELECT t.team_name, s.goals_for
            FROM standings s JOIN teams t ON s.team_id = t.team_id
            ORDER BY s.goals_for DESC LIMIT 1;
        """,
        "Top 5 point scorers": """
            SELECT p.first_name, p.last_name, t.team_name, s.points
            FROM skater_season_stats s
            JOIN players p ON s.player_id = p.player_id
            JOIN teams t ON s.team_id = t.team_id
            ORDER BY s.points DESC LIMIT 5;
        """,
        "Divisions with avg points > 90": """
            SELECT t.division_name, AVG(s.points) AS avg_points
            FROM standings s JOIN teams t ON s.team_id = t.team_id
            GROUP BY t.division_name
            HAVING AVG(s.points) > 90
            ORDER BY avg_points DESC;
        """,
    }

    choice = st.selectbox("Pick a ready-made query", list(prebuilt.keys()))
    default_sql = prebuilt[choice].strip()

    query_text = st.text_area("SQL Query", value=default_sql, height=150)

    if st.button("Run Query"):
        if not query_text.strip().lower().startswith("select"):
            st.error("Only SELECT queries are allowed.")
        else:
            try:
                result = pd.read_sql(query_text, engine)
                st.success(f"{len(result)} rows returned")
                st.dataframe(result, use_container_width=True, hide_index=True)
            except Exception as e:
                st.error(f"SQL error: {e}")