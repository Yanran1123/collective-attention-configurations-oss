import calendar
import datetime
import math
import time

from setup.graphql import run_query_variable, get_remaining, get_reset, sleep_in_seconds


# search a list of repositories with a time period condition
def fetch_repo_list_period(base_query, start_date, end_date):
    """
    :param base_query: conditions of search query except the time period part, e.g., "is:public is:root topic:ai"
    :param start_date: created from the start date in the format of "YYYY-MM-DD" --> Query: YYYY-MM-DDT00:00:00
    :param end_date: created before the end date in the format of "YYYY-MM-DD" --> Query: YYYY-MM-DDT00:00:00
    :return: repos: a list of repository objects
    """

    repos = []  # a list of repos to be returned
    first = 50  # 50 nodes per page; if we exhaust the API, we will have more issues

    start_obj = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end_obj = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    cursor_obj = end_obj    # Initiate the cursor_obj as end_obj

    total_delta = end_obj - start_obj
    """
    Note that this object has three attributes (read-only)
    days:           Between -999999999 and 999999999 inclusive
    seconds:        Between 0 and 86399 inclusive
    microseconds:   Between 0 and 999999 inclusive
    """

    # Slicing by 128 days, 64 days, then 32 days, then 16 days, then 8 day, then 4 days, then 2 days, then 1 day,
    # and finally slice_by_half_algorithm
    delta_days = 256     # Initiate the delta_seconds as the beginning state

    if total_delta.days <= 0:
        print("The end date is before the start date, or the end and start dates are the same.")
        print("Note that the function returns repos created before 00:00:00 of the end date.")
        return
    else:
        search_query = form_search_query(base_query=base_query, start_obj=start_obj, end_obj=end_obj)
        total_count = repo_count(search_query)
        print("The total number of repositories to be fetched this time is {}".format(str(total_count)))
        if total_count <= 1000:
            if get_remaining() > 15:
                repos.extend(search_repo_new(first, search_query))
            else:
                sleep = sleep_in_seconds(get_reset())
                print("Need to sleep about {} minutes to reset the 5000 scores".format(str(sleep / 60)))
                time.sleep(sleep)
                print("Restart! :-)")
                repos.extend(search_repo_new(first, search_query))
            print("The total number of searched repos is less than 1000.")
        else:
            rest_count = total_count
            cursor_obj = start_obj + datetime.timedelta(days=delta_days)

            while start_obj < end_obj:
                # Make sure that the cursor_obj does not exceed the end_obj
                while cursor_obj > end_obj and delta_days > 1:
                    delta_days = delta_days / 2
                    cursor_obj = start_obj + datetime.timedelta(days=delta_days)
                search_query = form_search_query(base_query=base_query, start_obj=start_obj, end_obj=cursor_obj)
                count = repo_count(search_query)
                # Try to shrink the slice by days while delta_days > 1
                while count > 1000 and delta_days > 1:
                    delta_days = delta_days / 2
                    cursor_obj = start_obj + datetime.timedelta(days=delta_days)
                    search_query = form_search_query(base_query=base_query, start_obj=start_obj, end_obj=cursor_obj)
                    count = repo_count(search_query)
                # If the slice by day exceeds the 1000 limit, use the slice-by_half_algorithm
                if delta_days <= 1 and count > 1000:
                    added_repos = slice_by_half_algorithm(base_query=base_query, first=first,
                                                          start_obj=start_obj, end_obj=cursor_obj)
                    repos.extend(added_repos)
                    rest_count = rest_count - len(added_repos)
                    start_obj = cursor_obj
                    cursor_obj = cursor_obj + datetime.timedelta(days=delta_days)
                else:
                    if get_remaining() > 15:
                        added_repos = search_repo_new(first, search_query)
                        repos.extend(added_repos)
                        rest_count = rest_count - len(added_repos)
                        start_obj = cursor_obj
                        cursor_obj = cursor_obj + datetime.timedelta(days=delta_days)
                    else:
                        sleep = sleep_in_seconds(get_reset())
                        print("Need to sleep about {} minutes to reset the 5000 scores".format(str(sleep / 60)))
                        time.sleep(sleep)
                        print("Restart! :-)")
                        added_repos = search_repo_new(first, search_query)
                        repos.extend(added_repos)
                        rest_count = rest_count - len(added_repos)
                        start_obj = cursor_obj
                        cursor_obj = cursor_obj + datetime.timedelta(days=delta_days)
                print("\nThe rest_count is {}".format(str(rest_count)))
                print("The start_obj now moves to {}".format(start_obj.strftime('%Y-%m-%dT%H:%M:%S')))

    return repos


# Use the method only when the slice of repos created by a day exceeds 1000
def slice_by_half_algorithm(base_query, first, start_obj, end_obj):
    repos = []

    search_query = form_search_query(base_query=base_query, start_obj=start_obj, end_obj=end_obj)

    total_count = repo_count(search_query)
    print("--------------------------------------------------------------------------")
    print("The number of daily created repos to be traversed by this slice_by_half_algorithm is {}".
          format(str(total_count)))

    if total_count <= 1000:
        if get_remaining() > 15:
            repos.extend(search_repo_new(first, search_query))
        else:
            sleep = sleep_in_seconds(get_reset())
            print("Need to sleep about {} minutes to reset the 5000 scores".format(str(sleep / 60)))
            time.sleep(sleep)
            print("Restart! :-)")
            repos.extend(search_repo_new(first, search_query))
        print("The total number of searched repos is less than 1000.")
    else:
        rest_count = total_count
        cursor_obj = end_obj
        while start_obj != end_obj:
            if rest_count > 1000:
                cursor_obj = shrink(start_obj=start_obj, end_obj=cursor_obj, base_query=base_query)
            search_query = form_search_query(base_query=base_query, start_obj=start_obj, end_obj=cursor_obj)
            if get_remaining() > 15:
                added_repos = search_repo_new(first=first, search_query=search_query)
                repos.extend(added_repos)
                rest_count = rest_count - len(added_repos)
                start_obj = cursor_obj
                cursor_obj = end_obj
            else:
                sleep = sleep_in_seconds(get_reset())
                print("Need to sleep about {} minutes to reset the 5000 scores".format(str(sleep / 60)))
                time.sleep(sleep)
                print("Restart! :-)")
                added_repos = search_repo_new(first=first, search_query=search_query)
                repos.extend(added_repos)
                rest_count = rest_count - len(added_repos)
                start_obj = cursor_obj
                cursor_obj = end_obj
            print("The rest_count of this slice by day is {}".format(str(rest_count)))
            print("The start_obj now moves to {}".format(start_obj.strftime('%Y-%m-%dT%H:%M:%S')))
    print("--------------------------------------------------------------------------")
    return repos


def shrink(start_obj, end_obj, base_query):
    delta = end_obj - start_obj
    delta_seconds = delta.days * 24 * 60 * 60 + delta.seconds
    delta_seconds = int(delta_seconds / 2)
    cursor_obj = start_obj + datetime.timedelta(seconds=delta_seconds)

    if cursor_obj == start_obj:
        return end_obj, end_obj.strftime('%Y-%m-%dT%H:%M:%S')

    search_query = form_search_query(base_query=base_query, start_obj=start_obj, end_obj=cursor_obj)

    count = repo_count(search_query)
    while count > 1000:
        delta_seconds = delta_seconds / 2
        cursor_obj = start_obj + datetime.timedelta(seconds=delta_seconds)
        search_query = form_search_query(base_query=base_query, start_obj=start_obj, end_obj=cursor_obj)
        if get_remaining() > 15:
            count = repo_count(search_query)
        else:
            sleep = sleep_in_seconds(get_reset())
            print("Need to sleep about {} minutes to reset the 5000 scores".format(str(sleep / 60)))
            time.sleep(sleep)
            print("Restart! :-)")
            count = repo_count(search_query)

    return cursor_obj


def form_search_query(base_query, start_obj, end_obj):
    start_utc = start_obj.strftime('%Y-%m-%dT%H:%M:%S')
    end_utc = end_obj.strftime('%Y-%m-%dT%H:%M:%S')
    search_query = base_query + " created:{}..{}".format(start_utc, end_utc)
    return search_query


# Estimated cost 1
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

    if get_remaining() > 15:
        result = run_query_variable(query, variables)
    else:
        sleep = sleep_in_seconds(get_reset())
        print("Need to sleep about {} minutes to reset the 5000 scores".format(str(sleep / 60)))
        time.sleep(sleep)
        print("Restart! :-)")
        result = run_query_variable(query, variables)

    return result["data"]["search"]["repositoryCount"]


# Estimated cost 10 (if 100, it means 1000 repos)
def search_repo_new(first, search_query):
    repos = []
    # Get 2 pieces of basic information about the list
    # 1. repositoryCount
    # 2. first_cursor: cursor of the first element in the list
    query = """
    query($first: Int!, $search_query: String!) {
      rateLimit{
        remaining
      }
      search(first:$first, type:REPOSITORY, query:$search_query){
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
              createdAt
              languages{
                totalSize
              }
              releases{
                totalCount
              }
            }
          }
        }
      } 
    }
    """
    variables = {
        "search_query": search_query,
        "first": first
    }

    result = run_query_variable(query, variables)
    repository_count = result["data"]["search"]["repositoryCount"]

    if repository_count == 0:
        return list(repos)
    else:
        end_cursor = result["data"]["search"]["pageInfo"]["endCursor"]
        remaining = result["data"]["rateLimit"]["remaining"]

        # Store information about the first repo in the topic list
        for i in result["data"]["search"]["edges"]:
            repo = [i["node"]["owner"]["login"], i["node"]["name"], i["node"]["createdAt"],
                    i["node"]["languages"]["totalSize"], i["node"]["releases"]["totalCount"]]
            repos.append(repo)

        # Traverse the repo list after the first page of repos
        after_cursor = end_cursor
        has_next_page = result["data"]["search"]["pageInfo"]["hasNextPage"]
        count = len(repos)
        first = first
        while has_next_page:
            fragment = search_repo_page_fragment(first, after_cursor, search_query)
            repos.extend(fragment[3:])
            remaining = fragment[0]
            after_cursor = fragment[1]
            has_next_page = fragment[2]

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
              createdAt
              languages{
                totalSize
              }
              releases{
                totalCount
              }
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
        repo = [i["node"]["owner"]["login"], i["node"]["name"], i["node"]["createdAt"],
                i["node"]["languages"]["totalSize"], i["node"]["releases"]["totalCount"]]
        fragment.append(repo)

    return list(fragment)


# Merge the guest set into the host set so that there are no duplicate repos
def combine_two_repo_sets(host, guest):
    print("todo function")
