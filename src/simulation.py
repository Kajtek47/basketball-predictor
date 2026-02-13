import random
from collections import defaultdict
import pandas as pd

class MonteCarloEngine:
    def __init__(self, elo_engine, df_standings, df_future):
        self.elo = elo_engine

        self.current_standings = {}
        for row in df_standings.itertuples():
            team = getattr(row, 'Team_Short')
            pts = getattr(row, 'Points')
            if team:
                self.current_standings[team] = int(pts)

        self.future_matches = []
        for row in df_future.itertuples():
            home = getattr(row, 'Home_Short')
            away = getattr(row, 'Away_Short')
            if home and away:
                self.future_matches.append((home, away))

    def _simulate_single_season(self):
        sim_standings = self.current_standings.copy()

        for home_team, away_team in self.future_matches:
            winner_side = self.elo.simulate_single_match(home_team, away_team)

            if winner_side == 'HOME':
                sim_standings[home_team] += 2
                sim_standings[away_team] += 1
            else:
                sim_standings[home_team] += 1
                sim_standings[away_team] += 2

        return sim_standings
    
    def run(self, iterations):
        print("\n Monte Carlo simulation started")

        stats = defaultdict(lambda: {'win': 0, 'playoff': 0, 'relegation': 0, 'expected_pts': 0})

        num_teams = len(self.current_standings)

        for i in range(iterations):
            final_points = self._simulate_single_season()
            standings_list = list(final_points.items())

            random.shuffle(standings_list)
            standings_list.sort(key=lambda x: x[1], reverse=True)
        
            for rank, (team, final_pts) in enumerate(standings_list):
                stats[team]['expected_pts'] += final_pts

                if rank == 0:
                    stats[team]['win'] += 1

                if rank < 8:
                    stats[team]['playoff'] += 1
                
                if rank >= num_teams - 2:
                    stats[team]['relegation'] += 1
            
        results = []
        all_teams = list(self.current_standings.keys())

        for team in all_teams:
            team_stats = stats[team]

            exp_points = team_stats['expected_pts'] / iterations

            results.append({
                'Team': team,
                'Expected_Points': round(exp_points, 1),
                'Win_Probability': round((team_stats['win'] / iterations) * 100, 4),
                'Playoff_Probability': round((team_stats['playoff'] / iterations) * 100, 4),
                'Relegation_Probability': round((team_stats['relegation'] / iterations) * 100, 4)
            })
        
        results.sort(key = lambda x: x['Expected_Points'], reverse=True)
        
        return results