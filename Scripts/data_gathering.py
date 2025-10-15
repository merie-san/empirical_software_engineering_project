import time
import os

import requests
import requests as req
from datetime import date
from dateutil.relativedelta import relativedelta
import json

# variables and constants
SEARCH_URL = 'https://api.github.com/search/repositories'
CODE_URL = 'https://api.github.com/search/code'

date_list = []
date_var = date.fromisoformat('2024-01-01')
while date_var < date.today():
    date_list.append(date_var)
    date_var = date_var + relativedelta(months=1)

sample_len = 5
queries = []

# github api request construction
for i in range(len(date_list) - 1):
    queries.append(f"language:python created:{date_list[i]}..{date_list[i + 1]} size:<10000")


params = [ {
    "q": query,
    "sort": "stars",    # sort by popularity
    "order": "desc",    # descrescent order
    "per_page": sample_len
} for query in  queries]

headers = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}"
}

filtered_response = []
for param in params:
    response = requests.get(SEARCH_URL, params=param, headers=headers)
    filtered_response.append(response.json().get('items', []))

with open("raw_data.json","w") as f:
    json.dump(filtered_response, f)

print("------------------------------------------------------------------------------------")