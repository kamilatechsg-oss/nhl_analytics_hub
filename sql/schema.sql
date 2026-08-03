CREATE TABLE TEAMS (
    team_id SERIAL PRIMARY KEY,
    TEAM_ABBREV VARCHAR (10) UNIQUE,
    TEAM_NAME VARCHAR (100) ,
    CONFERENCE_NAME VARCHAR (50),
    DIVISION_NAME VARCHAR (50),
    LOGO_URL TEXT
);
CREATE TABLE standings (
    standing_id SERIAL PRIMARY KEY,
    team_id INT REFERENCES TEAMS(team_id),
    season varchar(20),
    games_played INT,
    wins INT,
    losses INT,
    ot_losses INT,
    points INT,
    goals_for INT,
    goals_against INT,
    home_wins INT,
    away_wins INT,
    streak_type VARCHAR(20),
    streak_count INT
);
CREATE TABLE Players (
    player_id BIGINT PRIMARY KEY,
    team_id INT REFERENCES TEAMS(team_id),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    "position" VARCHAR(10),
    jersey_number INT,
    birth_date DATE,
    birth_country VARCHAR(10),
    height_cm REAL,
    weight_kg REAL,
    shoots_catches VARCHAR(5),
    headshot_url TEXT
);
CREATE TABLE GAMES (
    game_id BIGINT PRIMARY KEY,
    season VARCHAR(20),
    game_type INT,
    game_date DATE,
    home_team_id INT REFERENCES TEAMS(team_id),
    away_team_id INT REFERENCES TEAMS(team_id),
    home_score INT,
    away_score INT,
    game_state VARCHAR(20),
    venue_name VARCHAR(150)
);
create table game_stats (
    stat_id serial PRIMARY KEY,
    game_id BIGINT REFERENCES GAMES(game_id),
    player_id BIGINT REFERENCES Players(player_id),
    team_id INT REFERENCES TEAMS(team_id),
    goals INT,
    assists INT,
    points INT,
    shots_on_goal INT,
    penalty_min INT,
    toi VARCHAR(10),
    plus_minus INT
);
create table skater_season_stats (
    stat_id serial PRIMARY KEY,
    player_id BIGINT REFERENCES Players(player_id),
    season VARCHAR(20),
    team_id INT REFERENCES TEAMS(team_id),
    games_played INT,
    goals INT,
    assists INT,
    points INT,
    plus_minus INT,
    penalty_min INT,
    shots INT,
    avg_toi VARCHAR(10)
);
create table goalie_season_stats (
    stat_id serial PRIMARY KEY,
    player_id BIGINT REFERENCES Players(player_id),
    season VARCHAR(20),
    team_id INT REFERENCES TEAMS(team_id),
    games_played INT,
    wins INT,
    losses INT,
    ot_losses INT,
    save_pct FLOAT,          
    goals_against_avg FLOAT,
    shutouts INT,       
    saves INT
);