-- Query 1: Which team scored the most total goals this season?
-- (Aggregation + ORDER BY)
SELECT t.team_name, s.goals_for
FROM standings s
JOIN teams t ON s.team_id = t.team_id
ORDER BY s.goals_for DESC
LIMIT 1;

-- Query 2: Top 5 point scorers across the entire league
-- (JOIN + ORDER BY)
SELECT p.first_name, p.last_name, s.points
FROM skater_season_stats s
JOIN players p ON s.player_id = p.player_id
ORDER BY s.points DESC
LIMIT 5;

-- Query 3: Players with more than 20 goals AND more than 30 assists this season
-- (WHERE with multiple conditions)
SELECT p.first_name, p.last_name, s.goals, s.assists
FROM skater_season_stats s
JOIN players p ON s.player_id = p.player_id
WHERE s.goals > 20 AND s.assists > 30
ORDER BY s.points DESC;

-- Query 4: Teams with a season points total above the league average
-- (Subquery)
SELECT t.team_name, s.points
FROM standings s
JOIN teams t ON s.team_id = t.team_id
WHERE s.points > (SELECT AVG(points) FROM standings)
ORDER BY s.points DESC;

-- Query 5: Divisions with an average team points total above 90
-- (GROUP BY + HAVING)
SELECT t.division_name, AVG(s.points) AS avg_points
FROM standings s
JOIN teams t ON s.team_id = t.team_id
GROUP BY t.division_name
HAVING AVG(s.points) > 90
ORDER BY avg_points DESC;

-- Query 6: Goalies with the best save percentage (minimum 20 games played)
-- (Aggregation + WHERE + ORDER BY)
SELECT p.first_name, p.last_name, t.team_name, g.save_pct, g.games_played
FROM goalie_season_stats g
JOIN players p ON g.player_id = p.player_id
JOIN teams t ON g.team_id = t.team_id
WHERE g.games_played >= 20
ORDER BY g.save_pct DESC
LIMIT 10;

-- Query 7: Team win totals ranked within each conference
-- (JOIN + ORDER BY, conference-level rollup)
SELECT t.conference_name, t.team_name, s.wins
FROM standings s
JOIN teams t ON s.team_id = t.team_id
ORDER BY t.conference_name, s.wins DESC;

-- Query 8: Players who scored a hat trick (3+ goals) in a single game
-- (WHERE on per-game data, not season totals)
SELECT p.first_name, p.last_name, gm.game_date, gs.goals, t.team_name
FROM game_stats gs
JOIN players p ON gs.player_id = p.player_id
JOIN games gm ON gs.game_id = gm.game_id
JOIN teams t ON gs.team_id = t.team_id
WHERE gs.goals >= 3
ORDER BY gm.game_date DESC;

-- Query 9: Teams with above-average penalty minutes per game
-- (Subquery in HAVING)
SELECT t.team_name, ROUND(AVG(gs.penalty_min), 2) AS avg_pim_per_game
FROM game_stats gs
JOIN teams t ON gs.team_id = t.team_id
GROUP BY t.team_name
HAVING AVG(gs.penalty_min) > (SELECT AVG(penalty_min) FROM game_stats)
ORDER BY avg_pim_per_game DESC;

-- Query 10: Home vs away win counts per team
-- (Conditional aggregation using FILTER)
SELECT
    t.team_name,
    COUNT(*) FILTER (WHERE gm.home_team_id = t.team_id AND gm.home_score > gm.away_score) AS home_wins,
    COUNT(*) FILTER (WHERE gm.away_team_id = t.team_id AND gm.away_score > gm.home_score) AS away_wins
FROM teams t
JOIN games gm ON t.team_id IN (gm.home_team_id, gm.away_team_id)
WHERE gm.game_state = 'FINAL'
GROUP BY t.team_name
ORDER BY t.team_name;

-- Query 11: Top 5 teams by goal differential (goals for minus goals against)
-- (Calculated column + ORDER BY)
SELECT t.team_name, s.goals_for, s.goals_against, (s.goals_for - s.goals_against) AS goal_diff
FROM standings s
JOIN teams t ON s.team_id = t.team_id
ORDER BY goal_diff DESC
LIMIT 5;

-- Query 12: Number of players per team by position
-- (GROUP BY with multiple columns)
SELECT t.team_name, p."position", COUNT(*) AS player_count
FROM players p
JOIN teams t ON p.team_id = t.team_id
GROUP BY t.team_name, p."position"
ORDER BY t.team_name, p."position";