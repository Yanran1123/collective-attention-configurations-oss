import calendar
import time

from setup.graphql import run_query_variable


# Search repositories in a certain topic
# Return a list of repositories with information on their owners and names
# topic is also a string
# end_date: string in the format of YYYY-MM-DD
def fetch_repo_list(topic, end_date):
    repos = []

    delimiter = "-"
    end_year = int(end_date.split(delimiter)[0])
    end_month = int(end_date.split(delimiter)[1])

    base_query = "is:public is:root topic:{} created:".format(topic)

    # GitHub starts at 2008
    year = 2008

    # How many repos each page; we cannot have more than 100 items per page from connections of GitHub GraphQL API
    first = 10

    while year <= end_year:
        search_query = search_query_year(base_query, year)
        if repo_count(search_query) < 1000 - first:
            repos.extend(search_repo(first, search_query))
        else:
            if year != end_year:
                month = 1
                while month <= 12:
                    search_query = search_query_month(base_query, year, month)
                    if repo_count(search_query) < 1000 - first:
                        repos.extend(search_repo(first, search_query))
                    else:
                        if month == 1 or month == 3 or month == 5 or month == 7 or month == 8 or month == 10 \
                                or month == 12:
                            day = 1
                            while day <= 31:
                                search_query = search_query_day(base_query, year, month, day)
                                repos.extend(search_repo(first, search_query))
                                # print("Year {} Month {} Day {} finished with total repos: {}".format(
                                #     str(year), str(month), str(day), str(len(repos))))
                                day = day + 1
                        elif month == 4 or month == 6 or month == 9 or month == 11:
                            day = 1
                            while day <= 30:
                                search_query = search_query_day(base_query, year, month, day)
                                repos.extend(search_repo(first, search_query))
                                # print("Year {} Month {} Day {} finished with total repos: {}".format(
                                #     str(year), str(month), str(day), str(len(repos))))
                                day = day + 1
                        else:
                            if calendar.isleap(year):
                                day = 1
                                while day <= 29:
                                    search_query = search_query_day(base_query, year, month, day)
                                    repos.extend(first, search_repo(search_query))
                                    # print("Year {} Month {} Day {} finished with total repos: {}".format(
                                    #     str(year), str(month), str(day), str(len(repos))))
                                    day = day + 1
                            else:
                                day = 1
                                while day <= 28:
                                    search_query = search_query_day(base_query, year, month, day)
                                    repos.extend(first, search_repo(search_query))
                                    # print("Year {} Month {} Day {} finished with total repos: {}".format(
                                    #     str(year), str(month), str(day), str(len(repos))))
                                    day = day + 1
                    # print("Year {} Month {} finished with total repos: {}".format(
                    #     str(year), str(month), str(len(repos))))
                    month = month + 1
            else:
                month = 1
                while month <= end_month:
                    search_query = search_query_month(base_query, year, month)
                    if repo_count(search_query) < 1000 - first:
                        repos.extend(search_repo(first, search_query))
                    else:
                        if month == 1 or month == 3 or month == 5 or month == 7 or month == 8 or month == 10 \
                                or month == 12:
                            day = 1
                            while day <= 31:
                                search_query = search_query_day(base_query, year, month, day)
                                repos.extend(search_repo(first, search_query))
                                # print("Year {} Month {} Day {} finished with total repos: {}".format(
                                #     str(year), str(month), str(day), str(len(repos))))
                                day = day + 1
                        elif month == 4 or month == 6 or month == 9 or month == 11:
                            day = 1
                            while day <= 30:
                                search_query = search_query_day(base_query, year, month, day)
                                repos.extend(search_repo(first, search_query))
                                # print("Year {} Month {} Day {} finished with total repos: {}".format(
                                #     str(year), str(month), str(day), str(len(repos))))
                                day = day + 1
                        else:
                            if calendar.isleap(year):
                                day = 1
                                while day <= 29:
                                    search_query = search_query_day(base_query, year, month, day)
                                    repos.extend(search_repo(first, search_query))
                                    # print("Year {} Month {} Day {} finished with total repos: {}".format(
                                    #     str(year), str(month), str(day), str(len(repos))))
                                    day = day + 1
                            else:
                                day = 1
                                while day <= 28:
                                    search_query = search_query_day(base_query, year, month, day)
                                    repos.extend(search_repo(first, search_query))
                                    # print("Year {} Month {} Day {} finished with total repos: {}".format(
                                    #     str(year), str(month), str(day), str(len(repos))))
                                    day = day + 1
                    # print("Year {} Month {} finished with total repos: {}".format(
                    #     str(year), str(month), str(len(repos))))
                    month = month + 1
        # print("Year {} finished with total repos: {}".format(str(year), str(len(repos))))
        year = year + 1

    return repos


def search_query_year(base_query, year):
    search_query = base_query + "{}..{}".format(str(year), str(year))
    return search_query


def search_query_month(base_query, year, month):
    if month < 10:
        search_query = base_query + "{}-0{}..{}-0{}".format(
            str(year), str(month), str(year), str(month))
    else:
        search_query = base_query + "{}-{}..{}-{}".format(
            str(year), str(month), str(year), str(month))
    return search_query


def search_query_day(base_query, year, month, day):
    if month < 10:
        if day < 10:
            search_query = base_query + "{}-0{}-0{}..{}-0{}-0{}".format(
                str(year), str(month), str(day), str(year), str(month), str(day))
        else:
            search_query = base_query + "{}-0{}-{}..{}-0{}-{}".format(
                str(year), str(month), str(day), str(year), str(month), str(day))
    else:
        if day < 10:
            search_query = base_query + "{}-{}-0{}..{}-{}-0{}".format(
                str(year), str(month), str(day), str(year), str(month), str(day))
        else:
            search_query = base_query + "{}-{}-{}..{}-{}-{}".format(
                str(year), str(month), str(day), str(year), str(month), str(day))
    return search_query


def repo_count(search_query):
    query = """
    query($search_query: String!) {
      search(first:1, type:REPOSITORY, query:$search_query){
        repositoryCount
      }
    }
    """
    variables = {
        "search_query": search_query
    }

    result = run_query_variable(query, variables)
    return result["data"]["search"]["repositoryCount"]


def search_repo(first, search_query):
    repos = []
    # Get 2 pieces of basic information about the list
    # 1. repositoryCount
    # 2. first_cursor: cursor of the first element in the list
    query = """
    query($search_query: String!) {
      rateLimit{
        remaining
      }
      search(first:1, type:REPOSITORY, query:$search_query){
        repositoryCount
        pageInfo{
          endCursor
          hasNextPage
        }
        edges{
          node{
            ... on Repository{
              owner{
                login
              }
              name
            }
          }
        }
      } 
    }
    """
    variables = {
        "search_query": search_query
    }

    result = run_query_variable(query, variables)
    repository_count = result["data"]["search"]["repositoryCount"]

    if repository_count == 0:
        return list(repos)
    else:
        first_cursor = result["data"]["search"]["pageInfo"]["endCursor"]
        remaining = result["data"]["rateLimit"]["remaining"]

        # Store information about the first repo in the topic list
        repo = [result["data"]["search"]["edges"][0]["node"]["owner"]["login"],
                result["data"]["search"]["edges"][0]["node"]["name"]]
        repos.append(repo)

        # Traverse the repo list after the first repo
        after_cursor = first_cursor
        has_next_page = result["data"]["search"]["pageInfo"]["hasNextPage"]
        count = len(repos)
        first = first
        while has_next_page:
            if remaining >= 1:
                if count+first < repository_count:
                    fragment = search_repo_page_fragment(first, after_cursor, search_query)
                    repos.extend(fragment[3:])
                    count = len(repos)
                    remaining = fragment[0]
                    after_cursor = fragment[1]
                    has_next_page = fragment[2]
                else:
                    fragment = search_repo_page_fragment(repository_count-count, after_cursor, search_query)
                    repos.extend(fragment[3:])
                    count = len(repos)
                    remaining = fragment[0]
                    after_cursor = fragment[1]
                    has_next_page = fragment[2]
            else:
                time.sleep(3610)

        return list(repos)


def search_repo_page_fragment(first, after_cursor, search_query):
    # Create list to store the fragment of repo list
    # fragment[0], fragment[1], and fragment[2] store the cost, remaining, and resetAt of rateLimit
    # fragment[3] stores the endCursor
    fragment = []

    # Construct GraphQL query language with variables
    query = """
    query($first: Int!, $after_cursor: String!, $search_query: String!) {
      rateLimit{
        cost
        remaining
        resetAt
      }
      search(first:$first, after:$after_cursor, type:REPOSITORY, query:$search_query){
        pageInfo{
          endCursor
          hasNextPage
        }
        edges{
          node{
            ... on Repository{
              owner{
                login
              }
              name
            }
              
          }
        }
      }
       
    }
    """
    variables = {
        "first": first,
        "after_cursor": after_cursor,
        "search_query": search_query
    }

    # Fetch data from GitHub based on the argument of query and variables
    result = run_query_variable(query, variables)

    # fragment[0] store the remaining of rateLimit
    fragment.append(result["data"]["rateLimit"]["remaining"])

    # fragment[1] store the endCursor
    # fragment[2] store the hasNextPage
    fragment.append(result["data"]["search"]["pageInfo"]["endCursor"])
    fragment.append(result["data"]["search"]["pageInfo"]["hasNextPage"])

    # Append repo information to the fragment list
    for i in result["data"]["search"]["edges"]:
        repo = [i["node"]["owner"]["login"], i["node"]["name"]]
        fragment.append(repo)

    return list(fragment)


# Merge the guest set into the host set so that there are no duplicate repos
def combine_two_repo_sets(host, guest):
    print("todo function")
