import random
from collections import defaultdict

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

        winner = max(sim_standings, key=sim_standings.get)
        return winner
    
    def run(self, iterations=10000):
        print("\n Monte Carlo simulation started")

        winners_count = defaultdict(int)

        for i in range(iterations):
            winner = self._simulate_single_season()
            winners_count[winner] += 1

        results = []
        for team, wins in winners_count.items():
            probability = (wins / iterations) * 100
            results.append({
                'Team': team,
                'P': round(probability, 1)
            })
        
        results.sort(key = lambda x: x['Win_Prob'], reverse=True)

        return results