from github import Github, Auth
from datetime import date
from dateutil.relativedelta import relativedelta
import json
import sys


def mine_repos(client: Github, language: str, n_repo_month: int, starting_date: date, ending_date: date=date.today()):

    date_list = []
    date_var = starting_date
    while date_var < ending_date:
        date_list.append(date_var)
        date_var = date_var + relativedelta(months=1)
    repo_name_dict = {}
    for date_i in range(len(date_list) - 1):
        query_str = f"language:{language.lower()} created:{date.isoformat(date_list[date_i])}..{date.isoformat(date_list[date_i+1])}"
        repo_name_list = []
        results = client.search_repositories(query=query_str, sort="stars")
        i = 0
        for sampled_repo in results:
            if i >= n_repo_month:
                break
            repo_name_list.append(sampled_repo.full_name)
            i += 1

        repo_name_dict[date.isoformat(date_list[date_i])] = repo_name_list

    with open(f"repos_{language.lower()}.json", "w") as f:
        json.dump(repo_name_dict, f)


if __name__ == "__main__":

    # logout if no token is provided
    if len(sys.argv) < 2:
        print("No token provided")
        sys.exit()

    # login with the token
    auth = Auth.Token(sys.argv[1])
    g = Github(auth=auth)

    mine_repos(g, "python", 1, date.fromisoformat("2025-01-01"))
    with open("repos_python.json", "r") as f:
        print(json.load(f)) 
    
