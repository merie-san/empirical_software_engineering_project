"""Collect repository metadata monthly from a starting day up to an end date"""

import os
import time
import requests
from datetime import date
from dateutil.relativedelta import relativedelta
import json
import argparse

MAX_LEN_PAGE = 100
REPO_SEARCH_URL = "https://api.github.com/search/repositories"


def repo_search(
    language: str,
    starting_date: date,
    ending_date: date,
    repos_per_month: int,
    token: str = "",
) -> None:
    """query the github API for repos in a given language monthly from a given date up to an end date"""

    # initialize github token
    if token == "":
        env_token = os.getenv("GITHUB_TOKEN")
        if env_token:
            token = env_token
        else:
            raise ValueError("No github token provided")

    # github does not display more than 1000 results
    if repos_per_month > 100:
        raise ValueError("repos per month cannot be higher than 100")

    # generate the necessary date objects
    date_list = []
    date_var = starting_date
    while date_var < ending_date:
        date_list.append(date_var)
        date_var = date_var + relativedelta(months=1)

    # headers do not change
    headers = {
        "Accept": "application/vnd.github.mercy-preview+json",
        "Authorization": f"Bearer {token}",
    }

    # build the queries
    queries = []
    for i in range(len(date_list) - 1):
        queries.append(
            f"language:{language.lower()} created:{date_list[i]}..{date_list[i + 1]} size:<10000"
        )

    # build the parameter dicts
    param_list = [
        {
            "q": query,
            "sort": "stars",
            "order": "desc",
            "per_page": MAX_LEN_PAGE,
            "page": 0,
        }
        for query in queries
    ]

    responses = []

    # query github and collect requested results per month
    for param in param_list:
        n = 0
        i = 1

        # query multiple pages if necessary
        while n < repos_per_month:
            param["page"] = i
            response = requests.get(REPO_SEARCH_URL, params=param, headers=headers)

            # deal with rate limit
            if response.status_code == 403:
                reset_time = int(response.headers.get("X-RateLimit-Reset", time.time() + 60))
                sleep_time = max(reset_time - time.time(), 1)
                print(f"Rate limited. Sleeping {int(sleep_time)} seconds...")
                time.sleep(sleep_time)

            # get the repo items returned
            items = response.json().get("items", [])

            # if no item is returned then skip
            if not items:
                break

            # record metadata
            for item in items:
                responses.append(
                    {
                        "id": item.get("id"),
                        "name": item.get("name"),
                        "full_name": item.get("full_name"),
                        "html_url": item.get("html_url"),
                        "description": item.get("description"),
                        "language": item.get("language"),
                        "created_at": item.get("created_at"),
                        "updated_at": item.get("updated_at"),
                        "pushed_at": item.get("pushed_at"),
                        "stargazers_count": item.get("stargazers_count"),
                        "watchers_count": item.get("watchers_count"),
                        "forks_count": item.get("forks_count"),
                        "open_issues_count": item.get("open_issues_count"),
                        "topics": item.get("topics", []),
                        "license": (
                            item.get("license", {}).get("key")
                            if item.get("license")
                            else None
                        ),
                        "owner_login": (
                            item["owner"]["login"] if item.get("owner") else None
                        ),
                        "owner_type": (
                            item["owner"]["type"] if item.get("owner") else None
                        ),
                        "visibility": item.get("visibility"),
                        "archived": item.get("archived"),
                        "disabled": item.get("disabled"),
                        "score": item.get("score"),
                        "has_issues": item.get("has_issues"),
                        "has_projects": item.get("has_projects"),
                        "has_wiki": item.get("has_wiki"),
                        "has_pages": item.get("has_pages"),
                        "has_downloads": item.get("has_downloads"),
                    }
                )
                print(f"appended repo {item.get("full_name")} created at {item.get("created_at")}")

                # break if number of repos per month has been reached
                n += 1
                if n >= repos_per_month:
                    break

            # break if reached the maximum number of github resuls
            i += 1
            if i > 10:
                break

    # write to json file
    with open("repo_metadata.json", "w") as f:
        json.dump(responses, f)

    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="mine_repos",
        description="Collect repository metadata monthly from a starting day up to an end date",
    )
    parser.add_argument("language")
    parser.add_argument("starting_date")
    parser.add_argument("-f","--finish", default=date.today().isoformat())
    parser.add_argument("-m","--monthly", default=100, type=int)
    parser.add_argument("-t", "--token")
    args = parser.parse_args()
    repo_search(
        args.language,
        date.fromisoformat(args.starting_date),
        date.fromisoformat(args.finish),
        args.monthly,
        token = args.token or ""
    )
