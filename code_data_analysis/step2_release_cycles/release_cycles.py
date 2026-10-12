"""
Step 2a. Slice each project's history into release cycles. A cycle starts at the previous release
(or the project's creation date) and ends at the focal release; days = length of the cycle.
"""

import json
from classes.analysis.innovativeaction import InnovativeAction
from classes.analysis.repobyreleasecycle import RepoByReleaseCycle
from classes.github.repocollection.repo import Repo
from classes.releasecycle.release_cycle import ReleaseCycle


# Repos that cannot be found in GitHub anymore
path_repo_notFound = "logs/repo_notFound.txt"


# Skipped repo-releases in which the earliest commit comes after the release endTime
path_repo_sliceByReleaseCycle_issue = "logs/repo_sliceByReleaseCycle_issue.txt"


# Step 2a. Slice the time period of OSS development by release cycle
def slice_repo_byReleaseCycle():
    """
    From the time when the repos is created to the time when the last release is published
    1. Skipped repos that cannot be found any more in GitHub
    2. Skipped releases that are published before the committedDate of the first default-branch commit
        Note that the startCommitOid of the first occurred commit is None, and the start time is the endTime of
            the last release, e.g., search repository "HIT-SCIR/ltp" in repoByReleaseCycle collection
    :return: Documents of repoByReleaseCycle are saved in db1_analysis_small
    """
    repos = Repo.objects().only("nameWithOwner", "releases", "createdAt")
    begin_index = 0
    len_repos = len(repos)
    repos_notFound = []
    # Remove repos that cannot be found anymore in GitHub
    with open(path_repo_notFound) as json_file:
        data = json.load(json_file)
        for repo in data:
            repos_notFound.append(repo["nameWithOwner"])
        json_file.close()
    # Save repoByReleaseCycle
    count = 0    # Record how manny repos are created after the first default-branch commit
    for i in range(begin_index, len_repos):
        repository = repos[i]["nameWithOwner"]
        if repository in repos_notFound:
            continue
        # Read and sort the releases of each repo
        releases = []
        for release in repos[i]["releases"]:
            # Only include releases that are not draft
            if not release["isDraft"]:
                if release["publishedAt"]:
                    releases.append(
                        {
                            "endTime": release["publishedAt"],
                            "isPrerelease": release["isPrerelease"],
                            "tagName": release["tagName"],
                            "name": release["name"],
                            "tagCommitOid": release["tagCommit"],
                            "author": release["author"],
                            "description": release["description"],
                            "createdAt": release["createdAt"],
                            "updatedAt": release["updatedAt"]
                        }
                    )
                else:  # If a release is not a draft, it should have been published
                    raise Exception("Repo {}'s release {} is not draft, but it is not published".format(
                        repository, release["tagName"])
                    )
        releases.sort(reverse=False, key=sort_by)
        # Initiate cycleNumber and startTime
        cycleNumber = 1
        startTime = repos[i]["createdAt"]
        # The createdAt time of a repo can be after the first default-branch commit
        startCommit = InnovativeAction.objects().filter(
            commitRepository=repository, isInDefaultBranch=True, committedDate__lte=startTime
        ).order_by('-committedDate').first()
        if not startCommit:
            startCommitOid = None
        else:
            startCommitOid = startCommit["oid"]
            count = count + 1
        # Create RepoByReleaseCycle documents for each repository
        for release in releases:
            print("Working on repo {}'s {}th release {}".format(repository, str(cycleNumber), release["tagName"]))
            endCommit = InnovativeAction.objects().filter(
                commitRepository=repository, isInDefaultBranch=True, committedDate__lte=release["endTime"]
            ).order_by('-committedDate').first()
            # Issue recording: the earliest commit comes after the release endTime
            if not endCommit:
                repo_release = {
                    "repository": repository,
                    "cycleNumber": cycleNumber,
                    "tagName": release["tagName"],
                    "tagCommitOid": release["tagCommitOid"],
                    "startTime": startTime.strftime("%Y-%m-%dT%H:%M:%S"),
                    "endTime": release["endTime"].strftime("%Y-%m-%dT%H:%M:%S")
                }
                file = open(path_repo_sliceByReleaseCycle_issue, "a")
                repo_release_text = json.dumps(repo_release, indent=4)
                file.write("\n" + repo_release_text + ",")
                file.close()
                cycleNumber = cycleNumber + 1
                startTime = release["endTime"]
                startCommitOid = None
                continue
            print("--> The endCommit of this release is with oid {}, committed on {} ".
                  format(endCommit["oid"], endCommit["committedDate"]))
            endCommitOid = endCommit["oid"]
            endTime = release["endTime"]
            days = (endTime - startTime).days
            print("--> The endTime of this release is {}, and the cycle includes {} days".format(endTime, str(days)))
            repoByReleaseCycle = RepoByReleaseCycle(
                repository=repository, isPrerelease=release["isPrerelease"],
                tagName=release["tagName"], name=release["name"], tagCommitOid=release["tagCommitOid"],
                author=release["author"], description=release["description"],
                createdAt=release["createdAt"], updatedAt=release["updatedAt"],
                cycleNumber=cycleNumber,
                startTime=startTime, endTime=endTime, days=days,
                startCommitOid=startCommitOid, endCommitOid=endCommitOid
            )
            repoByReleaseCycle.save()
            print("Release saved in repoByReleaseCycle collection.")
            print("-------------------------------------------------")
            cycleNumber = cycleNumber + 1
            startTime = release["endTime"]
            startCommitOid = endCommitOid

        print("repos[{}] is finished".format(str(i)))
        print("*******************************************************************")

    print("----- NOTE ---------------------------")
    print("{} repos are created after the first default-branch commit is made".format(str(count)))
    print("----- NOTE ---------------------------")

    return


# Child function of slice_repoByReleaseCYCLE()
def sort_by(e):
    return e["endTime"]


# ---------------------------
# Step 1 Construct the sample and get basic release cycle information
def get_basic_releaseCycleInfo():
    """
    Copy the release cycles in repoByReleaseCycle_2539 (18,630 release cycles) into the ReleaseCycle collection
    :return: Basic information of the release cycles saved in the ReleaseCycle collection -- MongoDB
    """
    begin = 0
    delta = 1000
    end = RepoByReleaseCycle.objects().count()
    while begin < end:
        # Set the block of repoByReleaseCycle that this iteration focuses on
        cursor = begin + delta
        if cursor > end:
            cursor = end
        # 1. Get the static properties from the sample of last stage: repoByReleaseCycle collection
        old_rls = RepoByReleaseCycle.objects[begin:cursor].only(
            "repository", "isPrerelease", "tagName", "name", "tagCommitOid",
            "author", "description", "createdAt", "updatedAt",
            "cycleNumber", "startTime", "endTime", "days",
            "startCommitOid", "endCommitOid"
        )
        # 2. Store the information in the ReleaseCycle collection
        for rl in old_rls:
            case = ReleaseCycle(
                repository=rl["repository"], isPrerelease=rl["isPrerelease"], tagName=rl["tagName"], name=rl["name"],
                tagCommitOid=rl["tagCommitOid"], author=rl["author"], description=rl["description"],
                createdAt=rl["createdAt"], updatedAt=rl["updatedAt"],
                cycleNumber=rl["cycleNumber"], startTime=rl["startTime"], endTime=rl["endTime"], days=rl["days"],
                startCommitOid=rl["startCommitOid"], endCommitOid=rl["endCommitOid"]
            )
            case.save()
        # Move to the next block
        begin = cursor

    sample_size = ReleaseCycle.objects().count()
    print("The newly constructed sample has {} cases.".format(str(sample_size)))

    return
