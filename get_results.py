import pandas as pd
import requests

url_schedule = "https://1lm.pzkosz.pl/terminarz-i-wyniki.html"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url_schedule, headers=headers)
tables = pd.read_html(response.text)

all_games = pd.concat(tables)

print("Dostępne kolumny:", all_games.columns)

print(all_games.head())

all_games.to_csv("results.csv", index=False)