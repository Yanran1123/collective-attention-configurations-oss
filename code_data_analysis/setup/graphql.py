import os
import datetime

import requests

headers = {"Authorization": "token " + os.environ.get("GITHUB_TOKEN", "YOUR_GITHUB_TOKEN")}

# GitHub personal access token: supply your own via the GITHUB_TOKEN environment variable
# (see README.md). Never hard-code tokens in this file.


# query is a string
# To create a string with multiple lines, use triple quotes
def run_query(query):
    request = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))


# query is a string; variables is a dictionary
def run_query_variable(query, variables):
    request = requests.post('https://api.github.com/graphql', json={'query': query, 'variables': variables}, headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))


def get_remaining():
    query = """
    query {
      rateLimit{
        remaining
      }
    }
    """
    result = run_query(query)
    return result["data"]["rateLimit"]["remaining"]


def get_reset():
    query = """
    query {
      rateLimit{
        resetAt
      }
    }
    """
    result = run_query(query)
    return result["data"]["rateLimit"]["resetAt"]


def sleep_in_seconds(resetAt):
    """
    The function is to get how many minutes the program need to sleep to reset the 5000 scores
    :param resetAt: The UTC time of resetAt returned by GitHub GraphQL API
    :return: Seconds between the resetAt and the current time as well as a 5-second buffer
    """
    now = datetime.datetime.utcnow()
    reset = datetime.datetime.strptime(resetAt, "%Y-%m-%dT%H:%M:%SZ")
    delta = reset - now
    sleep = delta.days*24*60*60 + delta.seconds + 180
    return sleep

