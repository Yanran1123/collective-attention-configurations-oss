import csv

from Classes.issuecollection.issue import Issue
from Classes.issuecollection.pullrequest import PullRequest
from Classes.repocollection.repo import Repo


def issue_pr_count_csv():
    repos = Repo.objects().only("nameWithOwner")

    with open('/path/to/project/issue_pr_statistics.csv', mode='w') as repo_list:
        repo_writer = csv.writer(repo_list, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        repo_writer.writerow(["repository", "issueCount", "prCount"])

        for repo in repos:
            repository = repo["nameWithOwner"]
            issueCount = Issue.objects(repository=repository).count()
            prCount = PullRequest.objects(repository=repository).count()
            repo_writer.writerow([repository, issueCount, prCount])
