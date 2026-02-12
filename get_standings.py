import pandas as pd
import numpy as np
import requests

url = "https://1lm.pzkosz.pl/tabele.html"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

response = requests.get(url, headers=headers)

dfs = pd.read_html(response.text)

liga_table = dfs[0]

print(liga_table.head())

liga_table.to_csv("standings.csv", index=False)

