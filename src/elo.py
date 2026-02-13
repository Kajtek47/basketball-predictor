import math
import random

class EloEngine:
    def __init__(self, k_factor=20, home_advantage=70, initial_rating=1500):
        self.k = k_factor
        self.hca = home_advantage
        self.initial_rating = initial_rating

        self.ratings = {}

        self.history = []

    def get_rating(self, team):
        return self.ratings.get(team, self.initial_rating)
    
    def calculate_prob(self, rating_a, rating_b):
        prob = 1 / (1 + 10 ** ((rating_b - rating_a) / 400))
        return prob

    def update(self, home_team, away_team, home_points, away_points):
        r_home = self.ratings.get(home_team, self.initial_rating)
        r_away = self.ratings.get(away_team, self.initial_rating)

        diff = abs(home_points - away_points)

        # check who wins (1.0 for home, 0.0 for away)
        actual_score = 1.0 if home_points > away_points else 0.0

        # expected result
        r_home_effective = r_home + self.hca
        expected_score = self.calculate_prob(r_home_effective, r_away)

        # margin of victory multiplier
        mov_multiplier = math.log(diff + 1)

        if mov_multiplier < 1:
            mov_multiplier = 1

        # delta calculation
        k_dynamic = self.k * mov_multiplier
        delta = k_dynamic * (actual_score - expected_score)

        # update ratings
        self.ratings[home_team] = r_home + delta
        self.ratings[away_team] = r_away - delta

        # save in history
        self.history.append({
            'Home': home_team, 'Away': away_team,
            'Home_Elo_Before': r_home, 'Away_Elo_Before': r_away,
            'Diff': diff, 'Delta': delta,
            'Home_Elo_After': self.ratings[home_team], 
            'Away_Elo_After': self.ratings[away_team]
        })
        
    def process_season(self, df):
        for row in df.itertuples():
            self.update(
                home_team=row.Home_Short,
                away_team=row.Away_Short,
                home_points=row.Pts_Home,
                away_points=row.Pts_Away
            )

    def simulate_single_match(self, home_team, away_team):
        r_home = self.ratings.get(home_team, self.initial_rating)
        r_away = self.ratings.get(away_team, self.initial_rating)

        win_prob = self.calculate_prob(r_home + self.hca, r_away)

        random_roll = random.random()

        if random_roll < win_prob:
            return 'HOME'
        else:
            return 'AWAY'