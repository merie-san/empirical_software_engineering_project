import time
import os
import requests as req

# variables and constants
SEARCH_URL = 'https://api.github.com/search/repositories'
CODE_URL = 'https://api.github.com/search/code'

sample_len = 10

# github api request construction
query = 'language:python topic:ai'

params = {
    "q": query,
    "sort": "stars",    # sort by popularity
    "order": "desc",    # descrescent order
    "per_page": sample_len
}

headers = {
    "Accept": "application/vnd.github+json",
    "Authorization": os.getenv('GITHUB_TOKEN')
}

response = req.get(SEARCH_URL, params=params, headers=headers)
filtered_response = response.json().get('items', [])
for repo in filtered_response:
    print(repo['full_name'] + " ----- " + repo['html_url'])

print("------------------------------------------------------------------------------------")

counter = 0

for repo in filtered_response:
    full_name = repo['full_name']
    c_query = f'"import OpenAI" repo:{full_name}'

    params = {
        "q": c_query,   # sort by popularity
        "order": "desc" # descrescent order
    }

    c_response = req.get(CODE_URL, params=params, headers=headers)

    print(c_response.json())