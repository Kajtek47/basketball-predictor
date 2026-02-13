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

# Map for team abbreviations
TEAM_MAP = {
    "Enea Abramczyk Astoria Bydgoszcz": "AST",
    "SKS Fulimpex Starogard Gdański": "STG",
    "Solvera Sokół Łańcut": "ŁAŃ",
    "ŁKS Coolpack Łódź": "ŁKS",
    "GKS Tychy": "GKS",
    "Decka Pelplin": "PEL",
    "WKK Active Hotel Wrocław": "WKK",
    "Enea Basket Poznań": "POZ",
    "PGE Spójnia Stargard": "SPÓ",
    "Novimex Polonia 1912 Leszno": "LES",
    "OPTeam Energia Polska Resovia": "RES",
    "KKS Polonia Warszawa": "WAR",
    "Kotwica Port Morski Kołobrzeg": "KOT",
    "KSK Qemetica Noteć Inowrocław": "INO",
    "Weegree AZS Politechnika Opolska": "OPO",
    "Miners Katowice": "KAT",
    "Żubry Abakus Okna Białystok": "BIA",
}

def get_short_name(full_name):
    if full_name in TEAM_MAP:
        return TEAM_MAP[full_name]
    
    return full_name[:3].upper()

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
        df = df.rename(columns=rename_map)

        df['Team_Short'] = df['Team'].apply(get_short_name)

        # Choose final columns
        final_cols = ['Place', 'Team_Short', 'Team', 'Games', 'Points', 'Wins', 'Loses', 'Pts_Scored', 'Pts_Lost', 'Pts_Diff']
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
            matches = re.findall(r'(\d+:\d+)', val)
            if len(matches) >= 2:
                return matches[-1]
            return None
        
        df['Result'] = df[col_score].apply(extract_score)

        # Divide into played and future games
        df_played = df[df['Result'].notna()].copy()
        df_future = df[df['Result'].isna()].copy()

        df_played[['Pts_Home', 'Pts_Away']] = df_played['Result'].str.split(':', expand=True).astype(int)

        def parse_teams(text):
            clean_text = text.split(" Emocje TV")[0]
            parts = clean_text.split(" - ")
            if len(parts) >= 2:
                return parts[0].strip(), parts[1].strip()
            return 'Unknown', 'Unknown'
        
        def parse_date(text):
            if not isinstance(text, str):
                return None
                  
            match = re.search(r'(\d{2}\.\d{2}\.\d{4})', text)
            if match:
                return match.group(1)
            return text
        
        df_played[['Home', 'Away']] = df_played[col_info].apply(lambda x: pd.Series(parse_teams(x)))
        df_played['Home_Short'] = df_played['Home'].apply(get_short_name)
        df_played['Away_Short'] = df_played['Away'].apply(get_short_name)

        df_future[['Home', 'Away']] = df_future[col_info].apply(lambda x: pd.Series(parse_teams(x)))
        df_future['Date'] = df_future[col_score].apply(lambda x: parse_date(x) if pd.notna(parse_date(x)) else x)
        df_future['Home_Short'] = df_future['Home'].apply(get_short_name)
        df_future['Away_Short'] = df_future['Away'].apply(get_short_name)

        cols_played = ['Home', 'Home_Short', 'Away', 'Away_Short', 'Pts_Home', 'Pts_Away']
        cols_future = ['Date', 'Home', 'Home_Short', 'Away', 'Away_Short']

        df_future['Date'] = pd.to_datetime(df_future['Date'], format='%d.%m.%Y', errors='coerce')
        df_future = df_future.sort_values("Date")

        return df_played[cols_played], df_future[cols_future]
    
    except Exception as e:
        print(f"Schedule error: {e}")
        return pd.DataFrame, pd.DataFrame()