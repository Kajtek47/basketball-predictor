import pandas as pd
import requests
import numpy as np
import re

# Constant URLs
URL_TABLE = "https://1lm.pzkosz.pl/tabele.html"
URL_SCHEDULE = "https://1lm.pzkosz.pl/terminarz-i-wyniki.html"

# Headers to mimic a browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def get_standings():
    print("Downloading table standings")
    try:
        response = requests.get(URL_TABLE, headers=HEADERS)
        dfs = pd.read_html(response.text)
        df = dfs[0]

        # Data cleaning
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

        if 'zw.-por.' in df.columns:
            df[['Wins', 'Loses']] = df['zw.-por.'].str.split(' - ', expand=True).astype(int)

        if 'pkt.zd.-pkt.str.' in df.columns:
            df[['Pts_Scored', 'Pts_Lost']] = df['pkt.zd.-pkt.str.'].str.split(' - ', expand=True).astype(int)

        rename_map = {
            'm': 'Place', 'drużyna': 'Team', 'pkt': 'Points', 'mecze': 'Games', 'różnica': 'Pts_Diff'
        }
        df.rename(columns=rename_map)

        # Choose final columns
        final_cols = ['Place', 'Team', 'Games', 'Points', 'Wins', 'Loses', 'Pts_Scored', 'Pts_Lost', 'Pts_Diff']
        final_cols = [c for c in final_cols if c in df.columns]

        return df[final_cols]
    
    except Exception as e:
        print(f"Error while downloading standings: {e}")
        return pd.DataFrame()
    
def get_schedule():
    print("Downloading the schedule")
    try:
        response = requests.get(URL_SCHEDULE, headers=HEADERS)
        dfs = pd.read_html(response.text)
        df = pd.concat(dfs, ignore_index=True)

        df = df.astype(str)

        col_info = df.columns[0]
        col_score = df.columns[-1]

        def extract_score(val):
            match = re.search(r'(\d+:\d+)', val)
            if match:
                return match.group(1)
            return None
        
        df['Result'] = df[col_score].apply(extract_score)

        # Divide into played and future games
        df_played = df[df['Result'].notna()].copy()
        df_future = df[df['Result'].isna()].copy()

        df_played[['Pts_Home', 'Pts_Away']] = df_played['Result'].str.split(':', expand=True).astype(int)

        def parse_teams(text):
            clean_text = text.split(" Emocje TV")[0]
            parts = clean_text.split(" - ")
            if len(parts) > 2:
                return parts[0].strip(), parts[1].strip()
            return 'Unknown', 'Unknown'
        
        df_played[['Home', 'Away']] = df_played[col_info].apply(lambda x: pd.Series(parse_teams(x)))
        df_played['Data'] = df_played[col_score].apply(lambda x: x.split("  ")[0] if "  " in x else x.replace(x.split()[-1], "").strip())

        df_future[['Home', 'Away']] = df_future[col_info].apply(lambda x: pd.Series(parse_teams(x)))
        df_future['Data'] = df_future[col_score]

        cols_played = ['Data', 'Home', 'Away', 'Pts_Home', 'Pts_Away']
        cols_future = ['Data', 'Home', 'Away']

        return df_played[cols_played], df_future[cols_future]
    
    except Exception as e:
        print(f"Schedule error: {e}")
        return pd.DataFrame, pd.DataFrame()