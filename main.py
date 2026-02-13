import os
import pandas as pd
from src import scraper
from src.elo import EloEngine
from src.simulation import MonteCarloEngine

# Path configuration
DATA_DIR = 'data'
FILE_TABLE = os.path.join(DATA_DIR, 'table.csv')
FILE_GAMES = os.path.join(DATA_DIR, 'matches_played.csv')
FILE_SCHEDULE = os.path.join(DATA_DIR, 'matches_future.csv')

def main():
    print("Data processing started")

    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f"Created folder: {DATA_DIR}")

    df_table = scraper.get_standings()
    if not df_table.empty:
        df_table.to_csv(FILE_TABLE, index=False)
        print("Table saved successfully")
    else:
        print("Empty table - check connection")

    df_played, df_future = scraper.get_schedule()

    if not df_played.empty:
        df_played.to_csv(FILE_GAMES, index=False)
        print("Played games saved successfully")
    
    if not df_future.empty:
        df_future.to_csv(FILE_SCHEDULE, index=False)
        print("Future schedule saved successfully")

    if not df_played.empty:
        engine = EloEngine()
        engine.process_season(df_played)

    if not df_future.empty and not df_table.empty:
        mc = MonteCarloEngine(engine, df_table, df_future)

        results = mc.run(iterations=1000000)

        df_results = pd.DataFrame(results)
        print(df_results.to_string(index=False))

if __name__ == "__main__":
    main()