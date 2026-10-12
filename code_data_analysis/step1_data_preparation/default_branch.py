"""
Step 1b. Identify each repository's default-branch commits (InnovativeAction.isInDefaultBranch),
which are used to anchor release cycles to the codebase.
"""

import datetime
import json
import time
from classes.analysis.innovativeaction import InnovativeAction
from classes.analysis.repoinfo import RepoDescription
from classes.github.repocollection.repo import Repo
from setup.graphql import get_remaining
from setup.graphql import get_reset
from setup.graphql import run_query_variable
from setup.graphql import sleep_in_seconds
from step1_data_preparation.fetch_commits import fetch_repo_commit


# Read the most recent M commits in the MongoDB
M = 2000


# Fetch the most recent N default-branch commits until a time to identify the most recent default-branch commit
#   in MongoDB
N = 1000


cost = 2


first = 50


# Finally, I find repos that have no innovative actions either changed its owner name or cannot be found anymore
path_repo_noInnovativeActions = "logs/repo_no_innovative_actions.txt"


# Repos that cannot be found in GitHub anymore
path_repo_notFound = "logs/repo_notFound.txt"


# Step 1.a Find the most recent one that is in the master branch by the following steps,
# and store the information in repos_info collection
def identify_most_recent_defaultBranch_commit():
    repos = Repo.objects().only("owner", "name", "defaultBranch")
    len_repos = len(repos)  # 2539 is the length of repos
    begin_index = 0

    for i in range(begin_index, len_repos):
        # Find and sort commits of the repo by committedDate (descending)
        repository = repos[i]["owner"] + "/" + repos[i]["name"]
        print("Working on repo: {}".format(repository))
        branch = repos[i]["defaultBranch"]
        commits = InnovativeAction.objects(commitRepository=repository).order_by('-committedDate').limit(M).only(
            "oid", "committedDate"
        )
        # Continue if there are no commits in MongoDB
        if not commits:
            repo_noInnovativeActions = {
                "owner": repos[i]["owner"],
                "name": repos[i]["name"],
                "nameWithOwner": repository
            }
            file = open(path_repo_noInnovativeActions, "a")
            repo_noInnovativeActions_text = json.dumps(repo_noInnovativeActions, indent=4)
            file.write("\n" + repo_noInnovativeActions_text + ",")
            file.close()
            continue
        # Identify the most recent N default-branch commits until the most recent commit in db1_analysis_small
        until = commits[0]["committedDate"]
        until = until + datetime.timedelta(seconds=1)
        defaultBranch_oids = fetch_defaultBranch_commits(owner=repos[i]["owner"], name=repos[i]["name"], until=until)
        # Continue if the repo cannot be found any more
        if not defaultBranch_oids:
            continue
        # Check whether a commit is in the default branch one by one and identify the most recent default-branch commit
        len_commits = len(commits)
        oid = None
        for j in range(0, len_commits):
            if commits[j]["oid"] in defaultBranch_oids:
                # Save the information of identified commit at the repos_info collection in db1_analysis_small
                oid = commits[j]["oid"]
                print("The commits[{}] with oid {} is the most recent default-branch commit of repo {} in the MongoDB".
                      format(str(j), oid, repository))
                print("repos[{}] is finished".format(str(i)))
                print("*************************************************")
                num_updated = RepoDescription.objects(nameWithOwner=repository).update(
                    set__defaultBranch=branch, set__defaultBranchCommitOid=oid
                )
                if num_updated != 1:
                    raise Exception("Debug!")
                break
        if not oid:
            raise Exception("Cannot identify the most recent default-branch commit in MongoDB of repo {}".
                            format(repository))

    return


# Affiliated function of identify_most_recent_defaultBranch_commit()
# Address exception -- OAID/Tengine (default branch changed after data collection)
def repair_find_most_recent_defaultBranchCommit():
    """
    Repair the repos that are missed in identify_most_recent_defaultBranch_commit()
    1. OAID/Tengine  -- Cannot use GraphQL to get the commits in default branch
        step 1: get a default-branch oid by Merged events, oid: "9f963f1db81b54ff59c3f980b240d275e1e1f12c"
        step 2: Compare with commits in MongoDB
    2. platformio/platform-riscv_gap  -- The owner name is not updated from "pioplus" to "platformio"
        step 1: get a default-branch oid by query the defaultBranch, oid: "a8e57452b0732e0e2b484f988c491bf42ea90f43";
                this commit is committed on "2020-08-04T10:59:10Z"
        step 2: compare with commits in MongoDB
    3. jackzhenguo/python-small-examples  -- No idea why it is not fetched
        step 1: get a default-branch oid by Merged events, oid: "7c1a9ae9727f70c3ba965d805de562f58fe43df9"
        step 2: Compare with commits in MongoDB
    :return: the most recent defaultCommit of a such repo is identified and saved in repos_info collection

    Other 11 missed repos cannot be repaired because they cannot be found in GitHub anymore, see file
    logs/repo_notFound.txt
    """
    # Check the Merged events and find the default-branch commits by tracing the history of mergeRefCommit
    owner = "jackzhenguo"
    name = "python-small-examples"
    repository = owner + "/" + name
    oid = "7c1a9ae9727f70c3ba965d805de562f58fe43df9"
    defaultBranch_oids = []
    query_history = """
    query ($owner: String!, $name: String!, $first: Int!, $oid: GitObjectID!, $after_cursor: String) { 
      repository(owner: $owner, name: $name){
        createdAt
        object(oid: $oid){
          ... on Commit{
            oid
            history(first: $first, after: $after_cursor){
              totalCount
              pageInfo{
                hasNextPage
                endCursor
              }
              nodes{
                oid
                committedDate
                authoredDate
              }
            }
          }
        }
      }
    }
    """
    variables_history_firstPage = {
        "owner": owner,
        "name": name,
        "first": first,
        "oid": oid
    }
    if get_remaining() < cost:
        sleep = sleep_in_seconds(get_reset())
        print("Need to sleep about {} minutes to reset the 5000 scores".format(str(sleep / 60)))
        time.sleep(sleep)
        print("Restart! :-)")
    result = run_query_variable(query_history, variables_history_firstPage)
    for node in result["data"]["repository"]["object"]["history"]["nodes"]:
        defaultBranch_oids.append(node["oid"])
    after_cursor = result["data"]["repository"]["object"]["history"]["pageInfo"]["endCursor"]
    hasNextPage = result["data"]["repository"]["object"]["history"]["pageInfo"]["hasNextPage"]
    variables_history_nextPage = {
        "owner": owner,
        "name": name,
        "first": first,
        "oid": oid,
        "after_cursor": after_cursor
    }
    while hasNextPage:
        if get_remaining() < cost:
            sleep = sleep_in_seconds(get_reset())
            print("Need to sleep about {} minutes to reset the 5000 scores".format(str(sleep / 60)))
            time.sleep(sleep)
            print("Restart! :-)")
        result = run_query_variable(query_history, variables_history_nextPage)
        for node in result["data"]["repository"]["object"]["history"]["nodes"]:
            defaultBranch_oids.append(node["oid"])
        after_cursor = result["data"]["repository"]["object"]["history"]["pageInfo"]["endCursor"]
        hasNextPage = result["data"]["repository"]["object"]["history"]["pageInfo"]["hasNextPage"]
        variables_history_nextPage["after_cursor"] = after_cursor
    # Compare with commits in MongoDB
    commits = InnovativeAction.objects(commitRepository=repository).order_by('-committedDate').limit(M).only("oid")
    len_commits = len(commits)
    oid = None
    for j in range(0, len_commits):
        if commits[j]["oid"] in defaultBranch_oids:
            # Save the information of identified commit at the repos_info collection in db1_analysis_small
            oid = commits[j]["oid"]
            print("The commits[{}] with oid {} is the most recent default-branch commit of repo {} in the MongoDB".
                  format(str(j), oid, repository))
            print("*************************************************")
            repos = Repo.objects(nameWithOwner=repository).only("defaultBranch")
            if len(repos) != 1:
                raise Exception("There should be only one repository with {}".format(repository))
            branch = repos[0]["defaultBranch"]
            num_updated = RepoDescription.objects(nameWithOwner=repository).update(
                set__defaultBranch=branch, set__defaultBranchCommitOid=oid
            )
            if num_updated != 1:
                raise Exception("Debug!")
            break
    if not oid:
        raise Exception("Cannot identify the most recent default-branch commit in MongoDB of repo {}".
                        format(repository))
    return


# Child function of identify_defaultBranchCommits()
def fetch_defaultBranch_commits(owner, name, until):
    count = 0
    oids = []  # Store most recent N oids in the default branch until the "until" time

    until = until.strftime('%Y-%m-%dT%H:%M:%S')
    query_defaultBranch_commits = """
    query defaultBranch_commits($owner: String!, $name: String!, $first: Int!, $until: GitTimestamp, $after_cursor: String) {
      repository(owner: $owner, name: $name){
        defaultBranchRef{
          target{
            ... on Commit{
              history(first:$first, until:$until, after:$after_cursor){
                totalCount
                pageInfo{
                  hasNextPage
                  endCursor
                }
                nodes{
                  oid
                  committedDate
                  authoredDate
                }
              }
            }
          }
        }
      }
    }
    """
    variables_defaultBranch_commits_firstPage = {
        "owner": owner,
        "name": name,
        "first": first
    }
    if until:
        variables_defaultBranch_commits_firstPage["until"] = until
    if get_remaining() < cost:
        sleep = sleep_in_seconds(get_reset())
        print("Need to sleep about {} minutes to reset the 5000 scores".format(str(sleep / 60)))
        time.sleep(sleep)
        print("Restart! :-)")
    result = run_query_variable(query_defaultBranch_commits, variables_defaultBranch_commits_firstPage)
    # Directly return if the repo cannot be found anymore
    if not result["data"]["repository"]:
        repo_notFound = {
            "owner": owner,
            "name": name,
            "nameWithOwner": owner + "/" + name
        }
        file = open(path_repo_notFound, "a")
        repo_notFound_text = json.dumps(repo_notFound, indent=4)
        file.write("\n" + repo_notFound_text + ",")
        file.close()
        return
    for node in result["data"]["repository"]["defaultBranchRef"]["target"]["history"]["nodes"]:
        oids.append(node["oid"])
        count = count + 1
    after_cursor = result["data"]["repository"]["defaultBranchRef"]["target"]["history"]["pageInfo"]["endCursor"]
    hasNextPage = result["data"]["repository"]["defaultBranchRef"]["target"]["history"]["pageInfo"]["hasNextPage"]
    variables_defaultBranch_commits_nextPage = {
        "owner": owner,
        "name": name,
        "first": first,
        "after_cursor": after_cursor
    }
    if until:
        variables_defaultBranch_commits_nextPage["until"] = until
    while count < N and hasNextPage:
        if get_remaining() < cost:
            sleep = sleep_in_seconds(get_reset())
            print("Need to sleep about {} minutes to reset the 5000 scores".format(str(sleep / 60)))
            time.sleep(sleep)
            print("Restart! :-)")
        result = run_query_variable(query_defaultBranch_commits, variables_defaultBranch_commits_nextPage)
        for node in result["data"]["repository"]["defaultBranchRef"]["target"]["history"]["nodes"]:
            oids.append(node["oid"])
            count = count + 1
        after_cursor = result["data"]["repository"]["defaultBranchRef"]["target"]["history"]["pageInfo"]["endCursor"]
        hasNextPage = result["data"]["repository"]["defaultBranchRef"]["target"]["history"]["pageInfo"]["hasNextPage"]
        variables_defaultBranch_commits_nextPage["after_cursor"] = after_cursor
    print("{} commits in the default branch until {} is fetched, and is to be compared with commits in MongoDB".
          format(str(count), until))
    return list(oids)


# Step 1.b Trace all other innovative actions in this branch by the parents of each commit, and store the information
# of isInDefaultBranch in innovative_actions collection
def mark_all_defaultBranch_commits():
    # Find all the commits in the default branch, and store the information in innovative_action
    repos = RepoDescription.objects().only("nameWithOwner", "defaultBranchCommitOid")
    len_repos = len(repos)
    begin_index = 0
    for i in range(begin_index, len_repos):
        count = 0
        repository = repos[i]["nameWithOwner"]
        print("Working on repos[{}]: {}".format(str(i), repository))
        # If the repo does not have defaultBranchCommitOid, skip it
        if not repos[i]["defaultBranchCommitOid"]:
            continue
        # Else, work on the ones that have defaultBranchCommitOid
        bag = []
        oid = repos[i]["defaultBranchCommitOid"]
        bag.append(oid)
        parentOids = trace_parents(commitRepository=repository, oid=oid)
        # Keep collecting parents that are not duplicated
        while parentOids:
            # Add the parent to the bag
            for oid in parentOids:
                bag.append(oid)
            grandparentOids = []
            # Trace all the grandparents, and remove the duplicates
            for oid in parentOids:
                oids = trace_parents(commitRepository=repository, oid=oid)
                for p_oid in oids:
                    grandparentOids.append(p_oid)
            grandparentOids = list(dict.fromkeys(grandparentOids))
            # If a oid of the grandparents is not in the bag, go to the next iteration
            parentOids = []
            for oid in grandparentOids:
                if oid not in bag:
                    parentOids.append(oid)
        # Mark the collected default-branch commits as in default branch
        for oid in bag:
            mark_isInDefaultBranch(commitRepository=repository, oid=oid)
            count = count + 1
        print("{} default-branch commits are marked.".format(str(count)))
        print("***************************************************")
    return


# Child function of mark_all_defaultBranch_commits()
def trace_parents(commitRepository, oid):
    actions = InnovativeAction.objects(commitRepository=commitRepository, oid=oid).only("parents")
    if len(actions) > 1:
        raise Exception("Debug! There are multiple innovative actions with oid: {}, and commitRepository: {}".
                        format(oid, commitRepository))
    if len(actions) == 0:
        fetch_repo_commit(repository=commitRepository, commitOid=oid)
    actions = InnovativeAction.objects(commitRepository=commitRepository, oid=oid).only("parents")
    if len(actions) != 1:
        raise Exception("Debug!!")
    parents = actions[0]["parents"]
    parents_oid = []
    for parent in parents:
        parents_oid.append(parent["oid"])
    return list(parents_oid)


# Child function of mark_all_defaultBranch_commits()
def mark_isInDefaultBranch(commitRepository, oid):
    num_updated = InnovativeAction.objects(commitRepository=commitRepository, oid=oid). \
        update(set__isInDefaultBranch=True)
    if num_updated == 0:
        raise Exception("Cannot find this innovative action in MongoDB, with oid: {}, commitRepository: {}".
                        format(oid, commitRepository))
    if num_updated > 1:
        raise Exception("There are multiple innovative actions in MongoDB, with oid: {}, commitRepository: {}".
                        format(oid, commitRepository))
    return
