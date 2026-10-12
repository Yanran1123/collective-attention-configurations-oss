import datetime
# import math
# import pprint
import json
import time

from pathlib2 import Path

# from Classes.repocollection.release import Release
from Classes.commit.commit import Commit
from Classes.event.assign.assigned import AssignedEvent
from Classes.event.assign.unassigned import UnassignedEvent
from Classes.event.basehead.automaticbasechangefailed import AutomaticBaseChangeFailed
from Classes.event.basehead.automaticbasechangesucceeded import AutomaticBaseChangeSucceeded
from Classes.event.basehead.baserefchanged import BaseRefChanged
from Classes.event.basehead.baserefforcepushed import BaseRefForcePushed
from Classes.event.basehead.headrefdeleted import HeadRefDeleted
from Classes.event.basehead.headrefforcepushed import HeadRefForcePushed
from Classes.event.basehead.headrefrestored import HeadRefRestored
from Classes.event.comment.commentdeleted import CommentDeletedEvent
from Classes.event.comment.commitcomment import CommitComment
from Classes.event.comment.commitcommentthread import CommitCommentThread
from Classes.event.comment.issuecomment import IssueComment
from Classes.event.comment.pullrequestreviewcomment import PullRequestReviewComment
from Classes.event.connection.connected import ConnectedEvent
from Classes.event.connection.crossreferenced import CrossReferencedEvent
from Classes.event.connection.disconnected import DisconnectedEvent
from Classes.event.connection.referenced import ReferencedEvent
from Classes.event.connection.transferred import TransferredEvent
from Classes.event.label.labeled import LabeledEvent
from Classes.event.label.unlabeled import UnlabeledEvent
from Classes.event.mention.mentioned import MentionedEvent
from Classes.event.milestone.demilestoned import DemilestonedEvent
from Classes.event.milestone.milestoned import MilestonedEvent
from Classes.event.otherpronly.converttodraft import ConvertToDraft
from Classes.event.otherpronly.deployed import Deployed
from Classes.event.otherpronly.deploymentenvironmentchanged import DeploymentEnvironmentChanged
from Classes.event.output.merged import Merged
from Classes.event.priority.closed import ClosedEvent
from Classes.event.priority.locked import LockedEvent
from Classes.event.priority.markedasduplicate import MarkedAsDuplicateEvent
from Classes.event.priority.pinned import PinnedEvent
from Classes.event.priority.reopened import ReopenedEvent
from Classes.event.priority.unlocked import UnlockedEvent
from Classes.event.priority.unmarkedasduplicate import UnmarkedAsDuplicateEvent
from Classes.event.priority.unpinned import UnpinnedEvent
from Classes.event.project.addedtoproject import AddedToProjectEvent
from Classes.event.project.convertednotetoissue import ConvertedNoteToIssueEvent
from Classes.event.project.movedcolumnsinproject import MovedColumnsInProjectEvent
from Classes.event.project.removedfromproject import RemovedFromProjectEvent
from Classes.event.review.pullrequestreview import PullRequestReview
from Classes.event.review.pullrequestreviewthread import PullRequestReviewThread
from Classes.event.review.readyforreview import ReadyForReview
from Classes.event.review.reviewdismissed import ReviewDismissed
from Classes.event.review.reviewrequested import ReviewRequested
from Classes.event.review.reviewrequestremoved import ReviewRequestRemoved
from Classes.event.subscription.subscribed import SubscribedEvent
from Classes.event.subscription.unsubscribed import UnsubscribedEvent
from Classes.event.title.renamedtitle import RenamedTitleEvent
from Classes.event.userblock.userblocked import UserBlockedEvent
from Classes.issuecollection.pullrequest import PullRequest
from Classes.repocollection.repo import Repo
from explore.issueprstatistics import issue_pr_count_csv
from explore.reposelection import get_small_sample
# from explore.repostatistics import repo_info_csv, topic_modeling
from fetchGitHub.fetchcommit import update_changed_info
from fetchGitHub.fetchcommit_graphql import save_repo_commit_graphQL
from fetchGitHub.fetchissueinfo import add_issues
from fetchGitHub.fetchprevents import update_pr_timeline_items
from fetchGitHub.fetchprevents_repair import update_pr_timeline_items_repair
from fetchGitHub.fetchprinfo import update_pr_part2, add_prs_part1, update_pr_base_associationPRs, \
    update_pr_head_associationPRs, update_pr_changed_files, update_pr_edits, update_pr_suggested_reviewers
from fetchGitHub.fetchrepoinfo import add_repo, update_release, update_topic, update_language, repo_found
from fetchGitHub.fetchrepolist import fetch_repo_list
from fetchGitHub.fetchrepolist_new import search_repo_new, fetch_repo_list_period
from setup import mongo_setup as mongo_setup
from setup.graphql import run_query_variable, get_remaining, get_reset, sleep_in_seconds

# import calendar
import csv
# import string


def config_mongo():
    mongo_setup.global_init()


# Pass where to write the resultant repo list
def save_repo_list(repo_list_csv_path):
    config_mongo()

    repos = fetch_repo_list("machine-learning", "2019-12-31")
    print(len(repos))

    # EXAMPLE: repos = [["owner1", "name1"], ["owner2", "name2"]]
    with open(repo_list_csv_path, mode='w') as repo_list:
        repo_writer = csv.writer(repo_list, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        for repo in repos:
            repo_writer.writerow(repo)


# Get information of a list of repos searched by based_query and period (start_date and end_date)
def save_repo_list_new(repo_list_csv_path):
    config_mongo()

    base_query = "is:public is:root"  # conditions of search query except the time period part
    start_date = "2008-01-01"  # created from the start date in the format of "YYYY-MM-DD" --> YYYY-MM-DDT00:00:00
    end_date = "2010-01-01"  # created before the end date in the format of "YYYY-MM-DD" --> YYYY-MM-DDT00:00:00

    repos = fetch_repo_list_period(base_query, start_date, end_date)
    print(len(repos))

    # EXAMPLE: repos = [["owner1", "name1", "createdAt1", "languageSize1", "releaseCount1"], ["owner2", "name2"...]]
    with open(repo_list_csv_path, mode='w') as repo_list:
        repo_writer = csv.writer(repo_list, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        repo_writer.writerow(["owner", "name", "createdAt", "languageSize", "releaseCount"])
        for repo in repos:
            repo_writer.writerow(repo)


# Get information of all repos in the list repo_list_dupRemoved.csv
# Pass the path to the repo_list_dupRemoved.csv file
def save_repo_info(repo_list_dupRemoved_csv_path):
    config_mongo()

    with open(repo_list_dupRemoved_csv_path) as repo_list:
        repo_reader = csv.reader(repo_list, delimiter=',')
        repo_count = 0
        for row in repo_reader:
            if repo_count == 0:
                print("BEGIN TO FETCH REPO INFO")
                repo_count = repo_count + 1
            else:
                owner = row[0]
                name = row[1]
                if "#NAME?" in owner or "#NAME?" in name:
                    print("SKIPPED REPO WITH STRANGE NAME: {}/{}".format(owner, name))
                else:
                    if get_remaining() > 20:
                        if repo_found(owner, name):
                            add_repo(owner, name)
                            update_release(owner, name)
                            update_topic(owner, name)
                            update_language(owner, name)
                            print("Successfully get info of repo: {}/{}".format(owner, name))
                        else:
                            print("No repository {}/{}".format(owner, name))
                    else:
                        print("Need to sleep 3610 seconds, about 1 hour")
                        time.sleep(3610)
                        config_mongo()
                        print("Restart! :-)")
                        if repo_found(owner, name):
                            add_repo(owner, name)
                            update_release(owner, name)
                            update_topic(owner, name)
                            update_language(owner, name)
                            print("Successfully get info of repo: {}/{}".format(owner, name))
                        else:
                            print("No repository {}/{}".format(owner, name))
                if repo_count % 1000 == 0:
                    print("Complete collection information of {} repos!!")
                repo_count = repo_count + 1


# Pass where to write the final repo list
def repo_list_final_csv(repo_list_final_csv_path):
    config_mongo()

    repos = Repo.objects.only("owner", "name")
    # Note that repos is a list of Repo object with only the data at "owner" and "name" fields

    with open(repo_list_final_csv_path, mode='w') as repo_list:
        repo_writer = csv.writer(repo_list, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for repo in repos:
            repo_writer.writerow([repo["owner"], repo["name"]])


def pr_list_csv(pr_list_csv_path):
    config_mongo()
    prs = PullRequest.objects().only("repository", "number")

    pr_begin_index = 0
    pr_end_index = 99999  # when I fill the range the range data should be pr_end_index+1
    delimiter = "/"

    with open(pr_list_csv_path, mode='w') as pr_list:
        csv_writer = csv.writer(pr_list, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for i in range(pr_begin_index, pr_end_index+1):
            repository = prs[i]["repository"]
            owner = repository.split(delimiter)[0]
            name = repository.split(delimiter)[1]
            number = prs[i]["number"]
            csv_writer.writerow([owner, name, number])


def delete_pr_event(eventType, eventId):
    if eventType == "AssignedEvent":
        num_deleted = AssignedEvent.objects(id=eventId).delete()
        if num_deleted != 1:
            raise Exception("There are no {} or multiple {} with eventId {}".format(eventType, eventType, eventId))
    elif eventType == "UnassignedEvent":
        num_deleted = UnassignedEvent.objects(id=eventId).delete()
        if num_deleted != 1:
            raise Exception("There are no {} or multiple {} with eventId {}".format(eventType, eventType, eventId))
    elif eventType == "IssueComment":
        num_deleted = IssueComment.objects(id=eventId).delete()
        if num_deleted != 1:
            raise Exception("There are no {} or multiple {} with eventId {}".format(eventType, eventType, eventId))
    elif eventType == "CommentDeletedEvent":
        num_deleted = CommentDeletedEvent.objects(id=eventId).delete()
        if num_deleted != 1:
            raise Exception("There are no {} or multiple {} with eventId {}".format(eventType, eventType, eventId))
    elif eventType == "ConnectedEvent":
        num_deleted = ConnectedEvent.objects(id=eventId).delete()
        if num_deleted != 1:
            raise Exception("There are no {} or multiple {} with eventId {}".format(eventType, eventType, eventId))
    elif eventType == "DisconnectedEvent":
        num_deleted = DisconnectedEvent.objects(id=eventId).delete()
        if num_deleted != 1:
            raise Exception("There are no {} or multiple {} with eventId {}".format(eventType, eventType, eventId))
    elif eventType == "CrossReferencedEvent":
        num_deleted = CrossReferencedEvent.objects(id=eventId).delete()
        if num_deleted != 1:
            raise Exception("There are no {} or multiple {} with eventId {}".format(eventType, eventType, eventId))
    elif eventType == "ReferencedEvent":
        num_deleted = ReferencedEvent.objects(id=eventId).delete()
        if num_deleted != 1:
            raise Exception("There are no {} or multiple {} with eventId {}".format(eventType, eventType, eventId))
    elif eventType == "TransferredEvent":
        num_deleted = TransferredEvent.objects(id=eventId).delete()
        if num_deleted != 1:
            raise Exception("There are no {} or multiple {} with eventId {}".format(eventType, eventType, eventId))
    elif eventType == "LabeledEvent":
        num_deleted = LabeledEvent.objects(id=eventId).delete()
        if num_deleted != 1:
            raise Exception("There are no {} or multiple {} with eventId {}".format(eventType, eventType, eventId))
    elif eventType == "UnlabeledEvent":
        num_deleted = UnlabeledEvent.objects(id=eventId).delete()
        if num_deleted != 1:
            raise Exception("There are no {} or multiple {} with eventId {}".format(eventType, eventType, eventId))
    elif eventType == "MentionedEvent":
        num_deleted = MentionedEvent.objects(id=eventId).delete()
        if num_deleted != 1:
            raise Exception("There are no {} or multiple {} with eventId {}".format(eventType, eventType, eventId))
    elif eventType == "MilestonedEvent":
        num_deleted = MilestonedEvent.objects(id=eventId).delete()
        if num_deleted != 1:
            raise Exception("There are no {} or multiple {} with eventId {}".format(eventType, eventType, eventId))
    elif eventType == "DemilestonedEvent":
        num_deleted = DemilestonedEvent.objects(id=eventId).delete()
        if num_deleted != 1:
            raise Exception("There are no {} or multiple {} with eventId {}".format(eventType, eventType, eventId))
    elif eventType == "ClosedEvent":
        num_deleted = ClosedEvent.objects(id=eventId).delete()
        if num_deleted != 1:
            raise Exception("There are no {} or multiple {} with eventId {}".format(eventType, eventType, eventId))
    elif eventType == "ReopenedEvent":
        num_deleted = ReopenedEvent.objects(id=eventId).delete()
        if num_deleted != 1:
            raise Exception("There are no {} or multiple {} with eventId {}".format(eventType, eventType, eventId))
    elif eventType == "LockedEvent":
        num_deleted = LockedEvent.objects(id=eventId).delete()
        if num_deleted != 1:
            raise Exception("There are no {} or multiple {} with eventId {}".format(eventType, eventType, eventId))
    elif eventType == "UnlockedEvent":
        num_deleted = UnlockedEvent.objects(id=eventId).delete()
        if num_deleted != 1:
            raise Exception("There are no {} or multiple {} with eventId {}".format(eventType, eventType, eventId))
    elif eventType == "PinnedEvent":
        num_deleted = PinnedEvent.objects(id=eventId).delete()
        if num_deleted != 1:
            raise Exception("There are no {} or multiple {} with eventId {}".format(eventType, eventType, eventId))
    elif eventType == "UnpinnedEvent":
        num_deleted = UnpinnedEvent.objects(id=eventId).delete()
        if num_deleted != 1:
            raise Exception("There are no {} or multiple {} with eventId {}".format(eventType, eventType, eventId))
    elif eventType == "MarkedAsDuplicateEvent":
        num_deleted = MarkedAsDuplicateEvent.objects(id=eventId).delete()
        if num_deleted != 1:
            raise Exception("There are no {} or multiple {} with eventId {}".format(eventType, eventType, eventId))
    elif eventType == "UnmarkedAsDuplicateEvent":
        num_deleted = UnmarkedAsDuplicateEvent.objects(id=eventId).delete()
        if num_deleted != 1:
            raise Exception("There are no {} or multiple {} with eventId {}".format(eventType, eventType, eventId))
    elif eventType == "AddedToProjectEvent":
        num_deleted = AddedToProjectEvent.objects(id=eventId).delete()
        if num_deleted != 1:
            raise Exception("There are no {} or multiple {} with eventId {}".format(eventType, eventType, eventId))
    elif eventType == "RemovedFromProjectEvent":
        num_deleted = RemovedFromProjectEvent.objects(id=eventId).delete()
        if num_deleted != 1:
            raise Exception("There are no {} or multiple {} with eventId {}".format(eventType, eventType, eventId))
    elif eventType == "MovedColumnsInProjectEvent":
        num_deleted = MovedColumnsInProjectEvent.objects(id=eventId).delete()
        if num_deleted != 1:
            raise Exception("There are no {} or multiple {} with eventId {}".format(eventType, eventType, eventId))
    elif eventType == "ConvertedNoteToIssueEvent":
        num_deleted = ConvertedNoteToIssueEvent.objects(id=eventId).delete()
        if num_deleted != 1:
            raise Exception("There are no {} or multiple {} with eventId {}".format(eventType, eventType, eventId))
    elif eventType == "SubscribedEvent":
        num_deleted = SubscribedEvent.objects(id=eventId).delete()
        if num_deleted != 1:
            raise Exception("There are no {} or multiple {} with eventId {}".format(eventType, eventType, eventId))
    elif eventType == "UnsubscribedEvent":
        num_deleted = UnsubscribedEvent.objects(id=eventId).delete()
        if num_deleted != 1:
            raise Exception("There are no {} or multiple {} with eventId {}".format(eventType, eventType, eventId))
    elif eventType == "RenamedTitleEvent":
        num_deleted = RenamedTitleEvent.objects(id=eventId).delete()
        if num_deleted != 1:
            raise Exception("There are no {} or multiple {} with eventId {}".format(eventType, eventType, eventId))
    elif eventType == "UserBlockedEvent":
        num_deleted = UserBlockedEvent.objects(id=eventId).delete()
        if num_deleted != 1:
            raise Exception("There are no {} or multiple {} with eventId {}".format(eventType, eventType, eventId))
    elif eventType == "AutomaticBaseChangeFailedEvent":
        num_deleted = AutomaticBaseChangeFailed.objects(id=eventId).delete()
        if num_deleted != 1:
            raise Exception("There are no {} or multiple {} with eventId {}".format(eventType, eventType, eventId))
    elif eventType == "AutomaticBaseChangeSucceededEvent":
        num_deleted = AutomaticBaseChangeSucceeded.objects(id=eventId).delete()
        if num_deleted != 1:
            raise Exception("There are no {} or multiple {} with eventId {}".format(eventType, eventType, eventId))
    elif eventType == "BaseRefChangedEvent":
        num_deleted = BaseRefChanged.objects(id=eventId).delete()
        if num_deleted != 1:
            raise Exception("There are no {} or multiple {} with eventId {}".format(eventType, eventType, eventId))
    elif eventType == "BaseRefForcePushedEvent":
        num_deleted = BaseRefForcePushed.objects(id=eventId).delete()
        if num_deleted != 1:
            raise Exception("There are no {} or multiple {} with eventId {}".format(eventType, eventType, eventId))
    elif eventType == "HeadRefDeletedEvent":
        num_deleted = HeadRefDeleted.objects(id=eventId).delete()
        if num_deleted != 1:
            raise Exception("There are no {} or multiple {} with eventId {}".format(eventType, eventType, eventId))
    elif eventType == "HeadRefForcePushedEvent":
        num_deleted = HeadRefForcePushed.objects(id=eventId).delete()
        if num_deleted != 1:
            raise Exception("There are no {} or multiple {} with eventId {}".format(eventType, eventType, eventId))
    elif eventType == "HeadRefRestoredEvent":
        num_deleted = HeadRefRestored.objects(id=eventId).delete()
        if num_deleted != 1:
            raise Exception("There are no {} or multiple {} with eventId {}".format(eventType, eventType, eventId))
    elif eventType == "PullRequestCommit":
        print("Keep the commit!")
    elif eventType == "PullRequestCommitCommentThread":
        # Delete the associated reviewComments
        events = CommitCommentThread.objects(id=eventId)
        if len(events) != 1:
            raise Exception("There are no {} or multiple {} with eventId {}".format(eventType, eventType, eventId))
        for commentId in events[0]["commitCommentIds"]:
            num_deleted = CommitComment.objects(id=commentId).delete()
            if num_deleted != 1:
                raise Exception("There are no or multiple pullRequestReviewComments with eventId {}".format(eventId))
        # Delete the pullRequestReviewThread
        num_deleted = CommitCommentThread.objects(id=eventId).delete()
        if num_deleted != 1:
            raise Exception("There are no {} or multiple {} with eventId {}".format(eventType, eventType, eventId))
    elif eventType == "ConvertToDraftEvent":
        num_deleted = ConvertToDraft.objects(id=eventId).delete()
        if num_deleted != 1:
            raise Exception("There are no {} or multiple {} with eventId {}".format(eventType, eventType, eventId))
    elif eventType == "DeployedEvent":
        num_deleted = Deployed.objects(id=eventId).delete()
        if num_deleted != 1:
            raise Exception("There are no {} or multiple {} with eventId {}".format(eventType, eventType, eventId))
    elif eventType == "DeploymentEnvironmentChangedEvent":
        num_deleted = DeploymentEnvironmentChanged.objects(id=eventId).delete()
        if num_deleted != 1:
            raise Exception("There are no {} or multiple {} with eventId {}".format(eventType, eventType, eventId))
    elif eventType == "MergedEvent":
        num_deleted = Merged.objects(id=eventId).delete()
        if num_deleted != 1:
            raise Exception("There are no {} or multiple {} with eventId {}".format(eventType, eventType, eventId))
    elif eventType == "PullRequestReview":
        # Delete the associated reviewComments
        events = PullRequestReview.objects(id=eventId)
        if len(events) != 1:
            raise Exception("There are no {} or multiple {} with eventId {}".format(eventType, eventType, eventId))
        for commentId in events[0]["reviewCommentIds"]:
            num_deleted = PullRequestReviewComment.objects(id=commentId).delete()
            if num_deleted != 1:
                raise Exception("There are no or multiple pullRequestReviewComments with eventId {}".format(eventId))
        # Delete the pullRequestReviewThread
        num_deleted = PullRequestReview.objects(id=eventId).delete()
        if num_deleted != 1:
            raise Exception("There are no {} or multiple {} with eventId {}".format(eventType, eventType, eventId))
    elif eventType == "PullRequestReviewThread":
        # Delete the associated reviewComments
        events = PullRequestReviewThread.objects(id=eventId)
        if len(events) != 1:
            raise Exception("There are no {} or multiple {} with eventId {}".format(eventType, eventType, eventId))
        for commentId in events[0]["reviewCommentIds"]:
            num_deleted = PullRequestReviewComment.objects(id=commentId).delete()
            if num_deleted != 1:
                raise Exception("There are no or multiple pullRequestReviewComments with eventId {}".format(eventId))
        # Delete the pullRequestReviewThread
        num_deleted = PullRequestReviewThread.objects(id=eventId).delete()
        if num_deleted != 1:
            raise Exception("There are no {} or multiple {} with eventId {}".format(eventType, eventType, eventId))
    elif eventType == "ReadyForReviewEvent":
        num_deleted = ReadyForReview.objects(id=eventId).delete()
        if num_deleted != 1:
            raise Exception("There are no {} or multiple {} with eventId {}".format(eventType, eventType, eventId))
    elif eventType == "ReviewDismissedEvent":
        num_deleted = ReviewDismissed.objects(id=eventId).delete()
        if num_deleted != 1:
            raise Exception("There are no {} or multiple {} with eventId {}".format(eventType, eventType, eventId))
    elif eventType == "ReviewRequestedEvent":
        num_deleted = ReviewRequested.objects(id=eventId).delete()
        if num_deleted != 1:
            raise Exception("There are no {} or multiple {} with eventId {}".format(eventType, eventType, eventId))
    elif eventType == "ReviewRequestRemovedEvent":
        num_deleted = ReviewRequestRemoved.objects(id=eventId).delete()
        if num_deleted != 1:
            raise Exception("There are no {} or multiple {} with eventId {}".format(eventType, eventType, eventId))
    else:
        raise Exception("{} is an unexpected event type of issue timeline items".format(eventType))


def main():

    start_time = datetime.datetime.now()

    # *****************************
    # CORE PROGRAM

    config_mongo()

    # --------------------------------------------------------------------------------
    # --------------------------------------------------------------------------------

    # Get PullRequestEvents

    # Delete interrupted update TimelineItems
    # If an error occurs when fetching events associated with a pr, we need to clear out the added events
    # to start over again for the specific issue.
    #
    repository_delete = "apple/turicreate"
    number_delete = 2819
    # 1. Clear events associated with the timelineItems of the pullRequest
    prs_delete = PullRequest.objects().filter(repository=repository_delete, number=number_delete)
    if len(prs_delete) == 1:
        pr = prs_delete[0]
        if pr["timeline"]:
            for item in pr["timeline"]:
                eventType = item["eventType"]
                eventId = item["eventId"]
                delete_pr_event(eventType=eventType, eventId=eventId)
    else:
        raise Exception("There are no or multiple pullRequests with number {} in repo {} updated -- MongoDB database".
                        format(str(number_delete), repository_delete))
    # 2. Unset the timeline field of the pullRequest
    num_updated = PullRequest.objects().filter(repository=repository_delete, number=number_delete).\
        update_one(unset__timeline=1)
    if num_updated != 1:
        raise Exception("There are no or multiple pullRequests with number {} in repo {} updated -- MongoDB database".
                        format(str(number_delete), repository_delete))

    # ............................................

    # Continue to get PullRequestEvents

    # prs = PullRequest.objects().only("repository", "number")
    #
    # pr_index_begin = 247576 + 1
    # # pr[16420] The owner of this corresponding repo are both changed from IBM/AIX360 to Trusted-AI/AIX360
    # # pr[19473] pullRequest #64 of repo KevinMusgrave/pytorch-metric-learning Cannot be found any more!
    # # Skipped pr[247576] pullRequest #2819 of repo apple/turicreate, because its
    # #   commit a3d7419d938d69f3f7dcdab6d066eead1ac99582 has too many files changed and
    # #   cannot be fetched by GitHub REST API V3
    # delimiter = "/"
    # length = 249549  # len(prs) = 249549
    # for i in range(pr_index_begin, length):
    #     repository = prs[i]["repository"]
    #     owner = repository.split(delimiter)[0]
    #     name = repository.split(delimiter)[1]
    #     number = prs[i]["number"]
    #
    #     # if i % 5000 == 0:
    #     #     time.sleep(3600)
    #
    #     update_pr_timeline_items(owner, name, number)
    #
    #     print("The prs[{}] (pull request #{} of repo {}) is now finished".format(str(i), str(number), repository))
    #     print("Timestamp: {}".format(datetime.datetime.now()))
    #     print("*******************************************************\n")

    # ............................................

    # Repair the errors of "Something went wrong"

    # The path of file that record information of the pullRequests that have the error
    # path = Path("path/to/errors/prEvent_variablesOfQueryForTimelineItems_server.jscsrc")
    # with open(path) as json_file:
    #     data = json.load(json_file)  # if data is a list
    #     length = len(data)
    #     print("{} pullReqeusts need to be repaired!".format(str(length)))
    #     print("*******************************************************\n")
    #     begin_index = 3684 + 1
    #     for i in range(begin_index, length):
    #         update_pr_timeline_items_repair(data[i]["owner"], data[i]["name"], data[i]["number"])
    #
    #         print("The prs[{}] (pull request #{} of repo {}) is now finished".format(str(i), data[i]["number"],
    #                                                                                  data[i]["owner"] + "/" +
    #                                                                                  data[i]["name"]))
    #         print("Timestamp: {}".format(datetime.datetime.now()))
    #         print("*******************************************************\n")
    #     json_file.close()
    #
    # print("{} pullReqeusts need to be repaired!".format(str(len(data))))
    # print("*******************************************************\n")

    # ............................................

    # Repaire the issue of pullRequest #2819 of repo apple/turicreate
    # Cannot save commitOid a3d7419d938d69f3f7dcdab6d066eead1ac99582 because it has too many changed files
    # Actually, this is a merge commit

    repository = "apple/turicreate"

    # commitOid = "a3d7419d938d69f3f7dcdab6d066eead1ac99582"
    # save_repo_commit_graphQL(repository=repository, commitOid=commitOid)

    delimiter = "/"
    owner = repository.split(delimiter)[0]
    name = repository.split(delimiter)[1]
    update_pr_timeline_items(owner=owner, name=name, number=2819)


    # *******************************

    end_time = datetime.datetime.now()
    delta = end_time - start_time
    days = delta.days
    hours = int(delta.seconds / 3600)
    minutes = int((delta.seconds - hours * 3600) / 60)
    seconds = delta.seconds - hours * 3600 - minutes * 60
    print("\nRunning the program costs {} days, {} hours, {} minutes, and {} seconds,".
          format(str(days), str(hours), str(minutes), str(seconds)))
    print("Finished. Congratulations! :-)")

    # -------------------------------------------------------------------------------------------------------
    #
    # # Get pull-request information
    #
    # # repos = Repo.objects().only("owner", "name")
    # # start_time = datetime.datetime.now()
    # # begin_index = 99
    # # for i in range(begin_index, len(repos)):
    # #     add_prs_part1(owner=repos[i]["owner"], name=repos[i]["name"])
    # #     print("repos[{}] is finished".format(str(i)))
    #
    # # time.sleep(4000)
    # # update_pr_base_associationPRs(owner="scikit-learn", name="scikit-learn", number=14097)
    # # update_pr_head_associationPRs(owner="scikit-learn", name="scikit-learn", number=14097)
    #
    # # update_pr_changed_files(owner="apple", name="turicreate", number=2458)
    # # update_pr_edits(owner="apple", name="turicreate", number=2458)
    # # update_pr_suggested_reviewers(owner="apple", name="turicreate", number=2458)
    #
    # print("*******************************************************\n")
    #
    # prs = PullRequest.objects().only("repository", "number")
    # pr_index_begin = 247650 + 1
    # start_time = datetime.datetime.now()
    # delimiter = "/"
    # for i in range(pr_index_begin, len(prs)):
    #     repository = prs[i]["repository"]
    #     owner = repository.split(delimiter)[0]
    #     name = repository.split(delimiter)[1]
    #     number = prs[i]["number"]
    #
    #     update_pr_part2(owner=owner, name=name, number=number)
    #     # ------------------------------
    #     # Note: From prs[9649] (after finishing [9648], # 14121 scikit-learn/scikit-lesrn),
    #     # we stopped collecting baseAssociatedPRs and headAssociatedPRs.
    #
    #     # update_pr_base_associationPRs(owner=owner, name=name, number=number)
    #     # update_pr_head_associationPRs(owner=owner, name=name, number=number)
    #     # ------------------------------
    #     update_pr_changed_files(owner=owner, name=name, number=number)
    #     update_pr_edits(owner=owner, name=name, number=number)
    #     update_pr_suggested_reviewers(owner=owner, name=name, number=number)
    #
    #     print("The prs[{}] (pull request #{} of repo {}) is now finished".format(str(i), str(number), repository))
    #     print("Timestamp: {}".format(datetime.datetime.now()))
    #     print("*******************************************************\n")

    # ---------------------------------------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------------------

    # Update the changed files of commit

    # commits = Commit.objects().only("repository", "oid")
    #
    # commits_list = []
    #
    # for commit in commits:
    #     repository = commit["repository"]
    #     commitOid = commit["oid"]
    #     commits_list.append([repository, commitOid])
    #
    # remaining_server = 0
    # reset_server = datetime.datetime.now().timestamp() + 1200
    #
    # remaining_office = 5000
    # reset_office = datetime.datetime.now().timestamp() + 3600 + 120
    #
    # remaining_mac = 5000
    # reset_mac = datetime.datetime.now().timestamp() + 3600 + 120
    #
    # #
    # # # Address the issue of an interrupt for fetching information of a commit
    # # # Clear the half-updated commit
    # # repository = "jtablesaw/tablesaw"
    # # oid = "c812f3f75e67665f388a7b308b7b8949086e88cf"
    # # num_updated = Commit.objects(repository=repository, oid=oid).update(unset__changedFiles=1)
    # # if num_updated != 1:
    # #     raise Exception("Check the number of commit with oid {} in repo {}".format(oid, repository))
    # #
    # # Update the additions, deletions, and changedFiles of all commits
    # begin_index = 1226926 + 1
    # length = len(commits_list)
    # for i in range(begin_index, length):
    #     repository = commits_list[i][0]
    #     commitOid = commits_list[i][1]
    #
    #     remaining_server, remaining_office, remaining_mac, reset_server, reset_office, reset_mac = \
    #         update_changed_info(repository=repository, commitOid=commitOid, remaining_server=remaining_server,
    #                             remaining_office=remaining_office, remaining_mac=remaining_mac,
    #                             reset_server=reset_server, reset_office=reset_office, reset_mac=reset_mac)
    #
    #     print("Remaining score (server): {}".format(str(remaining_server)))
    #     print("Remaining score (office): {}".format(str(remaining_office)))
    #     print("Remaining score (mac): {}".format(str(remaining_mac)))
    #     # print("Reset: {}".format(str(reset)))
    #     print("commits[{}] is finished.".format(str(i)))
    #     print("Timestamp: {}".format(datetime.datetime.now()))
    #     print("********************************************************\n")


main()
