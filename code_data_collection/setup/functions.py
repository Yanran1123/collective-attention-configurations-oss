import mongoengine

from Classes.commit.commit import Commit
from Classes.event.comment.commitcomment import CommitComment
from Classes.event.comment.pullrequestreviewcomment import PullRequestReviewComment
from Classes.event.label.label import Label
from Classes.issuecollection.issue import Issue
from Classes.issuecollection.pullrequest import PullRequest
from Classes.repocollection.repo import Repo

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
from Classes.event.comment.commitcommentthread import CommitCommentThread
from Classes.event.comment.issuecomment import IssueComment
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


def update_repo_name(oldRepository, newRepository):
    """
    Update repository identification owner/name if it is changed
    :param oldRepository: the old owner/name of the corresponding repository in MongoDB
    :param newRepository: New owner/name of the repository
    :return: No return
    """
    repo = Repo.objects(nameWithOwner=oldRepository).first()
    repository = repo["nameWithOwner"]  # Equal to oldRepository

    delimiter = "/"
    newOwner = newRepository.split(delimiter)[0]
    newName = newRepository.split(delimiter)[1]

    # Update the "repository" field of Issue and PullRequest objects
    num_updated = Issue.objects(repository=repository).update(set__repository=newRepository)
    num_updated = PullRequest.objects(repository=repository).update(set__repository=newRepository)

    # Update the "repository" field of Commit objects
    num_updated = Commit.objects(repository=repository).update(set__repository=newRepository)

    # Update the "repository" field of 30 IssueEvent objects
    num_updated = AssignedEvent.objects(repository=repository).update(set__repository=newRepository)
    num_updated = UnassignedEvent.objects(repository=repository).update(set__repository=newRepository)
    num_updated = CommentDeletedEvent.objects(repository=repository).update(set__repository=newRepository)
    num_updated = IssueComment.objects(repository=repository).update(set__repository=newRepository)
    num_updated = ConnectedEvent.objects(sourceRepository=repository).update(set__sourceRepository=newRepository)
    num_updated = CrossReferencedEvent.objects(targetRepository=repository).update(set__targetRepository=newRepository)
    num_updated = DisconnectedEvent.objects(sourceRepository=repository).update(set__sourceRepository=newRepository)
    num_updated = ReferencedEvent.objects(repository=repository).update(set__repository=newRepository)
    num_updated = TransferredEvent.objects(repository=repository).update(set__repository=newRepository)
    num_updated = LabeledEvent.objects(repository=repository).update(set__repository=newRepository)
    num_updated = UnlabeledEvent.objects(repository=repository).update(set__repository=newRepository)
    num_updated = MentionedEvent.objects(repository=repository).update(set__repository=newRepository)
    num_updated = MilestonedEvent.objects(repository=repository).update(set__repository=newRepository)
    num_updated = DemilestonedEvent.objects(repository=repository).update(set__repository=newRepository)
    num_updated = ClosedEvent.objects(repository=repository).update(set__repository=newRepository)
    num_updated = ReopenedEvent.objects(repository=repository).update(set__repository=newRepository)
    num_updated = LockedEvent.objects(repository=repository).update(set__repository=newRepository)
    num_updated = UnlockedEvent.objects(repository=repository).update(set__repository=newRepository)
    num_updated = MarkedAsDuplicateEvent.objects(repository=repository).update(set__repository=newRepository)
    num_updated = UnmarkedAsDuplicateEvent.objects(repository=repository).update(set__repository=newRepository)
    num_updated = PinnedEvent.objects(repository=repository).update(set__repository=newRepository)
    num_updated = UnpinnedEvent.objects(repository=repository).update(set__repository=newRepository)
    num_updated = AddedToProjectEvent.objects(repository=repository).update(set__repository=newRepository)
    num_updated = ConvertedNoteToIssueEvent.objects(repository=repository).update(set__repository=newRepository)
    num_updated = MovedColumnsInProjectEvent.objects(repository=repository).update(set__repository=newRepository)
    num_updated = RemovedFromProjectEvent.objects(repository=repository).update(set__repository=newRepository)
    num_updated = SubscribedEvent.objects(repository=repository).update(set__repository=newRepository)
    num_updated = UnsubscribedEvent.objects(repository=repository).update(set__repository=newRepository)
    num_updated = RenamedTitleEvent.objects(repository=repository).update(set__repository=newRepository)
    num_updated = UserBlockedEvent.objects(repository=repository).update(set__repository=newRepository)

    # Update the "repository" field of 18 (commit is already updated) PullRequest only Event objects
    num_updated = AutomaticBaseChangeFailed.objects(repository=repository).update(set__repository=newRepository)
    num_updated = AutomaticBaseChangeSucceeded.objects(repository=repository).update(set__repository=newRepository)
    num_updated = BaseRefChanged.objects(repository=repository).update(set__repository=newRepository)
    num_updated = BaseRefForcePushed.objects(repository=repository).update(set__repository=newRepository)
    num_updated = HeadRefDeleted.objects(repository=repository).update(set__repository=newRepository)
    num_updated = HeadRefForcePushed.objects(repository=repository).update(set__repository=newRepository)
    num_updated = HeadRefRestored.objects(repository=repository).update(set__repository=newRepository)
    num_updated = CommitCommentThread.objects(repository=repository).update(set__repository=newRepository)
    num_updated = ConvertToDraft.objects(repository=repository).update(set__repository=newRepository)
    num_updated = Deployed.objects(repository=repository).update(set__repository=newRepository)
    num_updated = DeploymentEnvironmentChanged.objects(repository=repository).update(set__repository=newRepository)
    num_updated = Merged.objects(repository=repository).update(set__repository=newRepository)
    num_updated = PullRequestReview.objects(repository=repository).update(set__repository=newRepository)
    num_updated = PullRequestReviewThread.objects(repository=repository).update(set__repository=newRepository)
    num_updated = ReadyForReview.objects(repository=repository).update(set__repository=newRepository)
    num_updated = ReviewDismissed.objects(repository=repository).update(set__repository=newRepository)
    num_updated = ReviewRequested.objects(repository=repository).update(set__repository=newRepository)
    num_updated = ReviewRequestRemoved.objects(repository=repository).update(set__repository=newRepository)

    # Update the "repository" field of CommitComment and PullRequestReviewComment objects
    num_updated = CommitComment.objects(repository=repository).update(set__repository=newRepository)
    num_updated = PullRequestReviewComment.objects(repository=repository).update(set__repository=newRepository)

    # Update the "repository" field of Label objects
    num_updated = Label.objects(repository=repository).update(set__repository=newRepository)

    # Update the "name" and "nameWithOwner" fields of Repo objects
    num_updated = repo.update(set__owner=newOwner, set__name=newName, set__nameWithOwner=newRepository)


