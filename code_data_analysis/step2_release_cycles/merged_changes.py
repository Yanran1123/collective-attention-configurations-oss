"""
Step 2b. Number of changed files, lines added, and lines deleted of each merge (Merged events), retrieved from
the GitHub compare page between the pull request's base commit and the merged commit. Step 3a uses these fields
(merges with no changed files are skipped), and the lines changed of each output determine hasNoChangeInfo (step 5a).
  calculate_novelty_mergedEvents('RepoByReleaseCycle'): merges within each release cycle (it also stores average
      changed files and lines per release cycle, which no variable in the paper uses)
  fetch_changedInfo_of_mergedEvents(): catch-up pass over all Merged events whose information is still missing
"""

import time
import urllib3
from bs4 import BeautifulSoup
from classes.analysis.repobyreleasecycle import RepoByReleaseCycle
from classes.github.event.output.merged import Merged
from classes.github.issuecollection.pullrequest import PullRequest


# Maximum number of tries when doing the web calling
maxTry = 50


sleep_between_tries = 10


# Step 5. (final novelty calculation)
# The finalized way of calculating the novelty: average files/lines changed in the codebase
def calculate_novelty_mergedEvents(repoFrame):
    if repoFrame == "RepoByReleaseCycle":
        repo_releases = RepoByReleaseCycle.objects().only(
            "id", "repository", "cycleNumber", "startTime", "endTime")
        begin_index = 0
        len_repoReleases = len(repo_releases)
        count_no_headCommit = 0

        total_merged_dealt = 0  # The number of Merged events whose changed information is collected

        for i in range(begin_index, len_repoReleases):
            mongo_id = repo_releases[i]["id"]
            repository = repo_releases[i]["repository"]
            startTime = repo_releases[i]["startTime"]
            endTime = repo_releases[i]["endTime"]
            print("Working on repo_releases[{}]: {}, cycleNumber {}".format(
                str(i), repository, repo_releases[i]["cycleNumber"]))
            mergedEvents = Merged.objects().filter(
                repository=repository, createdAt__gte=startTime, createdAt__lt=endTime
            ).only("id", "commitOid", "number", "changedFilesCount", "additions", "deletions")
            # Calculate the average changed files and average changed lines of the Merged events
            n = len(mergedEvents)
            totalChangedFiles = 0
            totalChangedLines = 0
            for m in mergedEvents:
                head_commit = m["commitOid"]
                prNumber = m["number"]
                pr = PullRequest.objects(repository=repository, number=prNumber).only("baseRefOid").first()
                base_commit = pr["baseRefOid"]
                # Ignore the Merged event whose associated commitOid is missing
                if not head_commit:
                    count_no_headCommit = count_no_headCommit + 1
                    n = n - 1  # remember to decrement the number of mergedEvents to be divided
                    print("--> Skipped a merge event")
                    continue
                if not base_commit:
                    raise Exception("!! The baseRefOid of pr #{} in repo {} is None".
                                    format(str(prNumber), repository))

                # deal with the circumstance where some information about some Merged events are collected
                changedFilesCount = m["changedFilesCount"]
                additions = m["additions"]
                deletions = m["deletions"]
                if not changedFilesCount:
                    changedFilesCount, additions, deletions = compare_commits_url(
                        repository=repository, base_commit=base_commit, head_commit=head_commit)

                # store the information in Merged collection
                num_updated = Merged.objects(id=m["id"]).update(
                    set__changedFilesCount=changedFilesCount, set__additions=additions, set__deletions=deletions)
                if num_updated != 1:
                    raise Exception("!! There should be only one Merged event with id: {}".format(m["id"]))

                totalChangedFiles = totalChangedFiles + changedFilesCount
                totalChangedLines = totalChangedLines + additions + deletions
            if n == 0:
                aveChangedFiles = 0
                aveChangedLines = 0
            else:
                aveChangedFiles = totalChangedFiles / n
                aveChangedLines = totalChangedLines / n
            # store the information about novelty
            num_updated = RepoByReleaseCycle.objects(id=mongo_id).update(
                set__novelty_aveChangedFiles=aveChangedFiles, set__novelty_aveChangedLines=aveChangedLines
            )
            if num_updated != 1:
                raise Exception("Debug the problem!")

            print("--> Dealt with {} Merged events".format(str(n)))
            total_merged_dealt = total_merged_dealt + n
            print("    Total dealt Merged events is {}".format(str(total_merged_dealt)))
            print("Finished repo_releases[{}]: {}, cycleNumber {}".format(
                str(i), repository, repo_releases[i]["cycleNumber"]))
            print("*************************************************")
        # Print the number of Merged events that have no associated commitOid
        print("-------- Note ----------------------")
        print("{} Merged events have no commitOid".format(str(count_no_headCommit)))
        print("------------------------------------")
    elif repoFrame == "RepoByMonth":
        # todo complete this part; note that we need to weight the initial and last month
        print("To do")
    else:
        raise Exception("{} is an unknown repository frame.".format(repoFrame))

    return


# Child function of calculate_novelty_by_releaseCycle_defaultBranch(repo_release) and
#   calculate_novelty_mergedEvents(repoFrame)
def compare_commits_url(repository, base_commit, head_commit):
    # Construct the url and call the webpage by using urllib3
    http = urllib3.PoolManager()
    url = "https://github.com/" + repository + "/compare/" + base_commit + "..." + head_commit
    print("--> Fetching {}".format(url))
    response = http.request('GET', url)
    tried = 1
    while response.status != 200:
        response = http.request('GET', url)
        tried = tried + 1
        time.sleep(sleep_between_tries)
        if tried > maxTry:
            return "Exception", "Exception", "Exception"
            # raise Exception("!! Cannot fetch the web {} after {} times try".format(url, str(maxTry)))
    # Convert the content to structured data
    soup = BeautifulSoup(response.data)
    # pprint(soup)
    # Identify the field that shows data on information about the number of changed files,
    # # lines of additions and deletions
    content = soup.find_all(class_="toc-diff-stats")
    while not content:
        response = http.request('GET', url)
        soup = BeautifulSoup(response.data)
        content = soup.find_all(class_="toc-diff-stats")
        tried = tried + 1
        time.sleep(sleep_between_tries)
        if tried > maxTry:
            changedFilesCount = "Exception"
            additions = "Exception"
            deletions = "Exception"
            return changedFilesCount, additions, deletions
            # raise Exception("!! Tried {} times. No class 'toc-diff-stats' when calling {}".format(str(maxTry), url))
    # print(content[0].parent.text)
    # Get the specific information one the number of files that are changed and how much each file is changed
    text = content[0].parent.text
    x = [s for s in text.split()]
    for i in range(0, len(x)):
        if 'changed' in x[i]:
            break
    if i == len(x):
        raise Exception("!! Cannot find 'changed' in the fetched content")
    changedFilesCount = convert_str_to_int(x[i-1])
    for i in range(0, len(x)):
        if 'addition' in x[i]:
            break
    if i == len(x):
        raise Exception("!! Cannot find 'additions' in the fetched content")
    additions = convert_str_to_int(x[i-1])
    for i in range(0, len(x)):
        if 'deletion' in x[i]:
            break
    if i == len(x):
        raise Exception("!! Cannot find 'deletions' in the fetched content")
    deletions = convert_str_to_int(x[i-1])
    # # An old way of identifying the diff information
    # content = soup.find_all(class_="octicon octicon-file-diff")
    # print(content[0].parent.text)
    # # Get the specific information one the number of files that are changed and how much each file is changed
    # text = content[0].parent.text
    # x = [s for s in text.split() if s.isdigit()]
    # changedFilesCount = x[0]
    # additions = x[1]
    # deletions = x[2]
    return changedFilesCount, additions, deletions


# Child function of compare_commits_url(repository, base_commit, head_commit)
def convert_str_to_int(num_string):
    """
    Convert the string number written in, for example, 999,999,999 to a Int
    :param num_string: The str of a number delimited by ',' character
    :return: the int version of the number
    """
    numbers = num_string.split(',')
    x = ''
    for num in numbers:
        x = x + num
    x = int(x)
    return x


def fetch_changedInfo_of_mergedEvents():
    mergedEvents = Merged.objects().only("id", "commitOid", "repository", "number",
                                         "changedFilesCount", "additions", "deletions",
                                         "changedFilesCount", "additions", "deletions")
    # Calculate the average changed files and average changed lines of the Merged events
    n = len(mergedEvents)

    for m in mergedEvents:
        m_id = m["id"]
        head_commit = m["commitOid"]
        repository = m["repository"]
        prNumber = m["number"]
        pr = PullRequest.objects(repository=repository, number=prNumber).only("baseRefOid").first()
        if not pr:
            raise Exception("Pr #{} in repo {} cannot be found!".format(str(prNumber), repository))
        base_commit = pr["baseRefOid"]
        # Ignore the Merged event whose associated commitOid is missing
        if not head_commit:
            n = n - 1  # remember to decrement the number of mergedEvents to be divided
            print("--> Skipped a merge event")
            continue
        if not base_commit:
            raise Exception("!! The baseRefOid of pr #{} in repo {} is None".
                            format(str(prNumber), repository))

        # If the changed information of the Merged event is not collected, call the web information
        changedFilesCount = m["changedFilesCount"]
        if not changedFilesCount:
            changedFilesCount, additions, deletions = compare_commits_url(
                repository=repository, base_commit=base_commit, head_commit=head_commit)
            if changedFilesCount == "Exception":
                continue
            else:
                num_updated = Merged.objects(id=m_id).update(
                    changedFilesCount=changedFilesCount, additions=additions, deletions=deletions)
                if num_updated != 1:
                    raise Exception("!! There should be only one mergedEvent with the id: {}".format(m_id))
        else:
            continue

    return
