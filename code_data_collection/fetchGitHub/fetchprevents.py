import time
import json

from pathlib2 import Path

from Classes.actorcollection.team import Team
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
from Classes.event.label.label import Label
from Classes.event.label.labeled import LabeledEvent
from Classes.event.label.unlabeled import UnlabeledEvent
from Classes.event.mention.mentioned import MentionedEvent
from Classes.event.milestone.demilestoned import DemilestonedEvent
from Classes.event.milestone.milestoned import MilestonedEvent
from Classes.event.otherpronly.converttodraft import ConvertToDraft
from Classes.event.otherpronly.deployed import Deployed
from Classes.event.otherpronly.deployment import Deployment
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
from Classes.issuecollection.edit import Edit
from Classes.issuecollection.issue import Issue
from Classes.issuecollection.pullrequest import PullRequest

from Classes.issuecollection.reactiongroup import ReactionGroup
from Classes.issuecollection.timelineitem import TimelineItem
from Classes.repocollection.repo import Repo
from fetchGitHub.fetchcommit import save_repo_commit
from fetchGitHub.fetchissueevents import get_issue_or_pr_id
from setup.functions import update_repo_name
from setup.graphql import get_remaining, run_query_variable, sleep_in_seconds, get_reset


first = 30
cost = 30

# Set the path of JSON files that record the error messages and the corresponding variables
path_message = Path("path/to/errors/prEvent_errorMessages_server.jscsrc")
path_var = Path("path/to/errors/prEvent_variablesOfQueryForTimelineItems_server.jscsrc")


def update_pr_timeline_items(owner, name, number):
    """
    Update the timelineItems of a pullRequest
    :param owner: Owner of the associated repository
    :param name: Name of the associated repository
    :param number: Number of the pullRequest
    :return: No return; the event objects are saved and the timeline of the pullRequest is updated in MongoDB
    """
    print("Working on pullRequest #{} of repo {}/{}".format(str(number), owner, name))

    variables_total_count = {
        "owner": owner,
        "name": name,
        "number": number
    }

    # fetch_with_pagination(variables_total_count=variables_total_count)

    fetch_with_skip(variables_total_count=variables_total_count)


def fetch_with_skip(variables_total_count):
    events = []

    # Get nodes of timelineItems associated with the specific issue
    query_total_count = """
    query($owner: String!, $name: String!, $number: Int!) {
      repository(owner: $owner, name: $name){
        owner{
          login
          __typename
        }
        name
        pullRequest(number: $number){
          timelineItems(first: 1){
            totalCount
          }
        }
      }
    }
    """

    query_skip = """
    query($owner: String!, $name: String!, $number: Int!, $first: Int!, $skip: Int!) {
      rateLimit{
        cost
        remaining
      }
      repository(owner: $owner, name: $name){
        pullRequest(number: $number){
          timelineItems(first: $first, skip: $skip){
            totalCount
            pageInfo{
              hasNextPage
              endCursor
            }
            edges{
              cursor
              node{

                ... on AssignedEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt

                  assignee{
                    ... on User{
                      login
                      __typename
                    }
                    ... on Bot{
                      login
                      __typename
                    }
                    ... on Organization{
                      login
                      __typename
                    }
                    ... on Mannequin{
                      login
                      __typename
                    }
                  }

                  assignable{
                    __typename
                    ... on PullRequest{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                  }
                }

                ... on UnassignedEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt

                  assignee{
                    ... on User{
                      login
                      __typename
                    }
                    ... on Bot{
                      login
                      __typename
                    }
                    ... on Organization{
                      login
                      __typename
                    }
                    ... on Mannequin{
                      login
                      __typename
                    }
                  }

                  assignable{
                    __typename
                    ... on PullRequest{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                  } 
                }

                ... on IssueComment{
                  __typename
                  author{
                    login
                    __typename
                  }
                  authorAssociation
                  createdAt
                  createdViaEmail
                  publishedAt
                  updatedAt
                  databaseId
                  resourcePath
                  url
                  pullRequest{
                    __typename
                    repository{
                      nameWithOwner
                    }
                    number
                  }
                  isMinimized
                  minimizedReason
                  body
                  bodyHTML
                  bodyText
                  editor{
                    login
                    __typename
                  }
                  includesCreatedEdit
                  lastEditedAt
                  userContentEdits(first:50){
                    totalCount
                    nodes{
                      editor{
                        login
                        __typename
                      }
                      createdAt
                      editedAt
                      updatedAt
                      deletedAt
                      deletedBy{
                        login
                        __typename
                      }
                      diff
                    }
                  }
                  reactionGroups{
                    content
                    createdAt
                    users{
                      totalCount
                    }
                  }
                }

                ... on CommentDeletedEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  databaseId
                }

                ... on ConnectedEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  isCrossRepository
                  source{
                    __typename
                    ... on Issue{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                    ... on PullRequest{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                  }
                  subject{
                    __typename
                    ... on Issue{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                    ... on PullRequest{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                  }
                }

                ... on DisconnectedEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  isCrossRepository
                  source{
                    __typename
                    ... on Issue{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                    ... on PullRequest{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                  }
                  subject{
                    __typename
                    ... on Issue{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                    ... on PullRequest{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                  }
                }

                ... on CrossReferencedEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  referencedAt
                  resourcePath
                  url
                  isCrossRepository
                  willCloseTarget
                  source{
                    __typename
                    ... on Issue{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                    ... on PullRequest{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                  }
                  target{
                    __typename
                    ... on Issue{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                    ... on PullRequest{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                  }
                }

                ... on ReferencedEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  commit{
                    oid
                  }
                  commitRepository{
                    nameWithOwner
                  }
                  isCrossRepository
                  isDirectReference
                  subject{
                    __typename
                    ... on Issue{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                    ... on PullRequest{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                  }
                }

                ... on TransferredEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  fromRepository{
                    nameWithOwner
                  }
                  issue{
                    __typename
                    repository{
                      nameWithOwner
                    }
                    number
                  }
                }

                ... on LabeledEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  label{
                    name
                    createdAt
                    color
                    isDefault
                    description
                    repository{
                      nameWithOwner
                    }
                    resourcePath
                    url
                    updatedAt
                  }
                  labelable{
                    __typename
                    ... on Issue{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                    ... on PullRequest{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                  }
                }

                ... on UnlabeledEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  label{
                    name
                    createdAt
                    color
                    isDefault
                    description
                    repository{
                      nameWithOwner
                    }
                    resourcePath
                    url
                    updatedAt
                  }
                  labelable{
                    __typename
                    ... on Issue{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                    ... on PullRequest{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                  }
                }

                ... on MentionedEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  databaseId
                }

                ... on DemilestonedEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  milestoneTitle
                  subject{
                    __typename
                    ... on Issue{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                    ... on PullRequest{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                  }
                }

                ... on MilestonedEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  milestoneTitle
                  subject{
                    __typename
                    ... on Issue{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                    ... on PullRequest{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                  }
                }

                ... on ClosedEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  resourcePath
                  url
                  closable{
                    __typename
                    ... on Issue{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                    ... on PullRequest{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                  }
                  closer{
                    __typename
                    ... on Commit{
                      repository{
                        nameWithOwner
                      }
                      oid
                    }
                    ... on PullRequest{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                  }
                }

                ... on ReopenedEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  closable{
                    __typename
                    ... on Issue{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                    ... on PullRequest{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                  }
                }

                ... on LockedEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  lockReason
                  lockable{
                    __typename
                    ... on Issue{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                    ... on PullRequest{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                  }
                }

                ... on UnlockedEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  lockable{
                    __typename
                    ... on Issue{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                    ... on PullRequest{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                  }
                }

                ... on MarkedAsDuplicateEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                }

                ... on UnmarkedAsDuplicateEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                }

                ... on PinnedEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  issue{
                    __typename
                    repository{
                      nameWithOwner
                    }
                    number
                  }
                }

                ... on UnpinnedEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  issue{
                    __typename
                    repository{
                      nameWithOwner
                    }
                    number
                  }
                }

                ... on AddedToProjectEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  databaseId
                }

                ... on RemovedFromProjectEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  databaseId
                }

                ... on ConvertedNoteToIssueEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  databaseId
                }

                ... on MovedColumnsInProjectEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  databaseId
                }

                ... on SubscribedEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  subscribable{
                    ... on Issue{
                      __typename
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                    ... on PullRequest{
                      __typename
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                  }
                }

                ... on UnsubscribedEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  subscribable{
                    ... on Issue{
                      __typename
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                    ... on PullRequest{
                      __typename
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                  }
                }

                ... on RenamedTitleEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  currentTitle
                  previousTitle
                  subject{
                    ... on Issue{
                      __typename
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                    ... on PullRequest{
                      __typename
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                  }
                }

                ... on UserBlockedEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  blockDuration
                  subject{
                    login
                    __typename
                  }

                }

                ... on AutomaticBaseChangeFailedEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  newBase
                  oldBase
                  pullRequest{
                    __typename
                    repository{
                      nameWithOwner
                    }
                    number
                  }
                }

                ... on AutomaticBaseChangeSucceededEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  newBase
                  oldBase
                  pullRequest{
                    __typename
                    repository{
                      nameWithOwner
                    }
                    number
                  }
                }

                ... on BaseRefChangedEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  databaseId
                }

                ... on BaseRefForcePushedEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  ref{
                    name
                    prefix
                    target{
                      oid
                    }
                  }
                  beforeCommit{
                    oid
                  }
                  afterCommit{
                    oid
                  }
                  pullRequest{
                    __typename
                    repository{
                      nameWithOwner
                    }
                    number
                  }

                }

                ... on HeadRefDeletedEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  headRefName
                  headRef{
                    prefix
                    target{
                      oid
                    }
                  }
                  pullRequest{
                    __typename
                    repository{
                      nameWithOwner
                    }
                    number
                  }
                }

                ... on HeadRefForcePushedEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  ref{
                    name
                    prefix
                    target{
                      oid
                    }
                  }
                  beforeCommit{
                    oid
                  }
                  afterCommit{
                    oid
                  }
                  pullRequest{
                    __typename
                    repository{
                      nameWithOwner
                    }
                    number
                  }
                }

                ... on HeadRefRestoredEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  pullRequest{
                    __typename
                    repository{
                      nameWithOwner
                    }
                    number
                  }
                }

                ... on PullRequestCommit{
                  __typename
                  commit{
                    repository{
                      nameWithOwner
                    }
                    oid
                  }
                  pullRequest{
                    repository{
                      nameWithOwner
                    }
                    number
                  }
                }

                ... on PullRequestCommitCommentThread{
                  __typename
                  commit{
                    oid
                  }
                  path
                  position
                  pullRequest{
                    __typename
                    repository{
                      nameWithOwner
                    }
                    number
                  }
                  comments(first: 1){
                    totalCount
                  }
                }

                ... on ConvertToDraftEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  resourcePath
                  url
                  pullRequest{
                    __typename
                    repository{
                      nameWithOwner
                    }
                    number
                  }
                }

                ... on DeployedEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  databaseId
                  ref{
                    __typename
                    name
                    prefix
                    target{
                      oid
                    }
                  }
                  deployment{
                    creator{
                      login
                      __typename
                    }
                    createdAt
                    updatedAt
                    commitOid
                    task
                    databaseId
                    description
                    payload
                    environment
                    originalEnvironment
                    state
                  }
                  pullRequest{
                    __typename
                    repository{
                      nameWithOwner
                    }
                    number
                  }
                }

                ... on DeploymentEnvironmentChangedEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  deploymentStatus{
                    state
                    deployment{
                      creator{
                      login
                      __typename
                      }
                      createdAt
                      updatedAt
                      commitOid
                      task
                      databaseId
                      description
                      payload
                      environment
                      originalEnvironment
                      state
                    }
                  }
                  pullRequest{
                    __typename
                    repository{
                      nameWithOwner
                    }
                    number
                  }
                }

                ... on MergedEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  commit{
                    oid
                  }
                  resourcePath
                  url
                  mergeRefName
                  mergeRef{
                    __typename
                    prefix
                    target{
                      oid
                    }
                  }
                  pullRequest{
                    __typename
                    repository{
                      nameWithOwner
                    }
                    number
                  }
                }

                ... on PullRequestReview{
                  __typename
                  author{
                    login
                    __typename
                  }
                  authorAssociation
                  state
                  commit{
                    oid
                  }
                  createdAt
                  createdViaEmail
                  publishedAt
                  updatedAt
                  submittedAt
                  databaseId
                  resourcePath
                  url
                  body
                  bodyHTML
                  bodyText
                  editor{
                    login
                    __typename
                  }
                  includesCreatedEdit
                  lastEditedAt
                  userContentEdits(first: 50){
                    totalCount
                    pageInfo{
                      hasNextPage
                      endCursor
                    }
                    nodes{
                      editor{
                        login
                        __typename
                      }
                      createdAt
                      editedAt
                      updatedAt
                      deletedAt
                      deletedBy{
                        login
                        __typename
                      }
                      diff
                    }
                  }
                  reactionGroups{
                    content
                    createdAt
                    users{
                      totalCount
                    }
                  }
                  onBehalfOf(first:50){
                    totalCount
                    pageInfo{
                      hasNextPage
                      endCursor
                    }
                    nodes{
                      organization{
                        login
                      }
                      slug
                      combinedSlug
                      createdAt
                      updatedAt
                      databaseId
                      avatarUrl
                      resourcePath
                      url
                      name
                    }
                  }
                  comments(first:1){
                    totalCount
                  }
                  pullRequest{
                    __typename
                    repository{
                      nameWithOwner
                    }
                    number
                  }
                }

                ... on PullRequestReviewThread{
                  __typename
                  isResolved
                  line
                  startLine
                  originalLine
                  originalStartLine
                  resolvedBy{
                    login
                    __typename
                  }
                  diffSide
                  startDiffSide
                  comments(first: 1){
                    totalCount
                  }
                  pullRequest{
                    __typename
                    repository{
                      nameWithOwner
                    }
                    number
                  }
                }

                ... on ReadyForReviewEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  resourcePath
                  url
                  pullRequest{
                    __typename
                    repository{
                      nameWithOwner
                    }
                    number
                  }
                }

                ... on ReviewDismissedEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  databaseId
                  resourcePath
                  url
                  dismissalMessage
                  dismissalMessageHTML
                  previousReviewState
                  pullRequest{
                    __typename
                    repository{
                      nameWithOwner
                    }
                    number
                  }
                  pullRequestCommit{
                    commit{
                      oid
                    }
                  }
                  review{
                    author{
                      login
                    }
                    createdAt
                    body
                  }
                }

                ... on ReviewRequestedEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  requestedReviewer{
                    __typename
                    ... on Mannequin{
                      login
                    }
                    ... on Team{
                      organization{
                        login
                      }
                      slug
                      combinedSlug
                      createdAt
                      updatedAt
                      databaseId
                      avatarUrl
                      resourcePath
                      url
                      name
                    }
                    ... on User{
                      login
                    }
                  }
                  pullRequest{
                    __typename
                    repository{
                      nameWithOwner
                    }
                    number
                  }
                }

                ... on ReviewRequestRemovedEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  requestedReviewer{
                    ... on Mannequin{
                      login
                      __typename
                    }
                    ... on Team{
                      __typename
                      organization{
                        login
                      }
                      slug
                      combinedSlug
                      createdAt
                      updatedAt
                      databaseId
                      avatarUrl
                      resourcePath
                      url
                      name
                    }
                    ... on User{
                      login
                      __typename
                    }
                  }
                  pullRequest{
                    __typename
                    repository{
                      nameWithOwner
                    }
                    number
                  }
                } 
              }

            }
          }
        }
      }
    }
    """

    # ------------------------------------
    # Get the total count

    if get_remaining() > 1:
        result = run_query_variable(query_total_count, variables_total_count)
    else:
        sleep = sleep_in_seconds(get_reset())
        print("Need to sleep about {} minutes to reset the 5000 scores".format(str(sleep / 60)))
        time.sleep(sleep)
        print("Restart! :-)")
        result = run_query_variable(query_total_count, variables_total_count)

    # An exception: Cannot find repo "quantum9Innovation/Neural-Network-Frameworks" anymore
    if not result["data"]["repository"]:
        raise Exception("Cannot find repo {}/{} anymore!".
                        format(variables_total_count["owner"], variables_total_count["name"]))

    # ********************************
    # Check whether the owner or the name of the repository is changed
    # If the repository's owner or name name is changed, update the repository owner or name name in MongoDB database
    if result["data"]["repository"]["name"] != variables_total_count["name"] or \
            result["data"]["repository"]["owner"]["login"] != variables_total_count["owner"]:
        oldRepository = variables_total_count["owner"] + "/" + variables_total_count["name"]
        repo = Repo.objects(nameWithOwner=oldRepository).first()
        oldOwnerType = repo["ownerType"]
        newOwnerType = result["data"]["repository"]["owner"]["__typename"]
        if oldOwnerType != newOwnerType:
            raise Exception("The ownerType is different! old: {}, new: {}".format(oldOwnerType, newOwnerType))
        # Update the information of owner and name of a repository and its related documents
        newOwner = result["data"]["repository"]["owner"]["login"]
        newName = result["data"]["repository"]["name"]
        newRepository = newOwner + "/" + newName
        update_repo_name(oldRepository=oldRepository, newRepository=newRepository)
        variables_total_count["owner"] = newOwner
        variables_total_count["name"] = newName

    # ********************************

    # Get the total_count of timelineItems associated with the focal pullRequest
    total_count = result["data"]["repository"]["pullRequest"]["timelineItems"]["totalCount"]
    print("There are in total {} timeline items.".format(str(total_count)))

    if total_count == 0:
        print("------------------------------------------------------------")
        return

    # ------------------------------------
    # Traverse the list by skip function

    skip = 0

    variables_skip = {
        "owner": variables_total_count["owner"],
        "name": variables_total_count["name"],
        "number": variables_total_count["number"],
        "first": first,
        "skip": skip
    }

    while skip < total_count:
        hasNextPage, endCursor, edges = fetch_event_nodes(query=query_skip, variables=variables_skip)

        # If the query has an error, I set the edges as None;
        # Information about the errors is saved in the files at path_message and path_var
        if not edges:
            return

        events.extend(edges)
        skip = skip + first
        variables_skip["skip"] = skip

    # Note that there is no PullRequestRevisionMarker
    count = {
        "AssignedEvent": 0,
        "UnassignedEvent": 0,
        "IssueComment": 0,
        "CommentDeletedEvent": 0,
        "ConnectedEvent": 0,
        "DisconnectedEvent": 0,
        "CrossReferencedEvent": 0,
        "ReferencedEvent": 0,
        "TransferredEvent": 0,
        "LabeledEvent": 0,
        "UnlabeledEvent": 0,
        "MentionedEvent": 0,
        "MilestonedEvent": 0,
        "DemilestonedEvent": 0,
        "ClosedEvent": 0,
        "ReopenedEvent": 0,
        "LockedEvent": 0,
        "UnlockedEvent": 0,
        "PinnedEvent": 0,
        "UnpinnedEvent": 0,
        "MarkedAsDuplicateEvent": 0,
        "UnmarkedAsDuplicateEvent": 0,
        "AddedToProjectEvent": 0,
        "RemovedFromProjectEvent": 0,
        "MovedColumnsInProjectEvent": 0,
        "ConvertedNoteToIssueEvent": 0,
        "SubscribedEvent": 0,
        "UnsubscribedEvent": 0,
        "RenamedTitleEvent": 0,
        "UserBlockedEvent": 0,
        # From here, PR only events
        "AutomaticBaseChangeFailedEvent": 0,
        "AutomaticBaseChangeSucceededEvent": 0,
        "BaseRefChangedEvent": 0,
        "BaseRefForcePushedEvent": 0,
        "HeadRefDeletedEvent": 0,
        "HeadRefForcePushedEvent": 0,
        "HeadRefRestoredEvent": 0,
        "PullRequestCommit": 0,
        "PullRequestCommitCommentThread": 0,
        "ConvertToDraftEvent": 0,
        "DeployedEvent": 0,
        "DeploymentEnvironmentChangedEvent": 0,
        "MergedEvent": 0,
        "PullRequestReview": 0,
        "PullRequestReviewThread": 0,
        "ReadyForReviewEvent": 0,
        "ReviewDismissedEvent": 0,
        "ReviewRequestedEvent": 0,
        "ReviewRequestRemovedEvent": 0
    }

    # We use skip instead of beforeEventCursor to reach a specific timelineItem in the list
    # because skip seems much more stable.
    skip = 0

    repository = variables_total_count["owner"] + "/" + variables_total_count["name"]
    number = variables_total_count["number"]

    for i in range(0, len(events)):
        if not events[i]["node"]:
            continue
        eventType = events[i]["node"]["__typename"]
        event = events[i]["node"]
        # Save a document of the event in MongoDB
        if eventType == "AssignedEvent":
            timelineItem = save_assigned_event(event)
        elif eventType == "UnassignedEvent":
            timelineItem = save_unassigned_event(event)
        elif eventType == "IssueComment":
            timelineItem = save_issue_comment(event)
        elif eventType == "CommentDeletedEvent":
            timelineItem = save_comment_deleted_event(event, variables_total_count)
        elif eventType == "ConnectedEvent":
            timelineItem = save_connected_event(event)
        elif eventType == "DisconnectedEvent":
            timelineItem = save_disconnected_event(event)
        elif eventType == "CrossReferencedEvent":
            timelineItem = save_cross_referenced_event(event)
        elif eventType == "ReferencedEvent":
            timelineItem = save_referenced_event(event)
        elif eventType == "TransferredEvent":
            timelineItem = save_transferred_event(event)
        elif eventType == "LabeledEvent":
            timelineItem = save_labeled_event(event)
        elif eventType == "UnlabeledEvent":
            timelineItem = save_unlabeled_event(event)
        elif eventType == "MentionedEvent":
            timelineItem = save_mentioned_event(event, variables_total_count)
        elif eventType == "MilestonedEvent":
            timelineItem = save_milestoned_event(event)
        elif eventType == "DemilestonedEvent":
            timelineItem = save_demilestoned_event(event)
        elif eventType == "ClosedEvent":
            timelineItem = save_closed_event(event)
        elif eventType == "ReopenedEvent":
            timelineItem = save_reopened_event(event)
        elif eventType == "LockedEvent":
            timelineItem = save_locked_event(event)
        elif eventType == "UnlockedEvent":
            timelineItem = save_unlocked_event(event)
        elif eventType == "PinnedEvent":
            timelineItem = save_pinned_event(event)
        elif eventType == "UnpinnedEvent":
            timelineItem = save_unpinned_event(event)
        elif eventType == "MarkedAsDuplicateEvent":
            timelineItem = save_marked_as_duplicate_event(event, variables_total_count)
        elif eventType == "UnmarkedAsDuplicateEvent":
            timelineItem = save_unmarked_as_duplicate_event(event, variables_total_count)
        elif eventType == "AddedToProjectEvent":
            timelineItem = save_added_to_project_event(event, variables_total_count)
        elif eventType == "RemovedFromProjectEvent":
            timelineItem = save_removed_from_project_event(event, variables_total_count)
        elif eventType == "MovedColumnsInProjectEvent":
            timelineItem = save_moved_columns_in_project_event(event, variables_total_count)
        elif eventType == "ConvertedNoteToIssueEvent":
            timelineItem = save_converted_note_to_issue_event(event, variables_total_count)
        elif eventType == "SubscribedEvent":
            timelineItem = save_subscribed_event(event)
        elif eventType == "UnsubscribedEvent":
            timelineItem = save_unsubscribed_event(event)
        elif eventType == "RenamedTitleEvent":
            timelineItem = save_renamed_title_event(event)
        elif eventType == "UserBlockedEvent":
            timelineItem = save_user_blocked_event(event, variables_total_count)
        # From here: PR-only events
        elif eventType == "AutomaticBaseChangeFailedEvent":
            timelineItem = save_automatic_base_change_failed_event(event)
        elif eventType == "AutomaticBaseChangeSucceededEvent":
            timelineItem = save_automatic_base_change_succeeded_event(event)
        elif eventType == "BaseRefChangedEvent":
            timelineItem = save_baseRef_changed_event(event, variables_total_count)
        elif eventType == "BaseRefForcePushedEvent":
            timelineItem = save_baseRef_force_pushed_event(event)
        elif eventType == "HeadRefDeletedEvent":
            timelineItem = save_headRef_deleted_event(event)
        elif eventType == "HeadRefForcePushedEvent":
            timelineItem = save_headRef_force_pushed_event(event)
        elif eventType == "HeadRefRestoredEvent":
            timelineItem = save_headRef_restored_event(event)
        elif eventType == "PullRequestCommit":
            timelineItem = save_pr_commit(event)
        elif eventType == "PullRequestCommitCommentThread":
            timelineItem = save_pr_commit_comment_thread(event, variables_total_count, skip)
        elif eventType == "ConvertToDraftEvent":
            timelineItem = save_convert_to_draft_event(event)
        elif eventType == "DeployedEvent":
            timelineItem = save_deployed_event(event)
        elif eventType == "DeploymentEnvironmentChangedEvent":
            timelineItem = save_deployment_environment_changed_event(event)
        elif eventType == "MergedEvent":
            timelineItem = save_merged_event(event)
        elif eventType == "PullRequestReview":
            timelineItem = save_pr_review(event, variables_total_count, skip)
        elif eventType == "PullRequestReviewThread":
            timelineItem = save_pr_review_thread(event, variables_total_count, skip)
        elif eventType == "ReadyForReviewEvent":
            timelineItem = save_ready_for_review_event(event)
        elif eventType == "ReviewDismissedEvent":
            timelineItem = save_review_dismissed_event(event)
        elif eventType == "ReviewRequestedEvent":
            timelineItem = save_review_requested_event(event)
        elif eventType == "ReviewRequestRemovedEvent":
            timelineItem = save_review_request_removed_event(event)
        else:
            raise Exception("{} is an unexpected event type of pullRequest timeline items".format(eventType))

        # Save the timelineItem in the focal pullRequest
        num_updated = PullRequest.objects(repository=repository, number=number).update(push__timeline=timelineItem)
        if num_updated != 1:
            raise Exception(
                "No pullRequest with number {} in repo {} -- MongoDB database".format(str(number), repository))

        count[eventType] = count[eventType] + 1
        skip = skip + 1

    print("------------------------------------------------------------")
    print("{} events are added to the timeline of pullRequest #{} in repo {}/{} -- MongoDB database".
          format(str(len(events)), variables_total_count["number"],
                 variables_total_count["owner"], variables_total_count["name"]))
    for key in count:
        if count[key] != 0:
            print("  --> {}: {} added".format(key, count[key]))
    print("------------------------------------------------------------")
    # ------------------------------


def fetch_with_pagination(variables_total_count):
    """
    Use pagination to traverse the list of timelineItems associated with a pullRequest
    :param variables_total_count: A dictionary for information of the focal pullRequest and the associated repository
    :return: No return. The events and timeline information saved in MongoDB
    """
    events = []

    # Get nodes of timelineItems associated with the specific issue
    query_total_count = """
        query($owner: String!, $name: String!, $number: Int!) {
          repository(owner: $owner, name: $name){
            pullRequest(number: $number){
              timelineItems(first: 1){
                totalCount
              }
            }
          }
        }
        """

    query_first_page = """
        query($owner: String!, $name: String!, $number: Int!, $first: Int!) {
          rateLimit{
            cost
            remaining
          }
          repository(owner: $owner, name: $name){
            pullRequest(number: $number){
              timelineItems(first: $first){
                totalCount
                pageInfo{
                  hasNextPage
                  endCursor
                }
                edges{
                  cursor
                  node{

                    ... on AssignedEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt

                      assignee{
                        ... on User{
                          login
                          __typename
                        }
                        ... on Bot{
                          login
                          __typename
                        }
                        ... on Organization{
                          login
                          __typename
                        }
                        ... on Mannequin{
                          login
                          __typename
                        }
                      }

                      assignable{
                        __typename
                        ... on PullRequest{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                      }
                    }

                    ... on UnassignedEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt

                      assignee{
                        ... on User{
                          login
                          __typename
                        }
                        ... on Bot{
                          login
                          __typename
                        }
                        ... on Organization{
                          login
                          __typename
                        }
                        ... on Mannequin{
                          login
                          __typename
                        }
                      }

                      assignable{
                        __typename
                        ... on PullRequest{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                      } 
                    }

                    ... on IssueComment{
                      __typename
                      author{
                        login
                        __typename
                      }
                      authorAssociation
                      createdAt
                      createdViaEmail
                      publishedAt
                      updatedAt
                      databaseId
                      resourcePath
                      url
                      pullRequest{
                        __typename
                        repository{
                          nameWithOwner
                        }
                        number
                      }
                      isMinimized
                      minimizedReason
                      body
                      bodyHTML
                      bodyText
                      editor{
                        login
                        __typename
                      }
                      includesCreatedEdit
                      lastEditedAt
                      userContentEdits(first:50){
                        totalCount
                        nodes{
                          editor{
                            login
                            __typename
                          }
                          createdAt
                          editedAt
                          updatedAt
                          deletedAt
                          deletedBy{
                            login
                            __typename
                          }
                          diff
                        }
                      }
                      reactionGroups{
                        content
                        createdAt
                        users{
                          totalCount
                        }
                      }
                    }

                    ... on CommentDeletedEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      databaseId
                    }

                    ... on ConnectedEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      isCrossRepository
                      source{
                        __typename
                        ... on Issue{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                        ... on PullRequest{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                      }
                      subject{
                        __typename
                        ... on Issue{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                        ... on PullRequest{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                      }
                    }

                    ... on DisconnectedEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      isCrossRepository
                      source{
                        __typename
                        ... on Issue{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                        ... on PullRequest{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                      }
                      subject{
                        __typename
                        ... on Issue{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                        ... on PullRequest{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                      }
                    }

                    ... on CrossReferencedEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      referencedAt
                      resourcePath
                      url
                      isCrossRepository
                      willCloseTarget
                      source{
                        __typename
                        ... on Issue{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                        ... on PullRequest{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                      }
                      target{
                        __typename
                        ... on Issue{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                        ... on PullRequest{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                      }
                    }

                    ... on ReferencedEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      commit{
                        oid
                      }
                      commitRepository{
                        nameWithOwner
                      }
                      isCrossRepository
                      isDirectReference
                      subject{
                        __typename
                        ... on Issue{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                        ... on PullRequest{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                      }
                    }

                    ... on TransferredEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      fromRepository{
                        nameWithOwner
                      }
                      issue{
                        __typename
                        repository{
                          nameWithOwner
                        }
                        number
                      }
                    }

                    ... on LabeledEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      label{
                        name
                        createdAt
                        color
                        isDefault
                        description
                        repository{
                          nameWithOwner
                        }
                        resourcePath
                        url
                        updatedAt
                      }
                      labelable{
                        __typename
                        ... on Issue{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                        ... on PullRequest{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                      }
                    }

                    ... on UnlabeledEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      label{
                        name
                        createdAt
                        color
                        isDefault
                        description
                        repository{
                          nameWithOwner
                        }
                        resourcePath
                        url
                        updatedAt
                      }
                      labelable{
                        __typename
                        ... on Issue{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                        ... on PullRequest{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                      }
                    }

                    ... on MentionedEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      databaseId
                    }

                    ... on DemilestonedEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      milestoneTitle
                      subject{
                        __typename
                        ... on Issue{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                        ... on PullRequest{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                      }
                    }

                    ... on MilestonedEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      milestoneTitle
                      subject{
                        __typename
                        ... on Issue{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                        ... on PullRequest{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                      }
                    }

                    ... on ClosedEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      resourcePath
                      url
                      closable{
                        __typename
                        ... on Issue{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                        ... on PullRequest{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                      }
                      closer{
                        __typename
                        ... on Commit{
                          repository{
                            nameWithOwner
                          }
                          oid
                        }
                        ... on PullRequest{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                      }
                    }

                    ... on ReopenedEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      closable{
                        __typename
                        ... on Issue{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                        ... on PullRequest{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                      }
                    }

                    ... on LockedEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      lockReason
                      lockable{
                        __typename
                        ... on Issue{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                        ... on PullRequest{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                      }
                    }

                    ... on UnlockedEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      lockable{
                        __typename
                        ... on Issue{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                        ... on PullRequest{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                      }
                    }

                    ... on MarkedAsDuplicateEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                    }

                    ... on UnmarkedAsDuplicateEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                    }

                    ... on PinnedEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      issue{
                        __typename
                        repository{
                          nameWithOwner
                        }
                        number
                      }
                    }

                    ... on UnpinnedEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      issue{
                        __typename
                        repository{
                          nameWithOwner
                        }
                        number
                      }
                    }

                    ... on AddedToProjectEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      databaseId
                    }

                    ... on RemovedFromProjectEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      databaseId
                    }

                    ... on ConvertedNoteToIssueEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      databaseId
                    }

                    ... on MovedColumnsInProjectEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      databaseId
                    }

                    ... on SubscribedEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      subscribable{
                        ... on Issue{
                          __typename
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                        ... on PullRequest{
                          __typename
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                      }
                    }

                    ... on UnsubscribedEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      subscribable{
                        ... on Issue{
                          __typename
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                        ... on PullRequest{
                          __typename
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                      }
                    }

                    ... on RenamedTitleEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      currentTitle
                      previousTitle
                      subject{
                        ... on Issue{
                          __typename
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                        ... on PullRequest{
                          __typename
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                      }
                    }

                    ... on UserBlockedEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      blockDuration
                      subject{
                        login
                        __typename
                      }

                    }

                    ... on AutomaticBaseChangeFailedEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      newBase
                      oldBase
                      pullRequest{
                        __typename
                        repository{
                          nameWithOwner
                        }
                        number
                      }
                    }

                    ... on AutomaticBaseChangeSucceededEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      newBase
                      oldBase
                      pullRequest{
                        __typename
                        repository{
                          nameWithOwner
                        }
                        number
                      }
                    }

                    ... on BaseRefChangedEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      databaseId
                    }

                    ... on BaseRefForcePushedEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      ref{
                        name
                        prefix
                        target{
                          oid
                        }
                      }
                      beforeCommit{
                        oid
                      }
                      afterCommit{
                        oid
                      }
                      pullRequest{
                        __typename
                        repository{
                          nameWithOwner
                        }
                        number
                      }

                    }

                    ... on HeadRefDeletedEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      headRefName
                      headRef{
                        prefix
                        target{
                          oid
                        }
                      }
                      pullRequest{
                        __typename
                        repository{
                          nameWithOwner
                        }
                        number
                      }
                    }

                    ... on HeadRefForcePushedEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      ref{
                        name
                        prefix
                        target{
                          oid
                        }
                      }
                      beforeCommit{
                        oid
                      }
                      afterCommit{
                        oid
                      }
                      pullRequest{
                        __typename
                        repository{
                          nameWithOwner
                        }
                        number
                      }
                    }

                    ... on HeadRefRestoredEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      pullRequest{
                        __typename
                        repository{
                          nameWithOwner
                        }
                        number
                      }
                    }

                    ... on PullRequestCommit{
                      __typename
                      commit{
                        repository{
                          nameWithOwner
                        }
                        oid
                      }
                      pullRequest{
                      repository{
                        nameWithOwner
                      }
                        number
                      }
                    }

                    ... on PullRequestCommitCommentThread{
                      __typename
                      commit{
                        oid
                      }
                      path
                      position
                      pullRequest{
                        __typename
                        repository{
                          nameWithOwner
                        }
                        number
                      }
                      comments(first: 1){
                        totalCount
                      }
                    }

                    ... on ConvertToDraftEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      resourcePath
                      url
                      pullRequest{
                        __typename
                        repository{
                          nameWithOwner
                        }
                        number
                      }
                    }

                    ... on DeployedEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      databaseId
                      ref{
                        __typename
                        name
                        prefix
                        target{
                          oid
                        }
                      }
                      deployment{
                        creator{
                          login
                          __typename
                        }
                        createdAt
                        updatedAt
                        commitOid
                        task
                        databaseId
                        description
                        payload
                        environment
                        originalEnvironment
                        state
                      }
                      pullRequest{
                        __typename
                        repository{
                          nameWithOwner
                        }
                        number
                      }
                    }

                    ... on DeploymentEnvironmentChangedEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      deploymentStatus{
                        state
                        deployment{
                          creator{
                          login
                          __typename
                          }
                          createdAt
                          updatedAt
                          commitOid
                          task
                          databaseId
                          description
                          payload
                          environment
                          originalEnvironment
                          state
                        }
                      }
                      pullRequest{
                        __typename
                        repository{
                          nameWithOwner
                        }
                        number
                      }
                    }

                    ... on MergedEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      commit{
                        oid
                      }
                      resourcePath
                      url
                      mergeRefName
                      mergeRef{
                        __typename
                        prefix
                        target{
                          oid
                        }
                      }
                      pullRequest{
                        __typename
                        repository{
                          nameWithOwner
                        }
                        number
                      }
                    }

                    ... on PullRequestReview{
                      __typename
                      author{
                        login
                        __typename
                      }
                      authorAssociation
                      state
                      commit{
                        oid
                      }
                      createdAt
                      createdViaEmail
                      publishedAt
                      updatedAt
                      submittedAt
                      databaseId
                      resourcePath
                      url
                      body
                      bodyHTML
                      bodyText
                      editor{
                        login
                        __typename
                      }
                      includesCreatedEdit
                      lastEditedAt
                      userContentEdits(first: 50){
                        totalCount
                        pageInfo{
                          hasNextPage
                          endCursor
                        }
                        nodes{
                          editor{
                            login
                            __typename
                          }
                          createdAt
                          editedAt
                          updatedAt
                          deletedAt
                          deletedBy{
                            login
                            __typename
                          }
                          diff
                        }
                      }
                      reactionGroups{
                        content
                        createdAt
                        users{
                          totalCount
                        }
                      }
                      onBehalfOf(first:50){
                        totalCount
                        pageInfo{
                          hasNextPage
                          endCursor
                        }
                        nodes{
                          organization{
                            login
                          }
                          slug
                          combinedSlug
                          createdAt
                          updatedAt
                          databaseId
                          avatarUrl
                          resourcePath
                          url
                          name
                        }
                      }
                      comments(first:1){
                        totalCount
                      }
                      pullRequest{
                        __typename
                        repository{
                          nameWithOwner
                        }
                        number
                      }
                    }

                    ... on PullRequestReviewThread{
                      __typename
                      isResolved
                      line
                      startLine
                      originalLine
                      originalStartLine
                      resolvedBy{
                        login
                        __typename
                      }
                      diffSide
                      startDiffSide
                      comments(first: 1){
                        totalCount
                      }
                      pullRequest{
                        __typename
                        repository{
                          nameWithOwner
                        }
                        number
                      }
                    }

                    ... on ReadyForReviewEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      resourcePath
                      url
                      pullRequest{
                        __typename
                        repository{
                          nameWithOwner
                        }
                        number
                      }
                    }

                    ... on ReviewDismissedEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      databaseId
                      resourcePath
                      url
                      dismissalMessage
                      dismissalMessageHTML
                      previousReviewState
                      pullRequest{
                        __typename
                        repository{
                          nameWithOwner
                        }
                        number
                      }
                      pullRequestCommit{
                        commit{
                          oid
                        }
                      }
                      review{
                        author{
                          login
                        }
                        createdAt
                        body
                      }
                    }

                    ... on ReviewRequestedEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      requestedReviewer{
                        __typename
                        ... on Mannequin{
                          login
                        }
                        ... on Team{
                          organization{
                            login
                          }
                          slug
                          combinedSlug
                          createdAt
                          updatedAt
                          databaseId
                          avatarUrl
                          resourcePath
                          url
                          name
                        }
                        ... on User{
                          login
                        }
                      }
                      pullRequest{
                        __typename
                        repository{
                          nameWithOwner
                        }
                        number
                      }
                    }

                    ... on ReviewRequestRemovedEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      requestedReviewer{
                        ... on Mannequin{
                          login
                          __typename
                        }
                        ... on Team{
                          __typename
                          organization{
                            login
                          }
                          slug
                          combinedSlug
                          createdAt
                          updatedAt
                          databaseId
                          avatarUrl
                          resourcePath
                          url
                          name
                        }
                        ... on User{
                          login
                          __typename
                        }
                      }
                      pullRequest{
                        __typename
                        repository{
                          nameWithOwner
                        }
                        number
                      }
                    } 
                  }

                }
              }
            }
          }
        }
        """

    query_next_page = """
        query($owner: String!, $name: String!, $number: Int!, $first: Int!, $after_cursor: String!) {
          rateLimit{
            cost
            remaining
          }
          repository(owner: $owner, name: $name){
            pullRequest(number: $number){
              timelineItems(first: $first, after: $after_cursor){
                totalCount
                pageInfo{
                  hasNextPage
                  endCursor
                }
                edges{
                  cursor
                  node{

                    ... on AssignedEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt

                      assignee{
                        ... on User{
                          login
                          __typename
                        }
                        ... on Bot{
                          login
                          __typename
                        }
                        ... on Organization{
                          login
                          __typename
                        }
                        ... on Mannequin{
                          login
                          __typename
                        }
                      }

                      assignable{
                        __typename
                        ... on PullRequest{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                      }
                    }

                    ... on UnassignedEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt

                      assignee{
                        ... on User{
                          login
                          __typename
                        }
                        ... on Bot{
                          login
                          __typename
                        }
                        ... on Organization{
                          login
                          __typename
                        }
                        ... on Mannequin{
                          login
                          __typename
                        }
                      }

                      assignable{
                        __typename
                        ... on PullRequest{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                      } 
                    }

                    ... on IssueComment{
                      __typename
                      author{
                        login
                        __typename
                      }
                      authorAssociation
                      createdAt
                      createdViaEmail
                      publishedAt
                      updatedAt
                      databaseId
                      resourcePath
                      url
                      pullRequest{
                        __typename
                        repository{
                          nameWithOwner
                        }
                        number
                      }
                      isMinimized
                      minimizedReason
                      body
                      bodyHTML
                      bodyText
                      editor{
                        login
                        __typename
                      }
                      includesCreatedEdit
                      lastEditedAt
                      userContentEdits(first:50){
                        totalCount
                        nodes{
                          editor{
                            login
                            __typename
                          }
                          createdAt
                          editedAt
                          updatedAt
                          deletedAt
                          deletedBy{
                            login
                            __typename
                          }
                          diff
                        }
                      }
                      reactionGroups{
                        content
                        createdAt
                        users{
                          totalCount
                        }
                      }
                    }

                    ... on CommentDeletedEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      databaseId
                    }

                    ... on ConnectedEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      isCrossRepository
                      source{
                        __typename
                        ... on Issue{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                        ... on PullRequest{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                      }
                      subject{
                        __typename
                        ... on Issue{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                        ... on PullRequest{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                      }
                    }

                    ... on DisconnectedEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      isCrossRepository
                      source{
                        __typename
                        ... on Issue{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                        ... on PullRequest{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                      }
                      subject{
                        __typename
                        ... on Issue{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                        ... on PullRequest{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                      }
                    }

                    ... on CrossReferencedEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      referencedAt
                      resourcePath
                      url
                      isCrossRepository
                      willCloseTarget
                      source{
                        __typename
                        ... on Issue{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                        ... on PullRequest{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                      }
                      target{
                        __typename
                        ... on Issue{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                        ... on PullRequest{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                      }
                    }

                    ... on ReferencedEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      commit{
                        oid
                      }
                      commitRepository{
                        nameWithOwner
                      }
                      isCrossRepository
                      isDirectReference
                      subject{
                        __typename
                        ... on Issue{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                        ... on PullRequest{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                      }
                    }

                    ... on TransferredEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      fromRepository{
                        nameWithOwner
                      }
                      issue{
                        __typename
                        repository{
                          nameWithOwner
                        }
                        number
                      }
                    }

                    ... on LabeledEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      label{
                        name
                        createdAt
                        color
                        isDefault
                        description
                        repository{
                          nameWithOwner
                        }
                        resourcePath
                        url
                        updatedAt
                      }
                      labelable{
                        __typename
                        ... on Issue{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                        ... on PullRequest{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                      }
                    }

                    ... on UnlabeledEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      label{
                        name
                        createdAt
                        color
                        isDefault
                        description
                        repository{
                          nameWithOwner
                        }
                        resourcePath
                        url
                        updatedAt
                      }
                      labelable{
                        __typename
                        ... on Issue{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                        ... on PullRequest{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                      }
                    }

                    ... on MentionedEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      databaseId
                    }

                    ... on DemilestonedEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      milestoneTitle
                      subject{
                        __typename
                        ... on Issue{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                        ... on PullRequest{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                      }
                    }

                    ... on MilestonedEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      milestoneTitle
                      subject{
                        __typename
                        ... on Issue{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                        ... on PullRequest{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                      }
                    }

                    ... on ClosedEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      resourcePath
                      url
                      closable{
                        __typename
                        ... on Issue{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                        ... on PullRequest{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                      }
                      closer{
                        __typename
                        ... on Commit{
                          repository{
                            nameWithOwner
                          }
                          oid
                        }
                        ... on PullRequest{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                      }
                    }

                    ... on ReopenedEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      closable{
                        __typename
                        ... on Issue{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                        ... on PullRequest{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                      }
                    }

                    ... on LockedEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      lockReason
                      lockable{
                        __typename
                        ... on Issue{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                        ... on PullRequest{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                      }
                    }

                    ... on UnlockedEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      lockable{
                        __typename
                        ... on Issue{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                        ... on PullRequest{
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                      }
                    }

                    ... on MarkedAsDuplicateEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                    }

                    ... on UnmarkedAsDuplicateEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                    }

                    ... on PinnedEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      issue{
                        __typename
                        repository{
                          nameWithOwner
                        }
                        number
                      }
                    }

                    ... on UnpinnedEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      issue{
                        __typename
                        repository{
                          nameWithOwner
                        }
                        number
                      }
                    }

                    ... on AddedToProjectEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      databaseId
                    }

                    ... on RemovedFromProjectEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      databaseId
                    }

                    ... on ConvertedNoteToIssueEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      databaseId
                    }

                    ... on MovedColumnsInProjectEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      databaseId
                    }

                    ... on SubscribedEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      subscribable{
                        ... on Issue{
                          __typename
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                        ... on PullRequest{
                          __typename
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                      }
                    }

                    ... on UnsubscribedEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      subscribable{
                        ... on Issue{
                          __typename
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                        ... on PullRequest{
                          __typename
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                      }
                    }

                    ... on RenamedTitleEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      currentTitle
                      previousTitle
                      subject{
                        ... on Issue{
                          __typename
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                        ... on PullRequest{
                          __typename
                          repository{
                            nameWithOwner
                          }
                          number
                        }
                      }
                    }

                    ... on UserBlockedEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      blockDuration
                      subject{
                        login
                        __typename
                      }

                    }

                    ... on AutomaticBaseChangeFailedEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      newBase
                      oldBase
                      pullRequest{
                        __typename
                        repository{
                          nameWithOwner
                        }
                        number
                      }
                    }

                    ... on AutomaticBaseChangeSucceededEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      newBase
                      oldBase
                      pullRequest{
                        __typename
                        repository{
                          nameWithOwner
                        }
                        number
                      }
                    }

                    ... on BaseRefChangedEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      databaseId
                    }

                    ... on BaseRefForcePushedEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      ref{
                        name
                        prefix
                        target{
                          oid
                        }
                      }
                      beforeCommit{
                        oid
                      }
                      afterCommit{
                        oid
                      }
                      pullRequest{
                        __typename
                        repository{
                          nameWithOwner
                        }
                        number
                      }

                    }

                    ... on HeadRefDeletedEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      headRefName
                      headRef{
                        prefix
                        target{
                          oid
                        }
                      }
                      pullRequest{
                        __typename
                        repository{
                          nameWithOwner
                        }
                        number
                      }
                    }

                    ... on HeadRefForcePushedEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      ref{
                        name
                        prefix
                        target{
                          oid
                        }
                      }
                      beforeCommit{
                        oid
                      }
                      afterCommit{
                        oid
                      }
                      pullRequest{
                        __typename
                        repository{
                          nameWithOwner
                        }
                        number
                      }
                    }

                    ... on HeadRefRestoredEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      pullRequest{
                        __typename
                        repository{
                          nameWithOwner
                        }
                        number
                      }
                    }

                    ... on PullRequestCommit{
                      __typename
                      commit{
                        repository{
                          nameWithOwner
                        }
                        oid
                      }
                      pullRequest{
                        repository{
                          nameWithOwner
                        }
                        number
                      }
                    }

                    ... on PullRequestCommitCommentThread{
                      __typename
                      commit{
                        oid
                      }
                      path
                      position
                      pullRequest{
                        __typename
                        repository{
                          nameWithOwner
                        }
                        number
                      }
                      comments(first: 1){
                        totalCount
                      }
                    }

                    ... on ConvertToDraftEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      resourcePath
                      url
                      pullRequest{
                        __typename
                        repository{
                          nameWithOwner
                        }
                        number
                      }
                    }

                    ... on DeployedEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      databaseId
                      ref{
                        __typename
                        name
                        prefix
                        target{
                          oid
                        }
                      }
                      deployment{
                        creator{
                          login
                          __typename
                        }
                        createdAt
                        updatedAt
                        commitOid
                        task
                        databaseId
                        description
                        payload
                        environment
                        originalEnvironment
                        state
                      }
                      pullRequest{
                        __typename
                        repository{
                          nameWithOwner
                        }
                        number
                      }
                    }

                    ... on DeploymentEnvironmentChangedEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      deploymentStatus{
                        state
                        deployment{
                          creator{
                          login
                          __typename
                          }
                          createdAt
                          updatedAt
                          commitOid
                          task
                          databaseId
                          description
                          payload
                          environment
                          originalEnvironment
                          state
                        }
                      }
                      pullRequest{
                        __typename
                        repository{
                          nameWithOwner
                        }
                        number
                      }
                    }

                    ... on MergedEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      commit{
                        oid
                      }
                      resourcePath
                      url
                      mergeRefName
                      mergeRef{
                        __typename
                        prefix
                        target{
                          oid
                        }
                      }
                      pullRequest{
                        __typename
                        repository{
                          nameWithOwner
                        }
                        number
                      }
                    }

                    ... on PullRequestReview{
                      __typename
                      author{
                        login
                        __typename
                      }
                      authorAssociation
                      state
                      commit{
                        oid
                      }
                      createdAt
                      createdViaEmail
                      publishedAt
                      updatedAt
                      submittedAt
                      databaseId
                      resourcePath
                      url
                      body
                      bodyHTML
                      bodyText
                      editor{
                        login
                        __typename
                      }
                      includesCreatedEdit
                      lastEditedAt
                      userContentEdits(first: 50){
                        totalCount
                        pageInfo{
                          hasNextPage
                          endCursor
                        }
                        nodes{
                          editor{
                            login
                            __typename
                          }
                          createdAt
                          editedAt
                          updatedAt
                          deletedAt
                          deletedBy{
                            login
                            __typename
                          }
                          diff
                        }
                      }
                      reactionGroups{
                        content
                        createdAt
                        users{
                          totalCount
                        }
                      }
                      onBehalfOf(first:50){
                        totalCount
                        pageInfo{
                          hasNextPage
                          endCursor
                        }
                        nodes{
                          organization{
                            login
                          }
                          slug
                          combinedSlug
                          createdAt
                          updatedAt
                          databaseId
                          avatarUrl
                          resourcePath
                          url
                          name
                        }
                      }
                      comments(first:1){
                        totalCount
                      }
                      pullRequest{
                        __typename
                        repository{
                          nameWithOwner
                        }
                        number
                      }
                    }

                    ... on PullRequestReviewThread{
                      __typename
                      isResolved
                      line
                      startLine
                      originalLine
                      originalStartLine
                      resolvedBy{
                        login
                        __typename
                      }
                      diffSide
                      startDiffSide
                      comments(first:1){
                        totalCount
                      }
                      pullRequest{
                        __typename
                        repository{
                          nameWithOwner
                        }
                        number
                      }
                    }

                    ... on ReadyForReviewEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      resourcePath
                      url
                      pullRequest{
                        __typename
                        repository{
                          nameWithOwner
                        }
                        number
                      }
                    }

                    ... on ReviewDismissedEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      databaseId
                      resourcePath
                      url
                      dismissalMessage
                      dismissalMessageHTML
                      previousReviewState
                      pullRequest{
                        __typename
                        repository{
                          nameWithOwner
                        }
                        number
                      }
                      pullRequestCommit{
                        commit{
                          oid
                        }
                      }
                      review{
                        author{
                          login
                        }
                        createdAt
                        body
                      }
                    }

                    ... on ReviewRequestedEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      requestedReviewer{
                        __typename
                        ... on Mannequin{
                          login
                        }
                        ... on Team{
                          organization{
                            login
                          }
                          slug
                          combinedSlug
                          createdAt
                          updatedAt
                          databaseId
                          avatarUrl
                          resourcePath
                          url
                          name
                        }
                        ... on User{
                          login
                        }
                      }
                      pullRequest{
                        __typename
                        repository{
                          nameWithOwner
                        }
                        number
                      }
                    }

                    ... on ReviewRequestRemovedEvent{
                      __typename
                      actor{
                        login
                        __typename
                      }
                      createdAt
                      requestedReviewer{
                        ... on Mannequin{
                          login
                          __typename
                        }
                        ... on Team{
                          __typename
                          organization{
                            login
                          }
                          slug
                          combinedSlug
                          createdAt
                          updatedAt
                          databaseId
                          avatarUrl
                          resourcePath
                          url
                          name
                        }
                        ... on User{
                          login
                          __typename
                        }
                      }
                      pullRequest{
                        __typename
                        repository{
                          nameWithOwner
                        }
                        number
                      }
                    } 
                  }

                }
              }
            }
          }
        }
        """

    # ------------------------------------
    # Get the total count

    if get_remaining() > 1:
        result = run_query_variable(query_total_count, variables_total_count)
    else:
        sleep = sleep_in_seconds(get_reset())
        print("Need to sleep about {} minutes to reset the 5000 scores".format(str(sleep / 60)))
        time.sleep(sleep)
        print("Restart! :-)")
        result = run_query_variable(query_total_count, variables_total_count)

    # An exception: Cannot find repo "quantum9Innovation/Neural-Network-Frameworks" anymore
    if not result["data"]["repository"]:
        raise Exception("Cannot find repo {}/{} anymore!".
                        format(variables_total_count["owner"], variables_total_count["name"]))

    total_count = result["data"]["repository"]["pullRequest"]["timelineItems"]["totalCount"]
    print("There are in total {} timeline items.".format(str(total_count)))

    if total_count == 0:
        print("------------------------------------------------------------")
        return

    # ------------------------------------
    # Traverse the list by pagination

    page = 1
    variables_first_page = {
        "owner": variables_total_count["owner"],
        "name": variables_total_count["name"],
        "number": variables_total_count["number"],
        "first": first
    }
    hasNextPage, endCursor, edges = fetch_event_nodes(query=query_first_page, variables=variables_first_page)
    # If the query has an error, I set the edges as None
    if not edges:
        return

    events.extend(edges)

    after_cursor = endCursor
    variables_next_page = {
        "owner": variables_total_count["owner"],
        "name": variables_total_count["name"],
        "number": variables_total_count["number"],
        "first": first,
        "after_cursor": after_cursor
    }
    while hasNextPage:
        page = page + 1
        hasNextPage, after_cursor, edges = fetch_event_nodes(query=query_next_page, variables=variables_next_page)
        # If the query has an error, I set the edges as None
        if not edges:
            return
        variables_next_page["after_cursor"] = after_cursor
        events.extend(edges)

    # Note that there is no PullRequestRevisionMarker
    count = {
        "AssignedEvent": 0,
        "UnassignedEvent": 0,
        "IssueComment": 0,
        "CommentDeletedEvent": 0,
        "ConnectedEvent": 0,
        "DisconnectedEvent": 0,
        "CrossReferencedEvent": 0,
        "ReferencedEvent": 0,
        "TransferredEvent": 0,
        "LabeledEvent": 0,
        "UnlabeledEvent": 0,
        "MentionedEvent": 0,
        "MilestonedEvent": 0,
        "DemilestonedEvent": 0,
        "ClosedEvent": 0,
        "ReopenedEvent": 0,
        "LockedEvent": 0,
        "UnlockedEvent": 0,
        "PinnedEvent": 0,
        "UnpinnedEvent": 0,
        "MarkedAsDuplicateEvent": 0,
        "UnmarkedAsDuplicateEvent": 0,
        "AddedToProjectEvent": 0,
        "RemovedFromProjectEvent": 0,
        "MovedColumnsInProjectEvent": 0,
        "ConvertedNoteToIssueEvent": 0,
        "SubscribedEvent": 0,
        "UnsubscribedEvent": 0,
        "RenamedTitleEvent": 0,
        "UserBlockedEvent": 0,
        # From here, PR only events
        "AutomaticBaseChangeFailedEvent": 0,
        "AutomaticBaseChangeSucceededEvent": 0,
        "BaseRefChangedEvent": 0,
        "BaseRefForcePushedEvent": 0,
        "HeadRefDeletedEvent": 0,
        "HeadRefForcePushedEvent": 0,
        "HeadRefRestoredEvent": 0,
        "PullRequestCommit": 0,
        "PullRequestCommitCommentThread": 0,
        "ConvertToDraftEvent": 0,
        "DeployedEvent": 0,
        "DeploymentEnvironmentChangedEvent": 0,
        "MergedEvent": 0,
        "PullRequestReview": 0,
        "PullRequestReviewThread": 0,
        "ReadyForReviewEvent": 0,
        "ReviewDismissedEvent": 0,
        "ReviewRequestedEvent": 0,
        "ReviewRequestRemovedEvent": 0
    }

    # We use skip instead of beforeEventCursor to reach a specific timelineItem in the list
    # because skip seems much more stable.
    skip = 0
    repository = variables_total_count["owner"] + "/" + variables_total_count["name"]
    number = variables_total_count["number"]
    for i in range(0, len(events)):
        eventType = events[i]["node"]["__typename"]
        event = events[i]["node"]
        # Save a document of the event in MongoDB
        if eventType == "AssignedEvent":
            timelineItem = save_assigned_event(event)
        elif eventType == "UnassignedEvent":
            timelineItem = save_unassigned_event(event)
        elif eventType == "IssueComment":
            timelineItem = save_issue_comment(event)
        elif eventType == "CommentDeletedEvent":
            timelineItem = save_comment_deleted_event(event, variables_total_count)
        elif eventType == "ConnectedEvent":
            timelineItem = save_connected_event(event)
        elif eventType == "DisconnectedEvent":
            timelineItem = save_disconnected_event(event)
        elif eventType == "CrossReferencedEvent":
            timelineItem = save_cross_referenced_event(event)
        elif eventType == "ReferencedEvent":
            timelineItem = save_referenced_event(event)
        elif eventType == "TransferredEvent":
            timelineItem = save_transferred_event(event)
        elif eventType == "LabeledEvent":
            timelineItem = save_labeled_event(event)
        elif eventType == "UnlabeledEvent":
            timelineItem = save_unlabeled_event(event)
        elif eventType == "MentionedEvent":
            timelineItem = save_mentioned_event(event, variables_total_count)
        elif eventType == "MilestonedEvent":
            timelineItem = save_milestoned_event(event)
        elif eventType == "DemilestonedEvent":
            timelineItem = save_demilestoned_event(event)
        elif eventType == "ClosedEvent":
            timelineItem = save_closed_event(event)
        elif eventType == "ReopenedEvent":
            timelineItem = save_reopened_event(event)
        elif eventType == "LockedEvent":
            timelineItem = save_locked_event(event)
        elif eventType == "UnlockedEvent":
            timelineItem = save_unlocked_event(event)
        elif eventType == "PinnedEvent":
            timelineItem = save_pinned_event(event)
        elif eventType == "UnpinnedEvent":
            timelineItem = save_unpinned_event(event)
        elif eventType == "MarkedAsDuplicateEvent":
            timelineItem = save_marked_as_duplicate_event(event, variables_total_count)
        elif eventType == "UnmarkedAsDuplicateEvent":
            timelineItem = save_unmarked_as_duplicate_event(event, variables_total_count)
        elif eventType == "AddedToProjectEvent":
            timelineItem = save_added_to_project_event(event, variables_total_count)
        elif eventType == "RemovedFromProjectEvent":
            timelineItem = save_removed_from_project_event(event, variables_total_count)
        elif eventType == "MovedColumnsInProjectEvent":
            timelineItem = save_moved_columns_in_project_event(event, variables_total_count)
        elif eventType == "ConvertedNoteToIssueEvent":
            timelineItem = save_converted_note_to_issue_event(event, variables_total_count)
        elif eventType == "SubscribedEvent":
            timelineItem = save_subscribed_event(event)
        elif eventType == "UnsubscribedEvent":
            timelineItem = save_unsubscribed_event(event)
        elif eventType == "RenamedTitleEvent":
            timelineItem = save_renamed_title_event(event)
        elif eventType == "UserBlockedEvent":
            timelineItem = save_user_blocked_event(event, variables_total_count)
        # From here: PR-only events
        elif eventType == "AutomaticBaseChangeFailedEvent":
            timelineItem = save_automatic_base_change_failed_event(event)
        elif eventType == "AutomaticBaseChangeSucceededEvent":
            timelineItem = save_automatic_base_change_succeeded_event(event)
        elif eventType == "BaseRefChangedEvent":
            timelineItem = save_baseRef_changed_event(event, variables_total_count)
        elif eventType == "BaseRefForcePushedEvent":
            timelineItem = save_baseRef_force_pushed_event(event)
        elif eventType == "HeadRefDeletedEvent":
            timelineItem = save_headRef_deleted_event(event)
        elif eventType == "HeadRefForcePushedEvent":
            timelineItem = save_headRef_force_pushed_event(event)
        elif eventType == "HeadRefRestoredEvent":
            timelineItem = save_headRef_restored_event(event)
        elif eventType == "PullRequestCommit":
            timelineItem = save_pr_commit(event)
        elif eventType == "PullRequestCommitCommentThread":
            timelineItem = save_pr_commit_comment_thread(event, variables_total_count, skip)
        elif eventType == "ConvertToDraftEvent":
            timelineItem = save_convert_to_draft_event(event)
        elif eventType == "DeployedEvent":
            timelineItem = save_deployed_event(event)
        elif eventType == "DeploymentEnvironmentChangedEvent":
            timelineItem = save_deployment_environment_changed_event(event)
        elif eventType == "MergedEvent":
            timelineItem = save_merged_event(event)
        elif eventType == "PullRequestReview":
            timelineItem = save_pr_review(event, variables_total_count, skip)
        elif eventType == "PullRequestReviewThread":
            timelineItem = save_pr_review_thread(event, variables_total_count, skip)
        elif eventType == "ReadyForReviewEvent":
            timelineItem = save_ready_for_review_event(event)
        elif eventType == "ReviewDismissedEvent":
            timelineItem = save_review_dismissed_event(event)
        elif eventType == "ReviewRequestedEvent":
            timelineItem = save_review_requested_event(event)
        elif eventType == "ReviewRequestRemovedEvent":
            timelineItem = save_review_request_removed_event(event)
        else:
            raise Exception("{} is an unexpected event type of pullRequest timeline items".format(eventType))

        # Save the timelineItem in the focal pullRequest
        num_updated = PullRequest.objects(repository=repository, number=number).update(push__timeline=timelineItem)
        if num_updated != 1:
            raise Exception(
                "No pullRequest with number {} in repo {} -- MongoDB database".format(str(number), repository))

        count[eventType] = count[eventType] + 1
        skip = skip + 1

    print("------------------------------------------------------------")
    print("{} events are added to the timeline of pullRequest #{} in repo {}/{} -- MongoDB database".
          format(str(len(events)), variables_total_count["number"],
                 variables_total_count["owner"], variables_total_count["name"]))
    for key in count:
        if count[key] != 0:
            print("  --> {}: {} added".format(key, count[key]))
    print("------------------------------------------------------------")
    # ------------------------------


def fetch_event_nodes(query, variables):
    """
    Call GitHub GraphQL API to get data
    :param query: The GraphQL query
    :param variables: Variables included in the query
    :return: hasNextPage, endCursor, nodes
    """

    if get_remaining() > cost:
        result = run_query_variable(query, variables)
    else:
        sleep = sleep_in_seconds(get_reset())
        print("Need to sleep about {} minutes to reset the 5000 scores".format(str(sleep / 60)))
        time.sleep(sleep)
        print("Restart! :-)")
        result = run_query_variable(query, variables)

    # Record if an error occurs. What I have now is that there are additional timelineItems beyond the length.
    # Or, we can say that the problem is that we cannot reach out to the "real" end TimelineItem
    # I find one solution is to remove the field headRef if the end TimelineItem is HeadRefDeleted
    if "errors" in result:
        result_text = json.dumps(result, indent=4)
        file = open(path_message, "a")
        file.write("\n" + result_text + ",")
        file.close()
        variables_text = json.dumps(variables, indent=4)
        file = open(path_var, "a")
        file.write("\n" + variables_text + ",")
        file.close()

        hasNextPage = False
        endCursor = None
        edges = None
        return hasNextPage, endCursor, edges

    if not result["data"]["repository"]:
        raise Exception("Repository not found")
    else:
        hasNextPage = result["data"]["repository"]["pullRequest"]["timelineItems"]["pageInfo"]["hasNextPage"]
        endCursor = result["data"]["repository"]["pullRequest"]["timelineItems"]["pageInfo"]["endCursor"]
        edges = result["data"]["repository"]["pullRequest"]["timelineItems"]["edges"]

        return hasNextPage, endCursor, edges


# ----------------------------------
# FROM HERE: Issues Have the Same Event

def save_assigned_event(node):
    """
    Save the event objects/documents and save the timeline items of those events
    :param node: Node of the event
    :return: timelineItem to be pushed to the focal pullRequest; save the event in MongoDB as a document
    """
    actor = node["actor"]
    if not actor:
        actor = ""
        actorType = ""
    else:
        actor = node["actor"]["login"]
        actorType = node["actor"]["__typename"]
    createdAt = node["createdAt"]

    assignee = node["assignee"]
    if not assignee:
        assignee = ""
        assigneeType = ""
    else:
        assignee = node["assignee"]["login"]
        assigneeType = node["assignee"]["__typename"]

    # Assignable is a required field of AssignedEvent
    assignableType = node["assignable"]["__typename"]
    # Repository is a required field (marked by !) of assignable; nameWithOwner is a required field of repository
    repository = node["assignable"]["repository"]["nameWithOwner"]
    number = node["assignable"]["number"]
    assignableId = get_issue_or_pr_id(type_issue_or_pr=assignableType, repository=repository, number=number)

    event = AssignedEvent(actor=actor, actorType=actorType, createdAt=createdAt,
                          assignee=assignee, assigneeType=assigneeType,
                          assignableType=assignableType, repository=repository, number=number,
                          assignableId=assignableId)
    event.save()

    # Create a corresponding timelineItem to be pushed to the focal pullRequest
    eventId = event["id"]  # Note that in Mongoengine the auto ID is "id"; in mongo shell, it is "_id"
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=eventId)

    return timelineItem


def save_unassigned_event(node):
    """
    Save the event objects/documents and save the timeline items of those events
    :param node: Node of the event
    :return: timelineItem to be pushed to the focal pullRequest; save the event in MongoDB as a document
    """
    actor = node["actor"]
    if not actor:
        actor = ""
        actorType = ""
    else:
        actor = node["actor"]["login"]
        actorType = node["actor"]["__typename"]
    createdAt = node["createdAt"]

    assignee = node["assignee"]
    if not assignee:
        assignee = ""
        assigneeType = ""
    else:
        assignee = node["assignee"]["login"]
        assigneeType = node["assignee"]["__typename"]

    # Assignable is a required field of AssignedEvent
    assignableType = node["assignable"]["__typename"]
    # Repository is a required field (marked by !) of assignable; nameWithOwner is a required field of repository
    repository = node["assignable"]["repository"]["nameWithOwner"]
    number = node["assignable"]["number"]
    assignableId = get_issue_or_pr_id(type_issue_or_pr=assignableType, repository=repository, number=number)

    event = UnassignedEvent(actor=actor, actorType=actorType, createdAt=createdAt,
                            assignee=assignee, assigneeType=assigneeType,
                            assignableType=assignableType, repository=repository, number=number,
                            assignableId=assignableId)
    event.save()

    # Create a corresponding timelineItem to be pushed to the focal pullRequest
    eventId = event["id"]  # Note that in Mongoengine the auto ID is "id"; in mongo shell, it is "_id"
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=eventId)

    return timelineItem


def save_issue_comment(node):
    """
    Save the event objects/documents and save the timeline items of those events
    :param node: Node of the event
    :return: timelineItem to be pushed to the focal pullRequest; save the event in MongoDB as a document
    """
    author = node["author"]
    if not author:
        author = ""
        authorType = ""
    else:
        author = node["author"]["login"]
        authorType = node["author"]["__typename"]
    authorAssociation = node["authorAssociation"]

    createdAt = node["createdAt"]
    createdViaEmail = node["createdViaEmail"]
    publishedAt = node["publishedAt"]
    updatedAt = node["updatedAt"]

    databaseId = node["databaseId"]
    resourcePath = node["resourcePath"]
    url = node["url"]

    subjectType = node["pullRequest"]["__typename"]
    repository = node["pullRequest"]["repository"]["nameWithOwner"]
    number = node["pullRequest"]["number"]
    subjectId = get_issue_or_pr_id(type_issue_or_pr=subjectType, repository=repository, number=number)

    isMinimized = node["isMinimized"]
    minimizedReason = node["minimizedReason"]

    body = node["body"]
    bodyHTML = node["bodyHTML"]
    bodyText = node["bodyText"]

    editor = node["editor"]
    if not editor:
        editor = ""
        editorType = ""
    else:
        editor = node["editor"]["login"]
        editorType = node["editor"]["__typename"]
    includesCreatedEdit = node["includesCreatedEdit"]
    lastEditedAt = node["lastEditedAt"]
    editCount = node["userContentEdits"]["totalCount"]

    event = IssueComment(author=author, authorType=authorType, authorAssociation=authorAssociation,
                         createdAt=createdAt, createdViaEmail=createdViaEmail,
                         publishedAt=publishedAt, updatedAt=updatedAt,
                         databaseId=databaseId, resourcePath=resourcePath, url=url,
                         subjectType=subjectType, repository=repository, number=number, subjectId=subjectId,
                         isMinimized=isMinimized, minimizedReason=minimizedReason,
                         body=body, bodyHTML=bodyHTML, bodyText=bodyText,
                         editor=editor, editorType=editorType,
                         includesCreatedEdit=includesCreatedEdit, lastEditedAt=lastEditedAt, editCount=editCount)
    event.save()

    # Update the userContentEdits (only the first 50), i.e., edits
    if editCount > 0:
        for edit in node["userContentEdits"]["nodes"]:  # If no nodes, it will the loop will not execute
            editor = edit["editor"]
            if not editor:
                editor = ""
                editorType = ""
            else:
                editor = edit["editor"]["login"]
                editorType = edit["editor"]["__typename"]
            edit_createdAt = edit["createdAt"]
            editedAt = edit["editedAt"]
            updatedAt = edit["updatedAt"]
            deletedAt = edit["deletedAt"]
            deletedBy = edit["deletedBy"]
            if not deletedBy:
                deletedBy = ""
                deletedByType = ""
            else:
                deletedBy = edit["deletedBy"]["login"]
                deletedByType = edit["deletedBy"]["__typename"]
            diff = edit["diff"]
            edit_obj = Edit(editor=editor, editorType=editorType, createdAt=edit_createdAt, editedAt=editedAt,
                            updatedAt=updatedAt, deletedAt=deletedAt, deletedBy=deletedBy,
                            deletedByType=deletedByType, diff=diff)
            num_updated = IssueComment.objects(id=event["id"]).update_one(push__edits=edit_obj)
            if num_updated != 1:
                raise Exception("Cannot find the issueComment to be updated!")

    # Update the reactionGroups of the issueComment; reactionGroups is a required field
    for reaction in node["reactionGroups"]:
        content = reaction["content"]
        reactionGroup_createdAt = reaction["createdAt"]
        userCount = reaction["users"]["totalCount"]
        reactionGroup = ReactionGroup(content=content, createdAt=reactionGroup_createdAt, userCount=userCount)
        num_updated = IssueComment.objects(id=event["id"]).update_one(push__reactionGroups=reactionGroup)
        if num_updated != 1:
            raise Exception("Cannot find the issueComment to be updated!")

    # Create a corresponding timelineItem to be pushed to the focal pullRequest
    eventId = event["id"]  # Note that in Mongoengine the auto ID is "id"; in mongo shell, it is "_id"
    timelineItem = TimelineItem(actor=author, actorType=authorType, createdAt=node["createdAt"],
                                eventType=node["__typename"], eventId=eventId)

    return timelineItem


def save_comment_deleted_event(node, variables_total_count):
    """
    Save the event objects/documents and save the timeline items of those events
    :param variables_total_count: information about pullRequest number as well as repository owner and name
    :param node: Node of the event
    :return: timelineItem to be pushed to the focal pullRequest; save the event in MongoDB as a document
    """
    actor = node["actor"]
    if not actor:
        actor = ""
        actorType = ""
    else:
        actor = node["actor"]["login"]
        actorType = node["actor"]["__typename"]
    createdAt = node["createdAt"]
    databaseId = node["databaseId"]

    subjectType = "PullRequest"
    repository = variables_total_count["owner"] + "/" + variables_total_count["name"]
    number = variables_total_count["number"]
    subjectId = get_issue_or_pr_id(type_issue_or_pr=subjectType, repository=repository, number=number)

    event = CommentDeletedEvent(actor=actor, actorType=actorType, createdAt=createdAt, databaseId=databaseId,
                                subjectType=subjectType, repository=repository, number=number, subjectId=subjectId)
    event.save()

    # Create a corresponding timelineItem to be pushed to the focal pullRequest
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])

    return timelineItem


def save_connected_event(node):
    """
    Save the event objects/documents and save the timeline items of those events
    :param node: Node of the event
    :return: timelineItem to be pushed to the focal pullRequest; save the event in MongoDB as a document
    """
    actor = node["actor"]
    if not actor:
        actor = ""
        actorType = ""
    else:
        actor = node["actor"]["login"]
        actorType = node["actor"]["__typename"]
    createdAt = node["createdAt"]
    isCrossRepository = node["isCrossRepository"]

    sourceType = node["source"]["__typename"]
    sourceRepository = node["source"]["repository"]["nameWithOwner"]
    sourceNumber = node["source"]["number"]
    sourceId = get_issue_or_pr_id(type_issue_or_pr=sourceType, repository=sourceRepository, number=sourceNumber)

    subjectType = node["subject"]["__typename"]
    subjectRepository = node["subject"]["repository"]["nameWithOwner"]
    subjectNumber = node["subject"]["number"]
    if subjectType == "Issue":
        issue = Issue.objects(repository=subjectRepository, number=subjectNumber).only("id")
        if len(issue) == 1:
            subjectId = issue[0]["id"]
        else:
            subjectId = ""
            print("ConnectedEvent: There are no {} or multiple {} with number {} in repo {} -- MongoDB database".
                  format(subjectType, subjectType, str(subjectNumber), subjectRepository))
    elif subjectType == "PullRequest":
        pr = PullRequest.objects(repository=subjectRepository, number=subjectNumber).only("id")
        if len(pr) == 1:
            subjectId = pr[0]["id"]
        else:
            subjectId = ""
            print("ConnectedEvent: There are no {}s or multiple {}s with number {} in repo {} -- MongoDB database".
                  format(subjectType, subjectType, str(subjectNumber), subjectRepository))
    else:
        raise Exception("The {} type is not a documented ReferecedSubject, which can be only Issue or PullRequest".
                        format(sourceType))

    if not subjectId:
        event = ConnectedEvent(actor=actor, actorType=actorType, createdAt=createdAt,
                               isCrossRepository=isCrossRepository,
                               sourceType=sourceType, sourceRepository=sourceRepository,
                               sourceNumber=sourceNumber, sourceId=sourceId,
                               subjectType=subjectType, subjectRepository=subjectRepository,
                               subjectNumber=subjectNumber)
    else:
        event = ConnectedEvent(actor=actor, actorType=actorType, createdAt=createdAt,
                               isCrossRepository=isCrossRepository,
                               sourceType=sourceType, sourceRepository=sourceRepository,
                               sourceNumber=sourceNumber, sourceId=sourceId,
                               subjectType=subjectType, subjectRepository=subjectRepository,
                               subjectNumber=subjectNumber, subjectId=subjectId)
    event.save()

    # Create a corresponding timelineItem to be pushed to the focal pullRequest
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])

    return timelineItem


def save_disconnected_event(node):
    """
    Save the event objects/documents and save the timeline items of those events
    :param node: Node of the event
    :return: timelineItem to be pushed to the focal pullRequest; save the event in MongoDB as a document
    """
    actor = node["actor"]
    if not actor:
        actor = ""
        actorType = ""
    else:
        actor = node["actor"]["login"]
        actorType = node["actor"]["__typename"]
    createdAt = node["createdAt"]

    isCrossRepository = node["isCrossRepository"]

    sourceType = node["source"]["__typename"]
    sourceRepository = node["source"]["repository"]["nameWithOwner"]
    sourceNumber = node["source"]["number"]
    sourceId = get_issue_or_pr_id(type_issue_or_pr=sourceType, repository=sourceRepository, number=sourceNumber)

    subjectType = node["subject"]["__typename"]
    subjectRepository = node["subject"]["repository"]["nameWithOwner"]
    subjectNumber = node["subject"]["number"]
    if subjectType == "Issue":
        issue = Issue.objects(repository=subjectRepository, number=subjectNumber).only("id")
        if len(issue) == 1:
            subjectId = issue[0]["id"]
        else:
            subjectId = ""
            print("DisconnectedEvent: There are no {}  or multiple {} with number {} in repo {} -- MongoDB database".
                  format(subjectType, subjectType, str(subjectNumber), subjectRepository))
    elif subjectType == "PullRequest":
        pr = PullRequest.objects(repository=subjectRepository, number=subjectNumber).only("id")
        if len(pr) == 1:
            subjectId = pr[0]["id"]
        else:
            subjectId = ""
            print("DisconnectedEvent: There are no {}s  or multiple {}s with number {} in repo {} -- MongoDB database".
                  format(subjectType, subjectType, str(subjectNumber), subjectRepository))
    else:
        raise Exception("The {} type is not a documented ReferecedSubject, which can be only Issue or PullRequest".
                        format(sourceType))

    if not subjectId:
        event = DisconnectedEvent(actor=actor, actorType=actorType, createdAt=createdAt,
                                  isCrossRepository=isCrossRepository,
                                  sourceType=sourceType, sourceRepository=sourceRepository,
                                  sourceNumber=sourceNumber, sourceId=sourceId,
                                  subjectType=subjectType, subjectRepository=subjectRepository,
                                  subjectNumber=subjectNumber)
    else:
        event = DisconnectedEvent(actor=actor, actorType=actorType, createdAt=createdAt,
                                  isCrossRepository=isCrossRepository,
                                  sourceType=sourceType, sourceRepository=sourceRepository,
                                  sourceNumber=sourceNumber, sourceId=sourceId,
                                  subjectType=subjectType, subjectRepository=subjectRepository,
                                  subjectNumber=subjectNumber, subjectId=subjectId)
    event.save()

    # Create a corresponding timelineItem to be pushed to the focal pullRequest
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])

    return timelineItem


def save_cross_referenced_event(node):
    """
    Save the event objects/documents and save the timeline items of those events
    :param node: Node of the event
    :return: timelineItem to be pushed to the focal pullRequest; save the event in MongoDB as a document
    """
    actor = node["actor"]
    if not actor:
        actor = ""
        actorType = ""
    else:
        actor = node["actor"]["login"]
        actorType = node["actor"]["__typename"]
    createdAt = node["createdAt"]
    referencedAt = node["referencedAt"]

    resourcePath = node["resourcePath"]
    url = node["url"]

    isCrossRepository = node["isCrossRepository"]
    willCloseTarget = node["willCloseTarget"]

    sourceType = node["source"]["__typename"]
    sourceRepository = node["source"]["repository"]["nameWithOwner"]
    sourceNumber = node["source"]["number"]
    if sourceType == "Issue":
        issue = Issue.objects(repository=sourceRepository, number=sourceNumber).only("id")
        if len(issue) == 1:
            sourceId = issue[0]["id"]
        else:
            sourceId = ""
            print("CrossReferencedEvent: There are no {}  or multiple {} with number {} in repo {} -- MongoDB database".
                  format(sourceType, sourceType, str(sourceNumber), sourceRepository))
    elif sourceType == "PullRequest":
        pr = PullRequest.objects(repository=sourceRepository, number=sourceNumber).only("id")
        if len(pr) == 1:
            sourceId = pr[0]["id"]
        else:
            sourceId = ""
            print("CrossReferencedEvent: There are no {}s  or multiple {}s with number {} in repo {} -- MongoDB database".
                  format(sourceType, sourceType, str(sourceNumber), sourceRepository))
    else:
        raise Exception("The {} type is not a documented ReferecedSubject, which can be only Issue or PullRequest".
                        format(sourceType))

    targetType = node["target"]["__typename"]
    targetRepository = node["target"]["repository"]["nameWithOwner"]
    targetNumber = node["target"]["number"]
    targetId = get_issue_or_pr_id(type_issue_or_pr=targetType, repository=targetRepository, number=targetNumber)

    if not sourceId:
        event = CrossReferencedEvent(actor=actor, actorType=actorType, createdAt=createdAt, referencedAt=referencedAt,
                                     resourcePath=resourcePath, url=url,
                                     isCrossRepository=isCrossRepository, willCloseTarget=willCloseTarget,
                                     sourceType=sourceType, sourceRepository=sourceRepository,
                                     sourceNumber=sourceNumber,
                                     targetType=targetType, targetRepository=targetRepository,
                                     targetNumber=targetNumber, targetId=targetId)
    else:
        event = CrossReferencedEvent(actor=actor, actorType=actorType, createdAt=createdAt, referencedAt=referencedAt,
                                     resourcePath=resourcePath, url=url,
                                     isCrossRepository=isCrossRepository, willCloseTarget=willCloseTarget,
                                     sourceType=sourceType, sourceRepository=sourceRepository,
                                     sourceNumber=sourceNumber, sourceId=sourceId,
                                     targetType=targetType, targetRepository=targetRepository,
                                     targetNumber=targetNumber, targetId=targetId)
    event.save()

    # Create a corresponding timelineItem to be pushed to the focal pullRequest
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])

    return timelineItem


def save_referenced_event(node):
    """
    Save the event objects/documents and save the timeline items of those events
    :param node: Node of the event
    :return: timelineItem to be pushed to the focal pullRequest; save the event in MongoDB as a document
    """
    actor = node["actor"]
    if not actor:
        actor = ""
        actorType = ""
    else:
        actor = node["actor"]["login"]
        actorType = node["actor"]["__typename"]
    createdAt = node["createdAt"]

    commit = node["commit"]
    if not commit:
        commitOid = ""
    else:
        commitOid = node["commit"]["oid"]
    commitRepository = node["commitRepository"]["nameWithOwner"]

    isCrossRepository = node["isCrossRepository"]
    isDirectReference = node["isDirectReference"]

    subjectType = node["subject"]["__typename"]
    repository = node["subject"]["repository"]["nameWithOwner"]
    number = node["subject"]["number"]
    subjectId = get_issue_or_pr_id(type_issue_or_pr=subjectType, repository=repository, number=number)

    event = ReferencedEvent(actor=actor, actorType=actorType, createdAt=createdAt,
                            commitOid=commitOid, commitRepository=commitRepository,
                            isCrossRepository=isCrossRepository, isDirectReference=isDirectReference,
                            subjectType=subjectType, repository=repository, number=number, subjectId=subjectId)
    event.save()

    # Create a corresponding timelineItem to be pushed to the focal pullRequest
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])

    return timelineItem


def save_transferred_event(node):
    """
    Save the event objects/documents and save the timeline items of those events
    :param node: Node of the event
    :return: timelineItem to be pushed to the focal pullRequest; save the event in MongoDB as a document
    """
    actor = node["actor"]
    if not actor:
        actor = ""
        actorType = ""
    else:
        actor = node["actor"]["login"]
        actorType = node["actor"]["__typename"]
    createdAt = node["createdAt"]

    fromRepository = node["fromRepository"]
    if not fromRepository:
        fromRepository = ""
    else:
        fromRepository = node["fromRepository"]["nameWithOwner"]

    # It seems that no pullRequests have this Transferred type of event
    subjectType = node["issue"]["__typename"]
    repository = node["issue"]["repository"]["nameWithOwner"]
    number = node["issue"]["number"]
    subjectId = get_issue_or_pr_id(type_issue_or_pr=subjectType, repository=repository, number=number)

    event = TransferredEvent(actor=actor, actorType=actorType, createdAt=createdAt, fromRepository=fromRepository,
                             subjectType=subjectType, repository=repository,
                             number=number, subjectId=subjectId)
    event.save()

    # Create a corresponding timelineItem to be pushed to the focal pullRequest
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])

    return timelineItem


def save_labeled_event(node):
    """
    Save the event objects/documents and save the timeline items of those events
    :param node: Node of the event
    :return: timelineItem to be pushed to the focal pullRequest; save the event in MongoDB as a document
    """
    actor = node["actor"]
    if not actor:
        actor = ""
        actorType = ""
    else:
        actor = node["actor"]["login"]
        actorType = node["actor"]["__typename"]
    createdAt = node["createdAt"]

    labelName = node["label"]["name"]
    labelColor = node["label"]["color"]
    labels = Label.objects(repository=node["label"]["repository"]["nameWithOwner"],
                           name=labelName, color=labelColor).only("id")
    if not labels:
        name = node["label"]["name"]
        labelCreatedAt = node["label"]["createdAt"]
        color = node["label"]["color"]
        isDefault = node["label"]["isDefault"]
        description = node["label"]["description"]
        repository = node["label"]["repository"]["nameWithOwner"]
        resourcePath = node["label"]["resourcePath"]
        url = node["label"]["url"]
        updatedAt = node["label"]["updatedAt"]
        label = Label(name=name, createdAt=labelCreatedAt, color=color, isDefault=isDefault, description=description,
                      repository=repository, resourcePath=resourcePath, url=url, updatedAt=updatedAt)
        label.save()
        labelId = label["id"]
    elif len(labels) == 1:
        labelId = labels[0]["id"]
    else:
        raise Exception("There are multiple labels with name {}, color {} in repo {}".
                        format(labelName, labelColor, node["label"]["repository"]))

    labelableType = node["labelable"]["__typename"]
    repository = node["labelable"]["repository"]["nameWithOwner"]
    number = node["labelable"]["number"]
    labelableId = get_issue_or_pr_id(type_issue_or_pr=labelableType, repository=repository, number=number)

    event = LabeledEvent(actor=actor, actorType=actorType, createdAt=createdAt,
                         labelName=labelName, labelColor=labelColor, labelId=labelId,
                         labelableType=labelableType, repository=repository, number=number, labelableId=labelableId)
    event.save()

    # Create a corresponding timelineItem to be pushed to the focal pullRequest
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])

    return timelineItem


def save_unlabeled_event(node):
    """
    Save the event objects/documents and save the timeline items of those events
    :param node: Node of the event
    :return: timelineItem to be pushed to the focal pullRequest; save the event in MongoDB as a document
    """
    actor = node["actor"]
    if not actor:
        actor = ""
        actorType = ""
    else:
        actor = node["actor"]["login"]
        actorType = node["actor"]["__typename"]
    createdAt = node["createdAt"]

    labelName = node["label"]["name"]
    labelColor = node["label"]["color"]
    labels = Label.objects(repository=node["label"]["repository"]["nameWithOwner"],
                           name=labelName, color=labelColor).only("id")
    if not labels:
        name = node["label"]["name"]
        labelCreatedAt = node["label"]["createdAt"]
        color = node["label"]["color"]
        isDefault = node["label"]["isDefault"]
        description = node["label"]["description"]
        repository = node["label"]["repository"]["nameWithOwner"]
        resourcePath = node["label"]["resourcePath"]
        url = node["label"]["url"]
        updatedAt = node["label"]["updatedAt"]
        label = Label(name=name, createdAt=labelCreatedAt, color=color, isDefault=isDefault, description=description,
                      repository=repository, resourcePath=resourcePath, url=url, updatedAt=updatedAt)
        label.save()
        labelId = label["id"]
    elif len(labels) == 1:
        labelId = labels[0]["id"]
    else:
        raise Exception("There are multiple labels with name {}, color {} in repo {}".
                        format(labelName, labelColor, node["label"]["repository"]))

    labelableType = node["labelable"]["__typename"]
    repository = node["labelable"]["repository"]["nameWithOwner"]
    number = node["labelable"]["number"]
    labelableId = get_issue_or_pr_id(type_issue_or_pr=labelableType, repository=repository, number=number)

    event = UnlabeledEvent(actor=actor, actorType=actorType, createdAt=createdAt,
                           labelName=labelName, labelColor=labelColor, labelId=labelId,
                           labelableType=labelableType, repository=repository, number=number, labelableId=labelableId)
    event.save()

    # Create a corresponding timelineItem to be pushed to the focal pullRequest
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])

    return timelineItem


def save_mentioned_event(node, variables_total_count):
    """
    Save the event objects/documents and save the timeline items of those events
    :param variables_total_count: information about repository owner and name as well as pullRequest number
    :param node: Node of the event
    :return: timelineItem to be pushed to the focal pullRequest; save the event in MongoDB as a document
    """
    actor = node["actor"]
    if not actor:
        actor = ""
        actorType = ""
    else:
        actor = node["actor"]["login"]
        actorType = node["actor"]["__typename"]
    createdAt = node["createdAt"]
    databaseId = node["databaseId"]

    subjectType = "PullRequest"
    repository = variables_total_count["owner"] + "/" + variables_total_count["name"]
    number = variables_total_count["number"]
    subjectId = get_issue_or_pr_id(type_issue_or_pr=subjectType, repository=repository, number=number)

    event = MentionedEvent(actor=actor, actorType=actorType, createdAt=createdAt, databaseId=databaseId,
                           subjectType=subjectType, repository=repository, number=number, subjectId=subjectId)
    event.save()

    # Create a corresponding timelineItem to be pushed to the focal pullRequest
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])

    return timelineItem


def save_milestoned_event(node):
    """
    Save the event objects/documents and save the timeline items of those events
    :param node: Node of the event
    :return: timelineItem to be pushed to the focal pullRequest; save the event in MongoDB as a document
    """
    actor = node["actor"]
    if not actor:
        actor = ""
        actorType = ""
    else:
        actor = node["actor"]["login"]
        actorType = node["actor"]["__typename"]
    createdAt = node["createdAt"]

    milestoneTitle = node["milestoneTitle"]

    subjectType = node["subject"]["__typename"]
    repository = node["subject"]["repository"]["nameWithOwner"]
    number = node["subject"]["number"]
    subjectId = get_issue_or_pr_id(type_issue_or_pr=subjectType, repository=repository, number=number)

    event = MilestonedEvent(actor=actor, actorType=actorType, createdAt=createdAt, milestoneTitle=milestoneTitle,
                            subjectType=subjectType, repository=repository, number=number, subjectId=subjectId)
    event.save()

    # Create a corresponding timelineItem to be pushed to the focal pullRequest
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])

    return timelineItem


def save_demilestoned_event(node):
    """
    Save the event objects/documents and save the timeline items of those events
    :param node: Node of the event
    :return: timelineItem to be pushed to the focal pullRequest; save the event in MongoDB as a document
    """
    actor = node["actor"]
    if not actor:
        actor = ""
        actorType = ""
    else:
        actor = node["actor"]["login"]
        actorType = node["actor"]["__typename"]
    createdAt = node["createdAt"]

    milestoneTitle = node["milestoneTitle"]

    subjectType = node["subject"]["__typename"]
    repository = node["subject"]["repository"]["nameWithOwner"]
    number = node["subject"]["number"]
    subjectId = get_issue_or_pr_id(type_issue_or_pr=subjectType, repository=repository, number=number)

    event = DemilestonedEvent(actor=actor, actorType=actorType, createdAt=createdAt, milestoneTitle=milestoneTitle,
                              subjectType=subjectType, repository=repository, number=number, subjectId=subjectId)
    event.save()

    # Create a corresponding timelineItem to be pushed to the focal pullRequest
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])

    return timelineItem


def save_closed_event(node):
    """
    Save the event objects/documents and save the timeline items of those events
    :param node: Node of the event
    :return: timelineItem to be pushed to the focal pullRequest; save the event in MongoDB as a document
    """
    actor = node["actor"]
    if not actor:
        actor = ""
        actorType = ""
    else:
        actor = node["actor"]["login"]
        actorType = node["actor"]["__typename"]
    createdAt = node["createdAt"]
    resourcePath = node["resourcePath"]
    url = node["url"]

    closableType = node["closable"]["__typename"]
    repository = node["closable"]["repository"]["nameWithOwner"]
    number = node["closable"]["number"]
    closableId = get_issue_or_pr_id(type_issue_or_pr=closableType, repository=repository, number=number)

    closer = node["closer"]
    if not closer:
        event = ClosedEvent(actor=actor, actorType=actorType, createdAt=createdAt, resourcePath=resourcePath, url=url,
                            closableType=closableType, repository=repository, number=number, closableId=closableId)
    else:
        closerType = node["closer"]["__typename"]
        closerRepository = node["closer"]["repository"]["nameWithOwner"]
        if closerType == "Commit":
            commitOid = node["closer"]["oid"]
            event = ClosedEvent(actor=actor, actorType=actorType, createdAt=createdAt, resourcePath=resourcePath,
                                url=url,
                                closableType=closableType, repository=repository, number=number, closableId=closableId,
                                closerType=closerType, closerRepository=closerRepository, commitOid=commitOid)
        else:
            pullRequestNumber = node["closer"]["number"]
            event = ClosedEvent(actor=actor, actorType=actorType, createdAt=createdAt, resourcePath=resourcePath,
                                url=url,
                                closableType=closableType, repository=repository, number=number, closableId=closableId,
                                closerType=closerType, closerRepository=closerRepository,
                                pullRequestNumber=pullRequestNumber)
    event.save()

    # Create a corresponding timelineItem to be pushed to the focal pullRequest
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])

    return timelineItem


def save_reopened_event(node):
    """
    Save the event objects/documents and save the timeline items of those events
    :param node: Node of the event
    :return: timelineItem to be pushed to the focal pullRequest; save the event in MongoDB as a document
    """
    actor = node["actor"]
    if not actor:
        actor = ""
        actorType = ""
    else:
        actor = node["actor"]["login"]
        actorType = node["actor"]["__typename"]
    createdAt = node["createdAt"]

    closableType = node["closable"]["__typename"]
    repository = node["closable"]["repository"]["nameWithOwner"]
    number = node["closable"]["number"]
    closableId = get_issue_or_pr_id(type_issue_or_pr=closableType, repository=repository, number=number)

    event = ReopenedEvent(actor=actor, actorType=actorType, createdAt=createdAt,
                          closableType=closableType, repository=repository, number=number, closableId=closableId)
    event.save()

    # Create a corresponding timelineItem to be pushed to the focal pullRequest
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])

    return timelineItem


def save_locked_event(node):
    """
    Save the event objects/documents and save the timeline items of those events
    :param node: Node of the event
    :return: timelineItem to be pushed to the focal pullRequest; save the event in MongoDB as a document
    """
    actor = node["actor"]
    if not actor:
        actor = ""
        actorType = ""
    else:
        actor = node["actor"]["login"]
        actorType = node["actor"]["__typename"]
    createdAt = node["createdAt"]

    lockReason = node["lockReason"]

    lockableType = node["lockable"]["__typename"]
    repository = node["lockable"]["repository"]["nameWithOwner"]
    number = node["lockable"]["number"]
    lockableId = get_issue_or_pr_id(type_issue_or_pr=lockableType, repository=repository, number=number)

    event = LockedEvent(actor=actor, actorType=actorType, createdAt=createdAt, lockReason=lockReason,
                        lockableType=lockableType, repository=repository, number=number, lockableId=lockableId)
    event.save()

    # Create a corresponding timelineItem to be pushed to the focal pullRequest
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])

    return timelineItem


def save_unlocked_event(node):
    """
    Save the event objects/documents and save the timeline items of those events
    :param node: Node of the event
    :return: timelineItem to be pushed to the focal pullRequest; save the event in MongoDB as a document
    """
    actor = node["actor"]
    if not actor:
        actor = ""
        actorType = ""
    else:
        actor = node["actor"]["login"]
        actorType = node["actor"]["__typename"]
    createdAt = node["createdAt"]

    lockableType = node["lockable"]["__typename"]
    repository = node["lockable"]["repository"]["nameWithOwner"]
    number = node["lockable"]["number"]
    lockableId = get_issue_or_pr_id(type_issue_or_pr=lockableType, repository=repository, number=number)

    event = UnlockedEvent(actor=actor, actorType=actorType, createdAt=createdAt,
                          lockableType=lockableType, repository=repository, number=number, lockableId=lockableId)
    event.save()

    # Create a corresponding timelineItem to be pushed to the focal pullRequest
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])

    return timelineItem


def save_pinned_event(node):
    """
    Save the event objects/documents and save the timeline items of those events
    :param node: Node of the event
    :return: timelineItem to be pushed to the focal pullRequest; save the event in MongoDB as a document
    """
    actor = node["actor"]
    if not actor:
        actor = ""
        actorType = ""
    else:
        actor = node["actor"]["login"]
        actorType = node["actor"]["__typename"]
    createdAt = node["createdAt"]

    # It seems that no pullRequests have this Pinned type of event
    subjectType = node["issue"]["__typename"]
    repository = node["issue"]["repository"]["nameWithOwner"]
    number = node["issue"]["number"]
    subjectId = get_issue_or_pr_id(type_issue_or_pr=subjectType, repository=repository, number=number)

    event = PinnedEvent(actor=actor, actorType=actorType, createdAt=createdAt,
                        subjectType=subjectType, repository=repository, number=number, subjectId=subjectId)
    event.save()

    # Create a corresponding timelineItem to be pushed to the focal pullRequest
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])

    return timelineItem


def save_unpinned_event(node):
    """
    Save the event objects/documents and save the timeline items of those events
    :param node: Node of the event
    :return: timelineItem to be pushed to the focal pullRequest; save the event in MongoDB as a document
    """
    actor = node["actor"]
    if not actor:
        actor = ""
        actorType = ""
    else:
        actor = node["actor"]["login"]
        actorType = node["actor"]["__typename"]
    createdAt = node["createdAt"]

    #  It seems that no pullRequests have this Pinned type of event
    subjectType = node["issue"]["__typename"]
    repository = node["issue"]["repository"]["nameWithOwner"]
    number = node["issue"]["number"]
    subjectId = get_issue_or_pr_id(type_issue_or_pr=subjectType, repository=repository, number=number)

    event = UnpinnedEvent(actor=actor, actorType=actorType, createdAt=createdAt,
                        subjectType=subjectType, repository=repository, number=number, subjectId=subjectId)
    event.save()

    # Create a corresponding timelineItem to be pushed to the focal pullRequest
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])

    return timelineItem


def save_marked_as_duplicate_event(node, variables_total_count):
    """
    Save the event objects/documents and save the timeline items of those events
    :param variables_total_count: information about the focal pullRequest number and repository
    :param node: Node of the event
    :return: timelineItem to be pushed to the focal pullRequest; save the event in MongoDB as a document
    """
    actor = node["actor"]
    if not actor:
        actor = ""
        actorType = ""
    else:
        actor = node["actor"]["login"]
        actorType = node["actor"]["__typename"]
    createdAt = node["createdAt"]

    subjectType = "PullRequest"
    repository = variables_total_count["owner"] + "/" + variables_total_count["name"]
    number = variables_total_count["number"]
    subjectId = get_issue_or_pr_id(type_issue_or_pr=subjectType, repository=repository, number=number)

    event = MarkedAsDuplicateEvent(actor=actor, actorType=actorType, createdAt=createdAt,
                                   subjectType=subjectType, repository=repository, number=number, subjectId=subjectId)
    event.save()

    # Create a corresponding timelineItem to be pushed to the focal pullRequest
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])

    return timelineItem


def save_unmarked_as_duplicate_event(node, variables_total_count):
    """
    Save the event objects/documents and save the timeline items of those events
    :param variables_total_count: information about the focal pullRequest and repository
    :param node: Node of the event
    :return: timelineItem to be pushed to the focal pullRequest; save the event in MongoDB as a document
    """
    actor = node["actor"]
    if not actor:
        actor = ""
        actorType = ""
    else:
        actor = node["actor"]["login"]
        actorType = node["actor"]["__typename"]
    createdAt = node["createdAt"]

    subjectType = "PullRequest"
    repository = variables_total_count["owner"] + "/" + variables_total_count["name"]
    number = variables_total_count["number"]
    subjectId = get_issue_or_pr_id(type_issue_or_pr=subjectType, repository=repository, number=number)

    event = UnmarkedAsDuplicateEvent(actor=actor, actorType=actorType, createdAt=createdAt,
                                     subjectType=subjectType, repository=repository, number=number, subjectId=subjectId)
    event.save()

    # Create a corresponding timelineItem to be pushed to the focal pullRequest
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])

    return timelineItem


def save_added_to_project_event(node, variables_total_count):
    """
    Save the event objects/documents and save the timeline items of those events
    :param variables_total_count: information about the focal pullRequest and repository
    :param node: Node of the event
    :return: timelineItem to be pushed to the focal pullRequest; save the event in MongoDB as a document
    """
    actor = node["actor"]
    if not actor:
        actor = ""
        actorType = ""
    else:
        actor = node["actor"]["login"]
        actorType = node["actor"]["__typename"]
    createdAt = node["createdAt"]

    databaseId = node["databaseId"]

    subjectType = "PullRequest"
    repository = variables_total_count["owner"] + "/" + variables_total_count["name"]
    number = variables_total_count["number"]
    subjectId = get_issue_or_pr_id(type_issue_or_pr=subjectType, repository=repository, number=number)

    event = AddedToProjectEvent(actor=actor, actorType=actorType, createdAt=createdAt, databaseId=databaseId,
                                subjectType=subjectType, repository=repository, number=number, subjectId=subjectId)
    event.save()

    # Create a corresponding timelineItem to be pushed to the focal pullRequest
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])

    return timelineItem


def save_removed_from_project_event(node, variables_total_count):
    """
    Save the event objects/documents and save the timeline items of those events
    :param variables_total_count: information about the focal pullRequest and repository
    :param node: Node of the event
    :return: timelineItem to be pushed to the focal pullRequest; save the event in MongoDB as a document
    """
    actor = node["actor"]
    if not actor:
        actor = ""
        actorType = ""
    else:
        actor = node["actor"]["login"]
        actorType = node["actor"]["__typename"]
    createdAt = node["createdAt"]

    databaseId = node["databaseId"]

    subjectType = "PullRequest"
    repository = variables_total_count["owner"] + "/" + variables_total_count["name"]
    number = variables_total_count["number"]
    subjectId = get_issue_or_pr_id(type_issue_or_pr=subjectType, repository=repository, number=number)

    event = RemovedFromProjectEvent(actor=actor, actorType=actorType, createdAt=createdAt, databaseId=databaseId,
                                    subjectType=subjectType, repository=repository, number=number, subjectId=subjectId)
    event.save()

    # Create a corresponding timelineItem to be pushed to the focal pullRequest
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])

    return timelineItem


def save_moved_columns_in_project_event(node, variables_total_count):
    """
    Save the event objects/documents and save the timeline items of those events
    :param variables_total_count: information about the focal issue and repository
    :param node: Node of the event
    :return: timelineItem to be pushed to the focal pullRequest; save the event in MongoDB as a document
    """
    actor = node["actor"]
    if not actor:
        actor = ""
        actorType = ""
    else:
        actor = node["actor"]["login"]
        actorType = node["actor"]["__typename"]
    createdAt = node["createdAt"]

    databaseId = node["databaseId"]

    subjectType = "PullRequest"
    repository = variables_total_count["owner"] + "/" + variables_total_count["name"]
    number = variables_total_count["number"]
    subjectId = get_issue_or_pr_id(type_issue_or_pr=subjectType, repository=repository, number=number)

    event = MovedColumnsInProjectEvent(actor=actor, actorType=actorType, createdAt=createdAt, databaseId=databaseId,
                                       subjectType=subjectType, repository=repository, number=number,
                                       subjectId=subjectId)
    event.save()

    # Create a corresponding timelineItem to be pushed to the focal pullRequest
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])

    return timelineItem


def save_converted_note_to_issue_event(node, variables_total_count):
    """
    Save the event objects/documents and save the timeline items of those events
    :param variables_total_count: information about the focal pullRequest and repository
    :param node: Node of the event
    :return: timelineItem to be pushed to the focal pullRequest; save the event in MongoDB as a document
    """
    actor = node["actor"]
    if not actor:
        actor = ""
        actorType = ""
    else:
        actor = node["actor"]["login"]
        actorType = node["actor"]["__typename"]
    createdAt = node["createdAt"]

    databaseId = node["databaseId"]

    subjectType = "Issue"
    repository = variables_total_count["owner"] + "/" + variables_total_count["name"]
    number = variables_total_count["number"]
    subjectId = get_issue_or_pr_id(type_issue_or_pr=subjectType, repository=repository, number=number)

    event = ConvertedNoteToIssueEvent(actor=actor, actorType=actorType, createdAt=createdAt, databaseId=databaseId,
                                      subjectType=subjectType, repository=repository, number=number,
                                      subjectId=subjectId)
    event.save()

    # Create a corresponding timelineItem to be pushed to the focal pullRequest
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])

    return timelineItem


def save_subscribed_event(node):
    """
    Save the event objects/documents and save the timeline items of those events
    :param node: Node of the event
    :return: timelineItem to be pushed to the focal pullRequest; save the event in MongoDB as a document
    """
    actor = node["actor"]
    if not actor:
        actor = ""
        actorType = ""
    else:
        actor = node["actor"]["login"]
        actorType = node["actor"]["__typename"]
    createdAt = node["createdAt"]

    subscribableType = node["subscribable"]["__typename"]
    repository = node["subscribable"]["repository"]["nameWithOwner"]
    number = node["subscribable"]["number"]
    subscribableId = get_issue_or_pr_id(type_issue_or_pr=subscribableType, repository=repository, number=number)

    event = SubscribedEvent(actor=actor, actorType=actorType, createdAt=createdAt,
                            subscribableType=subscribableType, repository=repository, number=number,
                            subscribableId=subscribableId)
    event.save()

    # Create a corresponding timelineItem to be pushed to the focal pullRequest
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])

    return timelineItem


def save_unsubscribed_event(node):
    """
    Save the event objects/documents and save the timeline items of those events
    :param node: Node of the event
    :return: timelineItem to be pushed to the focal pullRequest; save the event in MongoDB as a document
    """
    actor = node["actor"]
    if not actor:
        actor = ""
        actorType = ""
    else:
        actor = node["actor"]["login"]
        actorType = node["actor"]["__typename"]
    createdAt = node["createdAt"]

    subscribableType = node["subscribable"]["__typename"]
    repository = node["subscribable"]["repository"]["nameWithOwner"]
    number = node["subscribable"]["number"]
    subscribableId = get_issue_or_pr_id(type_issue_or_pr=subscribableType, repository=repository, number=number)

    event = UnsubscribedEvent(actor=actor, actorType=actorType, createdAt=createdAt,
                              subscribableType=subscribableType, repository=repository, number=number,
                              subscribableId=subscribableId)
    event.save()

    # Create a corresponding timelineItem to be pushed to the focal pullRequest
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])

    return timelineItem


def save_renamed_title_event(node):
    """
    Save the event objects/documents and save the timeline items of those events
    :param node: Node of the event
    :return: timelineItem to be pushed to the focal pullRequest; save the event in MongoDB as a document
    """
    actor = node["actor"]
    if not actor:
        actor = ""
        actorType = ""
    else:
        actor = node["actor"]["login"]
        actorType = node["actor"]["__typename"]
    createdAt = node["createdAt"]

    currentTitle = node["currentTitle"]
    previousTitle = node["previousTitle"]

    subjectType = node["subject"]["__typename"]
    repository = node["subject"]["repository"]["nameWithOwner"]
    number = node["subject"]["number"]
    subjectId = get_issue_or_pr_id(type_issue_or_pr=subjectType, repository=repository, number=number)

    event = RenamedTitleEvent(actor=actor, actorType=actorType, createdAt=createdAt,
                              currentTitle=currentTitle, previousTitle=previousTitle,
                              subjectType=subjectType, repository=repository, number=number, subjectId=subjectId)
    event.save()

    # Create a corresponding timelineItem to be pushed to the focal pullRequest
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])

    return timelineItem


def save_user_blocked_event(node, variables_total_count):
    """
    Save the event objects/documents and save the timeline items of those events
    :param node: Node of the event
    :param variables_total_count: information about the focal pullRequest and repository
    :return: timelineItem to be pushed to the focal pullRequest; save the event in MongoDB as a document
    """
    actor = node["actor"]
    if not actor:
        actor = ""
        actorType = ""
    else:
        actor = node["actor"]["login"]
        actorType = node["actor"]["__typename"]
    createdAt = node["createdAt"]

    blockDuration = node["blockDuration"]

    blocked = node["subject"]
    if not blocked:
        blockedUser = ""
        blockedUserType = ""
    else:
        blockedUser = node["subject"]["login"]
        blockedUserType = node["subject"]["__typename"]

    subjectType = "PullRequest"
    repository = variables_total_count["owner"] + "/" + variables_total_count["name"]
    number = variables_total_count["number"]
    subjectId = get_issue_or_pr_id(type_issue_or_pr=subjectType, repository=repository, number=number)

    event = UserBlockedEvent(actor=actor, actorType=actorType, createdAt=createdAt,
                             blockDuration=blockDuration, blockedUser=blockedUser, blockedUserType=blockedUserType,
                             subjectType=subjectType, repository=repository, number=number, subjectId=subjectId)
    event.save()

    # Create a corresponding timelineItem to be pushed to the focal pullRequest
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])

    return timelineItem


# ------------------------------------
# FROM HERE: PR Only Events

def save_automatic_base_change_failed_event(node):
    """
    Save the event object/document and save the timeline items of the event
    :param node: Node of the event
    :return: timelineItem to be pushed to the focal pullRequest; save the event in MongoDB as a document
    """
    actor = node["actor"]
    if not actor:
        actor = None
        actorType = None
    else:
        actor = node["actor"]["login"]
        actorType = node["actor"]["__typename"]
    createdAt = node["createdAt"]

    newBase = node["newBase"]
    oldBase = node["oldBase"]

    subjectType = node["pullRequest"]["__typename"]
    repository = node["pullRequest"]["repository"]["nameWithOwner"]
    number = node["pullRequest"]["number"]
    subjectId = get_issue_or_pr_id(type_issue_or_pr=subjectType, repository=repository, number=number)

    event = AutomaticBaseChangeFailed(actor=actor, actorType=actorType, createdAt=createdAt,
                                      newBase=newBase, oldBase=oldBase,
                                      subjectType=subjectType, repository=repository,
                                      number=number, subjectId=subjectId)
    event.save()

    # Create a corresponding timelineItem to be pushed to the focal pullRequest
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])

    return timelineItem


def save_automatic_base_change_succeeded_event(node):
    """
    Save the event object/document and save the timeline items of the event
    :param node: Node of the event
    :return: timelineItem to be pushed to the focal pullRequest; save the event in MongoDB as a document
    """
    actor = node["actor"]
    if not actor:
        actor = None
        actorType = None
    else:
        actor = node["actor"]["login"]
        actorType = node["actor"]["__typename"]
    createdAt = node["createdAt"]

    newBase = node["newBase"]
    oldBase = node["oldBase"]

    subjectType = node["pullRequest"]["__typename"]
    repository = node["pullRequest"]["repository"]["nameWithOwner"]
    number = node["pullRequest"]["number"]
    subjectId = get_issue_or_pr_id(type_issue_or_pr=subjectType, repository=repository, number=number)

    event = AutomaticBaseChangeSucceeded(actor=actor, actorType=actorType, createdAt=createdAt,
                                         newBase=newBase, oldBase=oldBase,
                                         subjectType=subjectType, repository=repository,
                                         number=number, subjectId=subjectId)
    event.save()

    # Create a corresponding timelineItem to be pushed to the focal pullRequest
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])

    return timelineItem


def save_baseRef_changed_event(node, variables_total_count):
    """
    Save the event objects/documents and save the timeline items of those events
    :param node: Node of the event
    :param variables_total_count: information about the focal pullRequest and repository
    :return: timelineItem to be pushed to the focal pullRequest; save the event in MongoDB as a document
    """
    actor = node["actor"]
    if not actor:
        actor = ""
        actorType = ""
    else:
        actor = node["actor"]["login"]
        actorType = node["actor"]["__typename"]
    createdAt = node["createdAt"]

    databaseId = node["databaseId"]

    subjectType = "PullRequest"
    repository = variables_total_count["owner"] + "/" + variables_total_count["name"]
    number = variables_total_count["number"]
    subjectId = get_issue_or_pr_id(type_issue_or_pr=subjectType, repository=repository, number=number)

    event = BaseRefChanged(actor=actor, actorType=actorType, createdAt=createdAt, databaseId=databaseId,
                           subjectType=subjectType, repository=repository, number=number, subjectId=subjectId)
    event.save()

    # Create a corresponding timelineItem to be pushed to the focal pullRequest
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])

    return timelineItem


def save_baseRef_force_pushed_event(node):
    """
    Save the event object/document and save the timeline items of the event
    :param node: Node of the event
    :return: timelineItem to be pushed to the focal pullRequest; save the event in MongoDB as a document
    """
    actor = node["actor"]
    if not actor:
        actor = None
        actorType = None
    else:
        actor = node["actor"]["login"]
        actorType = node["actor"]["__typename"]
    createdAt = node["createdAt"]

    ref = node["ref"]
    if not ref:
        refName = None
        refPrefix = None
        refOid = None
    else:
        refName = node["ref"]["name"]
        refPrefix = node["ref"]["prefix"]
        if node["ref"]["target"]:
            refOid = node["ref"]["target"]["oid"]
        else:
            refOid = None

    beforeCommit = node["beforeCommit"]
    if not beforeCommit:
        beforeCommitOid = None
    else:
        beforeCommitOid = node["beforeCommit"]["oid"]

    afterCommit = node["afterCommit"]
    if not afterCommit:
        afterCommitOid = None
    else:
        afterCommitOid = node["afterCommit"]["oid"]

    subjectType = node["pullRequest"]["__typename"]
    repository = node["pullRequest"]["repository"]["nameWithOwner"]
    number = node["pullRequest"]["number"]
    subjectId = get_issue_or_pr_id(type_issue_or_pr=subjectType, repository=repository, number=number)

    event = BaseRefForcePushed(actor=actor, actorType=actorType, createdAt=createdAt,
                               refName=refName, refPrefix=refPrefix, refOid=refOid,
                               beforeCommitOid=beforeCommitOid, afterCommitOid=afterCommitOid,
                               subjectType=subjectType, repository=repository, number=number, subjectId=subjectId)
    event.save()

    # Create a corresponding timelineItem to be pushed to the focal pullRequest
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])

    return timelineItem


def save_headRef_deleted_event(node):
    """
    Save the event object/document and save the timeline items of the event
    :param node: Node of the event
    :return: timelineItem to be pushed to the focal pullRequest; save the event in MongoDB as a document
    """
    actor = node["actor"]
    if not actor:
        actor = None
        actorType = None
    else:
        actor = node["actor"]["login"]
        actorType = node["actor"]["__typename"]
    createdAt = node["createdAt"]

    headRefName = node["headRefName"]

    headRef = node["headRef"]
    if not headRef:
        headRefPrefix = None
        headRefOid = None
    else:
        headRefPrefix = node["headRef"]["prefix"]
        if node["headRef"]["target"]:
            headRefOid = node["headRef"]["target"]["oid"]
        else:
            headRefOid = None

    subjectType = node["pullRequest"]["__typename"]
    repository = node["pullRequest"]["repository"]["nameWithOwner"]
    number = node["pullRequest"]["number"]
    subjectId = get_issue_or_pr_id(type_issue_or_pr=subjectType, repository=repository, number=number)

    event = HeadRefDeleted(actor=actor, actorType=actorType, createdAt=createdAt,
                           headRefName=headRefName, headRefPrefix=headRefPrefix, headRefOid=headRefOid,
                           subjectType=subjectType, repository=repository, number=number, subjectId=subjectId)
    event.save()

    # Create a corresponding timelineItem to be pushed to the focal pullRequest
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])

    return timelineItem


def save_headRef_force_pushed_event(node):
    """
    Save the event object/document and save the timeline items of the event
    :param node: Node of the event
    :return: timelineItem to be pushed to the focal pullRequest; save the event in MongoDB as a document
    """
    actor = node["actor"]
    if not actor:
        actor = None
        actorType = None
    else:
        actor = node["actor"]["login"]
        actorType = node["actor"]["__typename"]
    createdAt = node["createdAt"]

    ref = node["ref"]
    if not ref:
        refName = None
        refPrefix = None
        refOid = None
    else:
        refName = node["ref"]["name"]
        refPrefix = node["ref"]["prefix"]
        if node["ref"]["target"]:
            refOid = node["ref"]["target"]["oid"]
        else:
            refOid = None

    beforeCommit = node["beforeCommit"]
    if not beforeCommit:
        beforeCommitOid = None
    else:
        beforeCommitOid = node["beforeCommit"]["oid"]

    afterCommit = node["afterCommit"]
    if not afterCommit:
        afterCommitOid = None
    else:
        afterCommitOid = node["afterCommit"]["oid"]

    subjectType = node["pullRequest"]["__typename"]
    repository = node["pullRequest"]["repository"]["nameWithOwner"]
    number = node["pullRequest"]["number"]
    subjectId = get_issue_or_pr_id(type_issue_or_pr=subjectType, repository=repository, number=number)

    event = HeadRefForcePushed(actor=actor, actorType=actorType, createdAt=createdAt,
                               refName=refName, refPrefix=refPrefix, refOid=refOid,
                               beforeCommitOid=beforeCommitOid, afterCommitOid=afterCommitOid,
                               subjectType=subjectType, repository=repository, number=number, subjectId=subjectId)
    event.save()

    # Create a corresponding timelineItem to be pushed to the focal pullRequest
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])

    return timelineItem


def save_headRef_restored_event(node):
    """
    Save the event object/document and save the timeline items of the event
    :param node: Node of the event
    :return: timelineItem to be pushed to the focal pullRequest; save the event in MongoDB as a document
    """
    actor = node["actor"]
    if not actor:
        actor = None
        actorType = None
    else:
        actor = node["actor"]["login"]
        actorType = node["actor"]["__typename"]
    createdAt = node["createdAt"]

    subjectType = node["pullRequest"]["__typename"]
    repository = node["pullRequest"]["repository"]["nameWithOwner"]
    number = node["pullRequest"]["number"]
    subjectId = get_issue_or_pr_id(type_issue_or_pr=subjectType, repository=repository, number=number)

    event = HeadRefRestored(actor=actor, actorType=actorType, createdAt=createdAt,
                            subjectType=subjectType, repository=repository, number=number, subjectId=subjectId)
    event.save()

    # Create a corresponding timelineItem to be pushed to the focal pullRequest
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])

    return timelineItem


def save_pr_commit(node):
    """
    Save the event object/document and save the timeline items of the event
    :param node: Node of the event
    :return: timelineItem to be pushed to the focal pullRequest; save the event in MongoDB as a document
    """
    repository_commit = node["commit"]["repository"]["nameWithOwner"]
    commitOid = node["commit"]["oid"]

    commits = Commit.objects(repository=repository_commit, oid=commitOid)

    if len(commits) == 1:
        actor = commits[0]["author"]
        actorType = commits[0]["authorType"]
        createdAt = commits[0]["authoredDate"]
    elif len(commits) == 0:
        save_repo_commit(repository=repository_commit, commitOid=commitOid)
        commits = Commit.objects(repository=repository_commit, oid=commitOid)
        actor = commits[0]["author"]
        actorType = commits[0]["authorType"]
        createdAt = commits[0]["authoredDate"]
    else:
        raise Exception("There are multiple commits with oid {} in repo {}!".format(commitOid, repository_commit))

    # Get identification information of the focal pullRequest
    # Note that the repository of the focal pullRequest can be different from that of the commit
    repository = node["pullRequest"]["repository"]["nameWithOwner"]
    number = node["pullRequest"]["number"]

    # Get objectId of the focal pullRequest
    prId = get_issue_or_pr_id(type_issue_or_pr="PullRequest", repository=repository, number=number)
    # Push the focal pullRequest objectId into the associatedPRs in the asoociated commit
    commits[0].update(push__associatedPRs=prId)

    # Create a corresponding timelineItem to be pushed to the focal pullRequest
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=commits[0]["id"])

    return timelineItem


def save_convert_to_draft_event(node):
    """
    Save the event object/document and save the timeline items of the event
    :param node: Node of the event
    :return: timelineItem to be pushed to the focal pullRequest; save the event in MongoDB as a document
    """
    actor = node["actor"]
    if not actor:
        actor = None
        actorType = None
    else:
        actor = node["actor"]["login"]
        actorType = node["actor"]["__typename"]
    createdAt = node["createdAt"]

    resourcePath = node["resourcePath"]
    url = node["resourcePath"]

    subjectType = node["pullRequest"]["__typename"]
    repository = node["pullRequest"]["repository"]["nameWithOwner"]
    number = node["pullRequest"]["number"]
    subjectId = get_issue_or_pr_id(type_issue_or_pr=subjectType, repository=repository, number=number)

    event = ConvertToDraft(actor=actor, actorType=actorType, createdAt=createdAt,
                           resourcePath=resourcePath, url=url,
                           subjectType=subjectType, repository=repository, number=number, subjectId=subjectId)
    event.save()

    # Create a corresponding timelineItem to be pushed to the focal pullRequest
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])

    return timelineItem


def save_deployed_event(node):
    """
    Save the event object/document and save the timeline items of the event
    :param node: Node of the event
    :return: timelineItem to be pushed to the focal pullRequest; save the event in MongoDB as a document
    """
    actor = node["actor"]
    if not actor:
        actor = None
        actorType = None
    else:
        actor = node["actor"]["login"]
        actorType = node["actor"]["__typename"]
    createdAt = node["createdAt"]

    databaseId = node["databaseId"]

    ref = node["ref"]
    if not ref:
        refType = None
        refName = None
        refPrefix = None
        refOid = None
    else:
        refType = node["ref"]["__typename"]
        refName = node["ref"]["name"]
        refPrefix = node["ref"]["prefix"]
        if node["ref"]["target"]:
            refOid = node["ref"]["target"]["oid"]
        else:
            refOid = None

    # Save deployment
    creator = node["deployment"]["creator"]["login"]  # deployment, creator, and login are required
    creatorType = node["deployment"]["creator"]["__typename"]
    createdAt_deployment = node["deployment"]["createdAt"]
    updatedAt = node["deployment"]["updatedAt"]
    commitOid = node["deployment"]["commitOid"]
    task = node["deployment"]["task"]
    databaseId_deployment = node["deployment"]["databaseId"]
    description = node["deployment"]["description"]
    payload = node["deployment"]["payload"]
    environment = node["deployment"]["environment"]
    originalEnvironment = node["deployment"]["originalEnvironment"]
    state = node["deployment"]["state"]
    deployment = Deployment(creator=creator, creatorType=creatorType,
                            createdAt=createdAt_deployment, updatedAt=updatedAt,
                            commitOid=commitOid, task=task, databaseId=databaseId_deployment,
                            description=description, payload=payload,
                            environment=environment, originalEnvironment=originalEnvironment,
                            state=state)

    # Associated pullRequest
    subjectType = node["pullRequest"]["__typename"]
    repository = node["pullRequest"]["repository"]["nameWithOwner"]
    number = node["pullRequest"]["number"]
    subjectId = get_issue_or_pr_id(type_issue_or_pr=subjectType, repository=repository, number=number)

    event = Deployed(actor=actor, actorType=actorType, createdAt=createdAt, databaseId=databaseId,
                     refType=refType, refName=refName, refPrefix=refPrefix, refOid=refOid, deployment=deployment,
                     subjectType=subjectType, repository=repository, number=number, subjectId=subjectId)
    event.save()

    # Create a corresponding timelineItem to be pushed to the focal pullRequest
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])

    return timelineItem


def save_deployment_environment_changed_event(node):
    """
    Save the event object/document and save the timeline items of the event
    :param node: Node of the event
    :return: timelineItem to be pushed to the focal pullRequest; save the event in MongoDB as a document
    """
    actor = node["actor"]
    if not actor:
        actor = None
        actorType = None
    else:
        actor = node["actor"]["login"]
        actorType = node["actor"]["__typename"]
    createdAt = node["createdAt"]

    updateState = node["deploymentStatus"]["State"]

    # Save deployment
    creator = node["deploymentStatus"]["deployment"]["creator"]["login"]  # deployment, creator, and login are required
    creatorType = node["deploymentStatus"]["deployment"]["creator"]["__typename"]
    createdAt_deployment = node["deploymentStatus"]["deployment"]["createdAt"]
    updatedAt = node["deploymentStatus"]["deployment"]["updatedAt"]
    commitOid = node["deploymentStatus"]["deployment"]["commitOid"]
    task = node["deploymentStatus"]["deployment"]["task"]
    databaseId_deployment = node["deploymentStatus"]["deployment"]["databaseId"]
    description = node["deploymentStatus"]["deployment"]["description"]
    payload = node["deploymentStatus"]["deployment"]["payload"]
    environment = node["deploymentStatus"]["deployment"]["environment"]
    originalEnvironment = node["deploymentStatus"]["deployment"]["originalEnvironment"]
    state = node["deploymentStatus"]["deployment"]["state"]
    deployment = Deployment(creator=creator, creatorType=creatorType,
                            createdAt=createdAt_deployment, updatedAt=updatedAt,
                            commitOid=commitOid, task=task, databaseId=databaseId_deployment,
                            description=description, payload=payload,
                            environment=environment, originalEnvironment=originalEnvironment,
                            state=state)

    # Associated pullRequest
    subjectType = node["pullRequest"]["__typename"]
    repository = node["pullRequest"]["repository"]["nameWithOwner"]
    number = node["pullRequest"]["number"]
    subjectId = get_issue_or_pr_id(type_issue_or_pr=subjectType, repository=repository, number=number)

    event = DeploymentEnvironmentChanged(actor=actor, actorType=actorType, createdAt=createdAt,
                                         updateState=updateState, deployment=deployment, subjectType=subjectType,
                                         repository=repository, number=number, subjectId=subjectId)
    event.save()

    # Create a corresponding timelineItem to be pushed to the focal pullRequest
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])

    return timelineItem


def save_merged_event(node):
    """
    Save the event object/document and save the timeline items of the event
    :param node: Node of the event
    :return: timelineItem to be pushed to the focal pullRequest; save the event in MongoDB as a document
    """
    actor = node["actor"]
    if not actor:
        actor = None
        actorType = None
    else:
        actor = node["actor"]["login"]
        actorType = node["actor"]["__typename"]
    createdAt = node["createdAt"]

    commit = node["commit"]
    if not commit:
        commitOid = None
    else:
        commitOid = node["commit"]["oid"]

    resourcePath = node["resourcePath"]
    url = node["url"]

    mergeRefName = node["mergeRefName"]
    mergeRef = node["mergeRef"]
    if not mergeRef:
        mergeRefType = None
        mergeRefPrefix = None
        mergeRefOid = None
    else:
        mergeRefType = node["mergeRef"]["__typename"]
        mergeRefPrefix = node["mergeRef"]["prefix"]
        if node["mergeRef"]["target"]:
            mergeRefOid = node["mergeRef"]["target"]["oid"]
        else:
            mergeRefOid = None

    # Associated pullRequest
    subjectType = node["pullRequest"]["__typename"]
    repository = node["pullRequest"]["repository"]["nameWithOwner"]
    number = node["pullRequest"]["number"]
    subjectId = get_issue_or_pr_id(type_issue_or_pr=subjectType, repository=repository, number=number)

    event = Merged(actor=actor, actorType=actorType, createdAt=createdAt,
                   commitOid=commitOid, resourcePath=resourcePath, url=url,
                   mergeRefType=mergeRefType, mergeRefName=mergeRefName,
                   mergeRefPrefix=mergeRefPrefix, mergeRefOid=mergeRefOid,
                   subjectType=subjectType, repository=repository, number=number, subjectId=subjectId)
    event.save()

    # Create a corresponding timelineItem to be pushed to the focal pullRequest
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])

    return timelineItem


def save_ready_for_review_event(node):
    """
    Save the event object/document and save the timeline items of the event
    :param node: Node of the event
    :return: timelineItem to be pushed to the focal pullRequest; save the event in MongoDB as a document
    """
    actor = node["actor"]
    if not actor:
        actor = None
        actorType = None
    else:
        actor = node["actor"]["login"]
        actorType = node["actor"]["__typename"]
    createdAt = node["createdAt"]

    resourcePath = node["resourcePath"]
    url = node["url"]

    # Associated pullRequest
    subjectType = node["pullRequest"]["__typename"]
    repository = node["pullRequest"]["repository"]["nameWithOwner"]
    number = node["pullRequest"]["number"]
    subjectId = get_issue_or_pr_id(type_issue_or_pr=subjectType, repository=repository, number=number)

    event = ReadyForReview(actor=actor, actorType=actorType, createdAt=createdAt,
                           resourcePath=resourcePath, url=url,
                           subjectType=subjectType, repository=repository, number=number, subjectId=subjectId)
    event.save()

    # Create a corresponding timelineItem to be pushed to the focal pullRequest
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])

    return timelineItem


def save_review_dismissed_event(node):
    """
    Save the event object/document and save the timeline items of the event
    :param node: Node of the event
    :return: timelineItem to be pushed to the focal pullRequest; save the event in MongoDB as a document
    """
    actor = node["actor"]
    if not actor:
        actor = None
        actorType = None
    else:
        actor = node["actor"]["login"]
        actorType = node["actor"]["__typename"]
    createdAt = node["createdAt"]

    databaseId = node["databaseId"]
    resourcePath = node["resourcePath"]
    url = node["url"]

    dismissalMessage = node["dismissalMessage"]
    dismissalMessageHTML = node["dismissalMessageHTML"]
    previousReviewState = node["previousReviewState"]

    # Associated pullRequest
    subjectType = node["pullRequest"]["__typename"]
    repository = node["pullRequest"]["repository"]["nameWithOwner"]
    number = node["pullRequest"]["number"]
    subjectId = get_issue_or_pr_id(type_issue_or_pr=subjectType, repository=repository, number=number)

    commit = node["pullRequestCommit"]
    if not commit:
        commitOid = None
    else:
        commitOid = node["pullRequestCommit"]["commit"]["oid"]

    review = node["review"]
    if not review:
        review = None
    else:
        if node["review"]["author"]:
            author = node["review"]["author"]["login"]
        else:
            author = None
        createdAt_review = node["review"]["createdAt"]
        body = node["review"]["body"]
        pullRequestReviews = PullRequestReview.objects(author=author, createdAt=createdAt_review, body=body)
        if len(pullRequestReviews) == 1:
            review = pullRequestReviews[0]["id"]
        elif len(pullRequestReviews) == 0:
            raise Exception("Cannot find the associated review that is dismissed; author: {}, createdAt: {}, ".
                            format(author, str(createdAt_review)) + "body: {}".format(body))
        else:
            raise Exception("Multiple associated reviews are found to be dismissed by this event; author: {}, ".
                            format(author) + "createdAt: {}, body: {}".format(str(createdAt_review), body))

    event = ReviewDismissed(actor=actor, actorType=actorType, createdAt=createdAt,
                            databaseId=databaseId, resourcePath=resourcePath, url=url,
                            dismissalMessage=dismissalMessage, dismissalMessageHTML=dismissalMessageHTML,
                            previousReviewState=previousReviewState,
                            subjectType=subjectType, repository=repository, number=number, subjectId=subjectId,
                            commitOid=commitOid, review=review)
    event.save()

    # Create a corresponding timelineItem to be pushed to the focal pullRequest
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])

    return timelineItem


def save_review_requested_event(node):
    """
    Save the event object/document and save the timeline items of the event
    :param node: Node of the event
    :return: timelineItem to be pushed to the focal pullRequest; save the event in MongoDB as a document
    """
    actor = node["actor"]
    if not actor:
        actor = None
        actorType = None
    else:
        actor = node["actor"]["login"]
        actorType = node["actor"]["__typename"]
    createdAt = node["createdAt"]

    requestedReviewer = node["requestedReviewer"]
    if not requestedReviewer:
        requestedReviewer = None
        requestedReviewerType = None
    else:
        requestedReviewerType = node["requestedReviewer"]["__typename"]
        if requestedReviewerType == "Team":
            organization = node["requestedReviewer"]["organization"]["login"]
            slug = node["requestedReviewer"]["slug"]
            name = node["requestedReviewer"]["name"]
            createdAt_team = node["requestedReviewer"]["createdAt"]
            teams = Team.objects(organization=organization, slug=slug, name=name, createdAt=createdAt_team)
            if len(teams) == 1:
                requestedReviewer = organization + "/" + "name"
            elif len(teams) == 0:
                requestedReviewer = organization + "/" + "name"
                # Save the team in MongoDB
                combinedSlug = node["requestedReviewer"]["combinedSlug"]
                updatedAt = node["requestedReviewer"]["updatedAt"]
                databaseId = node["requestedReviewer"]["databaseId"]
                avatarUrl = node["requestedReviewer"]["avatarUrl"]
                resourcePath = node["requestedReviewer"]["resourcePath"]
                url = node["requestedReviewer"]["url"]
                team = Team(organization=organization, slug=slug, combinedSlug=combinedSlug,
                            createdAt=createdAt_team, updatedAt=updatedAt,
                            databaseId=databaseId, avatarUrl=avatarUrl, resourcePath=resourcePath, url=url,
                            name=name)
                team.save()
            else:
                raise Exception("There are multiple teams with organization: {}, slug: {}, name: {}, createdAt: {}".
                                format(organization, slug, name, str(createdAt)))
        else:
            requestedReviewer = node["requestedReviewer"]["login"]

    # Associated pullRequest
    subjectType = node["pullRequest"]["__typename"]
    repository = node["pullRequest"]["repository"]["nameWithOwner"]
    number = node["pullRequest"]["number"]
    subjectId = get_issue_or_pr_id(type_issue_or_pr=subjectType, repository=repository, number=number)

    event = ReviewRequested(actor=actor, actorType=actorType, createdAt=createdAt,
                            requestedReviewer=requestedReviewer, requestedReviewerType=requestedReviewerType,
                            subjectType=subjectType, repository=repository, number=number, subjectId=subjectId)
    event.save()

    # Create a corresponding timelineItem to be pushed to the focal pullRequest
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])

    return timelineItem


def save_review_request_removed_event(node):
    """
    Save the event object/document and save the timeline items of the event
    :param node: Node of the event
    :return: timelineItem to be pushed to the focal pullRequest; save the event in MongoDB as a document
    """
    actor = node["actor"]
    if not actor:
        actor = None
        actorType = None
    else:
        actor = node["actor"]["login"]
        actorType = node["actor"]["__typename"]
    createdAt = node["createdAt"]

    requestedReviewer = node["requestedReviewer"]
    if not requestedReviewer:
        requestedReviewer = None
        requestedReviewerType = None
    else:
        requestedReviewerType = node["requestedReviewer"]["__typename"]
        if requestedReviewerType == "Team":
            organization = node["requestedReviewer"]["organization"]["login"]
            slug = node["requestedReviewer"]["slug"]
            name = node["requestedReviewer"]["name"]
            createdAt_team = node["requestedReviewer"]["createdAt"]
            teams = Team.objects(organization=organization, slug=slug, name=name, createdAt=createdAt_team)
            if len(teams) == 1:
                requestedReviewer = organization + "/" + "name"
            elif len(teams) == 0:
                requestedReviewer = organization + "/" + "name"
                # Save the team in MongoDB
                combinedSlug = node["requestedReviewer"]["combinedSlug"]
                updatedAt = node["requestedReviewer"]["updatedAt"]
                databaseId = node["requestedReviewer"]["databaseId"]
                avatarUrl = node["requestedReviewer"]["avatarUrl"]
                resourcePath = node["requestedReviewer"]["resourcePath"]
                url = node["requestedReviewer"]["url"]
                team = Team(organization=organization, slug=slug, combinedSlug=combinedSlug,
                            createdAt=createdAt_team, updatedAt=updatedAt,
                            databaseId=databaseId, avatarUrl=avatarUrl, resourcePath=resourcePath, url=url,
                            name=name)
                team.save()
            else:
                raise Exception("There are multiple teams with organization: {}, slug: {}, name: {}, createdAt: {}".
                                format(organization, slug, name, str(createdAt)))
        else:
            requestedReviewer = node["requestedReviewer"]["login"]

    # Associated pullRequest
    subjectType = node["pullRequest"]["__typename"]
    repository = node["pullRequest"]["repository"]["nameWithOwner"]
    number = node["pullRequest"]["number"]
    subjectId = get_issue_or_pr_id(type_issue_or_pr=subjectType, repository=repository, number=number)

    event = ReviewRequestRemoved(actor=actor, actorType=actorType, createdAt=createdAt,
                                 requestedReviewer=requestedReviewer, requestedReviewerType=requestedReviewerType,
                                 subjectType=subjectType, repository=repository, number=number, subjectId=subjectId)
    event.save()

    # Create a corresponding timelineItem to be pushed to the focal pullRequest
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])

    return timelineItem


def save_pr_commit_comment_thread(node, variables_total_count, skip):
    """
    Save the event object/document and save the timeline items of the event
    :param skip: How many timelineItems are before this specific PullRequestCommitCommentThread event
    :param variables_total_count: Information about the focal pullRequest and repository
    :param node: Node of the event
    :return: timelineItem to be pushed to the focal pullRequest; save the event in MongoDB as a document
    """
    commitOid = node["commit"]["oid"]
    path = node["path"]
    position = node["position"]

    subjectType = node["pullRequest"]["__typename"]
    repository = node["pullRequest"]["repository"]["nameWithOwner"]
    number = node["pullRequest"]["number"]
    subjectId = get_issue_or_pr_id(type_issue_or_pr=subjectType, repository=repository, number=number)

    commitCommentCount = node["comments"]["totalCount"]

    event = CommitCommentThread(commitOid=commitOid, path=path, position=position,
                                subjectType=subjectType, repository=repository, number=number, subjectId=subjectId,
                                commitCommentCount=commitCommentCount)
    event.save()

    # Save a list of the objectIds of associated commitComments
    if commitCommentCount > 0:
        commitComments = fetch_commit_or_review_comments_with_pagination(skip=skip,
                                                                         variables_total_count=variables_total_count)
        for commitComment in commitComments:
            commitCommentId = save_commit_comment(node=commitComment)
            num_updated = CommitCommentThread.objects(id=event["id"]).\
                update(add_to_set__commitCommentIds=commitCommentId)
            if num_updated != 1:
                raise Exception("CommitCommentThread: Debug!")

    # Create a corresponding timelineItem to be pushed to the focal pullRequest
    timelineItem = TimelineItem(actor=None, actorType=None, createdAt=None,
                                eventType=node["__typename"], eventId=event["id"])

    return timelineItem


def save_pr_review(node, variables_total_count, skip):
    """
    Save the event object/document and save the timeline items of the event
    :param skip: How many timelineItems are before this PullRequestReview event
    :param variables_total_count: Information about the focal pullRequest and repository
    :param node: Node of the event
    :return: timelineItem to be pushed to the focal pullRequest; save the event in MongoDB as a document
    """
    author = node["author"]
    if not author:
        author = ""
        authorType = ""
    else:
        author = node["author"]["login"]
        authorType = node["author"]["__typename"]
    authorAssociation = node["authorAssociation"]

    state = node["state"]

    commit = node["commit"]
    if not commit:
        commitOid = None
    else:
        commitOid = node["commit"]["oid"]

    createdAt = node["createdAt"]
    createdViaEmail = node["createdViaEmail"]
    publishedAt = node["publishedAt"]
    updatedAt = node["updatedAt"]
    submittedAt = node["submittedAt"]

    databaseId = node["databaseId"]
    resourcePath = node["resourcePath"]
    url = node["url"]

    body = node["body"]
    bodyHTML = node["bodyHTML"]
    bodyText = node["bodyText"]

    editor = node["editor"]
    if not editor:
        editor = ""
        editorType = ""
    else:
        editor = node["editor"]["login"]
        editorType = node["editor"]["__typename"]
    includesCreatedEdit = node["includesCreatedEdit"]
    lastEditedAt = node["lastEditedAt"]
    editCount = node["userContentEdits"]["totalCount"]

    onBehalfOfCount = node["onBehalfOf"]["totalCount"]

    commentCount = node["comments"]["totalCount"]

    subjectType = node["pullRequest"]["__typename"]
    repository = node["pullRequest"]["repository"]["nameWithOwner"]
    number = node["pullRequest"]["number"]
    subjectId = get_issue_or_pr_id(type_issue_or_pr=subjectType, repository=repository, number=number)

    event = PullRequestReview(author=author, authorType=authorType, authorAssociation=authorAssociation,
                              state=state, commitOid=commitOid,
                              createdAt=createdAt, createdViaEmail=createdViaEmail,
                              publishedAt=publishedAt, updatedAt=updatedAt, submittedAt=submittedAt,
                              databaseId=databaseId, resourcePath=resourcePath, url=url,
                              body=body, bodyHTML=bodyHTML, bodyText=bodyText,
                              editor=editor, editorType=editorType, includesCreatedEdit=includesCreatedEdit,
                              lastEditedAt=lastEditedAt, editCount=editCount,
                              onBehalfOfCount=onBehalfOfCount, commentCount=commentCount,
                              subjectType=subjectType, repository=repository, number=number, subjectId=subjectId)
    event.save()

    # Update the userContentEdits (only the first 50), i.e., edits
    if node["userContentEdits"]["nodes"]:
        for edit in node["userContentEdits"]["nodes"]:  # If no nodes, it will the loop will not execute
            editor = edit["editor"]
            if not editor:
                editor = ""
                editorType = ""
            else:
                editor = edit["editor"]["login"]
                editorType = edit["editor"]["__typename"]
            edit_createdAt = edit["createdAt"]
            editedAt = edit["editedAt"]
            updatedAt = edit["updatedAt"]
            deletedAt = edit["deletedAt"]
            deletedBy = edit["deletedBy"]
            if not deletedBy:
                deletedBy = ""
                deletedByType = ""
            else:
                deletedBy = edit["deletedBy"]["login"]
                deletedByType = edit["deletedBy"]["__typename"]
            diff = edit["diff"]
            edit_obj = Edit(editor=editor, editorType=editorType, createdAt=edit_createdAt, editedAt=editedAt,
                            updatedAt=updatedAt, deletedAt=deletedAt, deletedBy=deletedBy,
                            deletedByType=deletedByType, diff=diff)
            num_updated = PullRequestReview.objects(id=event["id"]).update(push__edits=edit_obj)
            if num_updated != 1:
                raise Exception("Cannot find the commitComment to be updated!")

    # Update the reactionGroups of the issueComment; reactionGroups is a required field
    for reaction in node["reactionGroups"]:
        content = reaction["content"]
        reactionGroup_createdAt = reaction["createdAt"]
        userCount = reaction["users"]["totalCount"]
        reactionGroup = ReactionGroup(content=content, createdAt=reactionGroup_createdAt, userCount=userCount)
        num_updated = PullRequestReview.objects(id=event["id"]).update(push__reactionGroups=reactionGroup)
        if num_updated != 1:
            raise Exception("Cannot find the commitComment to be updated!")

    # Update the onBehalfOf
    onBehalfOfs = node["onBehalfOf"]["nodes"]
    for onBehalfOf in onBehalfOfs:
        organization = onBehalfOf["organization"]["login"]
        slug = onBehalfOf["slug"]
        name = onBehalfOf["name"]
        createdAt_team = onBehalfOf["createdAt"]
        teams = Team.objects(organization=organization, slug=slug, name=name, createdAt=createdAt_team)
        if len(teams) == 1:
            num_updated = PullRequestReview.objects(id=event["id"]).update(push__onBehalfOfTeams=teams[0]["id"])
            if num_updated != 1:
                raise Exception("Check the problem! No or multiple PullRequestReview events with id: {}".
                                format(event["id"]))
        elif len(teams) == 0:
            # Save the team in MongoDB
            combinedSlug = onBehalfOf["combinedSlug"]
            updatedAt = onBehalfOf["updatedAt"]
            databaseId = onBehalfOf["databaseId"]
            avatarUrl = onBehalfOf["avatarUrl"]
            resourcePath = onBehalfOf["resourcePath"]
            url = onBehalfOf["url"]
            team = Team(organization=organization, slug=slug, combinedSlug=combinedSlug,
                        createdAt=createdAt_team, updatedAt=updatedAt,
                        databaseId=databaseId, avatarUrl=avatarUrl, resourcePath=resourcePath, url=url,
                        name=name)
            team.save()
            num_updated = PullRequestReview.objects(id=event["id"]).update(push__onBehalfOfIds=team["id"])
            if num_updated != 1:
                raise Exception("Check the problem! No or multiple PullRequestReview events with id: {}".
                                format(event["id"]))
        else:
            raise Exception("There are multiple teams with organization: {}, slug: {}, name: {}, createdAt: {}".
                            format(organization, slug, name, str(createdAt)))

    # Update the comments
    if commentCount > 0:
        reviewComments = fetch_commit_or_review_comments_with_pagination(skip=skip,
                                                                         variables_total_count=variables_total_count)
        for reviewComment in reviewComments:
            reviewCommentId = save_pr_review_comment(node=reviewComment, eventType=node["__typename"], eventId=event["id"])
            num_updated = PullRequestReview.objects(id=event["id"]). \
                update(add_to_set__reviewCommentIds=reviewCommentId)
            if num_updated != 1:
                raise Exception("PullRequestReview: Debug!")

    # Create a corresponding timelineItem to be pushed to the focal pullRequest
    timelineItem = TimelineItem(actor=author, actorType=authorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])

    return timelineItem


def save_pr_review_thread(node, variables_total_count, skip):
    """
    Save the event object/document and save the timeline items of the event
    :param variables_total_count: Information about the focal pullRequest and repository
    :param skip: How many timelineItems are before this PullRequestReviewThread event
    :param node: Node of the event
    :return: timelineItem to be pushed to the focal pullRequest; save the event in MongoDB as a document
    """
    isResolved = node["isResolved"]
    line = node["line"]
    startLine = node["startLine"]
    originalLine = node["originalLine"]
    originalStartLine = node["originalStartLine"]

    resolvedBy = node["resolvedBy"]
    if not resolvedBy:
        resolvedBy = None
        resolvedByType = None
    else:
        resolvedBy = node["resolvedBy"]["login"]
        resolvedByType = node["resolvedBy"]["__typename"]

    diffSide = node["diffSide"]
    startDiffSide = node["startDiffSide"]

    commentCount = node["comments"]["totalCount"]

    subjectType = node["pullRequest"]["__typename"]
    repository = node["pullRequest"]["repository"]["nameWithOwner"]
    number = node["pullRequest"]["number"]
    subjectId = get_issue_or_pr_id(type_issue_or_pr=subjectType, repository=repository, number=number)

    event = PullRequestReviewThread(isResolved=isResolved, line=line, startLine=startLine,
                                    originalLine=originalLine, originalStartLine=originalStartLine,
                                    resolvedBy=resolvedBy, resolvedByType=resolvedByType,
                                    diffSide=diffSide, startDiffSide=startDiffSide, commentCount=commentCount,
                                    subjectType=subjectType, repository=repository, number=number, subjectId=subjectId)
    event.save()

    # Update the comments
    if commentCount > 0:
        reviewComments = fetch_commit_or_review_comments_with_pagination(skip=skip,
                                                                         variables_total_count=variables_total_count)
        for reviewComment in reviewComments:
            reviewCommentId = save_pr_review_comment(node=reviewComment, eventType=node["__typename"],
                                                     eventId=event["id"])
            num_updated = PullRequestReviewThread.objects(id=event["id"]). \
                update(add_to_set__reviewCommentIds=reviewCommentId)
            if num_updated != 1:
                raise Exception("PullRequestReview: Debug!")

    # Create a corresponding timelineItem to be pushed to the focal pullRequest
    timelineItem = TimelineItem(actor=None, actorType=None, createdAt=None,
                                eventType=node["__typename"], eventId=event["id"])

    return timelineItem


def save_commit_comment(node):
    """
    Save the associated commitComment in MongoDB and return the objectId
    :param node: GitHub node of the commitComment
    :return: ObjectId of the saved commitComment
    """
    author = node["author"]
    if not author:
        author = ""
        authorType = ""
    else:
        author = node["author"]["login"]
        authorType = node["author"]["__typename"]
    authorAssociation = node["authorAssociation"]

    commit = node["commit"]
    if not commit:
        commitOid = None
    else:
        commitOid = node["commit"]["oid"]
    path = node["path"]
    position = node["position"]

    repository = node["repository"]["nameWithOwner"]

    createdAt = node["createdAt"]
    createdViaEmail = node["createdViaEmail"]
    publishedAt = node["publishedAt"]
    updatedAt = node["updatedAt"]

    databaseId = node["databaseId"]
    resourcePath = node["resourcePath"]
    url = node["url"]

    isMinimized = node["isMinimized"]
    minimizedReason = node["minimizedReason"]

    body = node["body"]
    bodyHTML = node["bodyHTML"]
    bodyText = node["bodyText"]

    editor = node["editor"]
    if not editor:
        editor = ""
        editorType = ""
    else:
        editor = node["editor"]["login"]
        editorType = node["editor"]["__typename"]
    includesCreatedEdit = node["includesCreatedEdit"]
    lastEditedAt = node["lastEditedAt"]
    editCount = node["userContentEdits"]["totalCount"]

    event = CommitComment(author=author, authorType=authorType, authorAssociation=authorAssociation,
                          commitOid=commitOid, path=path, position=position, repository=repository,
                          createdAt=createdAt, createdViaEmail=createdViaEmail,
                          publishedAt=publishedAt, updatedAt=updatedAt,
                          databaseId=databaseId, resourcePath=resourcePath, url=url,
                          isMinimized=isMinimized, minimizedReason=minimizedReason,
                          body=body, bodyHTML=bodyHTML, bodyText=bodyText,
                          editor=editor, editorType=editorType, includesCreatedEdit=includesCreatedEdit,
                          lastEditedAt=lastEditedAt, editCount=editCount)
    event.save()

    # Update the userContentEdits (only the first 50), i.e., edits
    if node["userContentEdits"]["nodes"]:
        for edit in node["userContentEdits"]["nodes"]:  # If no nodes, it will the loop will not execute
            editor = edit["editor"]
            if not editor:
                editor = ""
                editorType = ""
            else:
                editor = edit["editor"]["login"]
                editorType = edit["editor"]["__typename"]
            edit_createdAt = edit["createdAt"]
            editedAt = edit["editedAt"]
            updatedAt = edit["updatedAt"]
            deletedAt = edit["deletedAt"]
            deletedBy = edit["deletedBy"]
            if not deletedBy:
                deletedBy = ""
                deletedByType = ""
            else:
                deletedBy = edit["deletedBy"]["login"]
                deletedByType = edit["deletedBy"]["__typename"]
            diff = edit["diff"]
            edit_obj = Edit(editor=editor, editorType=editorType, createdAt=edit_createdAt, editedAt=editedAt,
                            updatedAt=updatedAt, deletedAt=deletedAt, deletedBy=deletedBy,
                            deletedByType=deletedByType, diff=diff)
            num_updated = CommitComment.objects(id=event["id"]).update_one(push__edits=edit_obj)
            if num_updated != 1:
                raise Exception("Cannot find the commitComment to be updated!")

    # Update the reactionGroups of the issueComment; reactionGroups is a required field
    for reaction in node["reactionGroups"]:
        content = reaction["content"]
        reactionGroup_createdAt = reaction["createdAt"]
        userCount = reaction["users"]["totalCount"]
        reactionGroup = ReactionGroup(content=content, createdAt=reactionGroup_createdAt, userCount=userCount)
        num_updated = CommitComment.objects(id=event["id"]).update_one(push__reactionGroups=reactionGroup)
        if num_updated != 1:
            raise Exception("Cannot find the commitComment to be updated!")

    return event["id"]


def save_pr_review_comment(node, eventType, eventId):
    """
    Save the comments connection in PullRequestReview and PullRequestReviewThread
    :param node: node in comments
    :param eventType: PullRequestReview or PullRequestReviewThread type
    :param eventId: The eventId of the PullRequestReview or PullRequestReviewThread type
    :return:
    """
    author = node["author"]
    if not author:
        author = ""
        authorType = ""
    else:
        author = node["author"]["login"]
        authorType = node["author"]["__typename"]
    authorAssociation = node["authorAssociation"]

    commit = node["commit"]
    if not commit:
        commitOid = None
    else:
        commitOid = node["commit"]["oid"]

    originalCommit = node["originalCommit"]
    if not originalCommit:
        originalCommitOid = None
    else:
        originalCommitOid = node["originalCommit"]["oid"]

    diffHunk = node["diffHunk"]
    path = node["path"]
    position = node["position"]
    originalPosition = node["originalPosition"]

    outdated = node["outdated"]

    state = node["state"]

    createdAt = node["createdAt"]
    createdViaEmail = node["createdViaEmail"]
    publishedAt = node["publishedAt"]
    updatedAt = node["updatedAt"]
    draftedAt = node["draftedAt"]

    databaseId = node["databaseId"]
    resourcePath = node["resourcePath"]
    url = node["url"]

    isMinimized = node["isMinimized"]
    minimizedReason = node["minimizedReason"]

    body = node["body"]
    bodyHTML = node["bodyHTML"]
    bodyText = node["bodyText"]

    editor = node["editor"]
    if not editor:
        editor = ""
        editorType = ""
    else:
        editor = node["editor"]["login"]
        editorType = node["editor"]["__typename"]
    includesCreatedEdit = node["includesCreatedEdit"]
    lastEditedAt = node["lastEditedAt"]
    editCount = node["userContentEdits"]["totalCount"]

    # Associated pull request
    subjectType = node["pullRequest"]["__typename"]
    repository = node["pullRequest"]["repository"]["nameWithOwner"]
    number = node["pullRequest"]["number"]
    subjectId = get_issue_or_pr_id(type_issue_or_pr=subjectType, repository=repository, number=number)

    # pullRequestReviewId and pullRequestReviewThreadId
    if eventType == "PullRequestReview":
        pullRequestReviewId = eventId
        pullRequestReviewThreadId = None
    elif eventType == "PullRequestReviewThread":
        pullRequestReviewId = None
        pullRequestReviewThreadId = eventId
    else:
        raise Exception("Unexpected pullRequest eventType! Should be PullRequestReview or PullRequestReviewThread")

    # replyTo
    replyTo = node["replyTo"]
    if not replyTo:
        replyToCommentId = None
    else:
        author_reply = node["replyTo"]["author"]
        if not author_reply:
            author_reply = None
        else:
            author_reply = node["replyTo"]["author"]["login"]
        createdAt_reply = node["replyTo"]["createdAt"]
        body_reply = node["replyTo"]["body"]
        path = node["replyTo"]["path"]
        position = node["replyTo"]["position"]
        originalPosition = node["replyTo"]["originalPosition"]
        comments = PullRequestReviewComment.objects(author=author_reply, createdAt=createdAt_reply, body=body_reply,
                                                    path=path, position=position, originalPosition=originalPosition)
        if len(comments) == 1:
            replyToCommentId = comments[0]["id"]
        elif len(comments) == 0:
            replyToCommentId = save_pr_review_comment(node["replyTo"], eventType, eventId)
        else:
            raise Exception("Find multiple comment replied to with author: {}, createdAt: {}, body: {}".
                            format(author_reply, createdAt_reply, body_reply))

    event = PullRequestReviewComment(author=author, authorType=authorType, authorAssociation=authorAssociation,
                                     commitOid=commitOid, originalCommitOid=originalCommitOid,
                                     diffHunk=diffHunk, path=path, position=position, originalPosition=originalPosition,
                                     outdated=outdated, state=state,
                                     createdAt=createdAt, createdViaEmail=createdViaEmail,
                                     publishedAt=publishedAt, updatedAt=updatedAt, draftedAt=draftedAt,
                                     databaseId=databaseId, resourcePath=resourcePath, url=url,
                                     isMinimized=isMinimized, minimizedReason=minimizedReason,
                                     body=body, bodyHTML=bodyHTML, bodyText=bodyText,
                                     editor=editor, editorType=editorType, includesCreatedEdit=includesCreatedEdit,
                                     lastEditedAt=lastEditedAt, editCount=editCount,
                                     subjectType=subjectType, repository=repository, number=number, subjectId=subjectId,
                                     pullRequestReviewId=pullRequestReviewId,
                                     pullRequestReviewThreadId=pullRequestReviewThreadId,
                                     replyToCommentId=replyToCommentId)
    event.save()

    # Update the userContentEdits (only the first 50), i.e., edits
    for edit in node["userContentEdits"]["nodes"]:  # If no nodes, the loop will not execute
        editor = edit["editor"]
        if not editor:
            editor = ""
            editorType = ""
        else:
            editor = edit["editor"]["login"]
            editorType = edit["editor"]["__typename"]
        edit_createdAt = edit["createdAt"]
        editedAt = edit["editedAt"]
        updatedAt = edit["updatedAt"]
        deletedAt = edit["deletedAt"]
        deletedBy = edit["deletedBy"]
        if not deletedBy:
            deletedBy = ""
            deletedByType = ""
        else:
            deletedBy = edit["deletedBy"]["login"]
            deletedByType = edit["deletedBy"]["__typename"]
        diff = edit["diff"]
        edit_obj = Edit(editor=editor, editorType=editorType, createdAt=edit_createdAt, editedAt=editedAt,
                        updatedAt=updatedAt, deletedAt=deletedAt, deletedBy=deletedBy,
                        deletedByType=deletedByType, diff=diff)
        num_updated = PullRequestReviewComment.objects(id=event["id"]).update_one(push__edits=edit_obj)
        if num_updated != 1:
            raise Exception("Cannot find the commitComment to be updated!")

    # Update the reactionGroups of the issueComment; reactionGroups is a required field
    for reaction in node["reactionGroups"]:
        content = reaction["content"]
        reactionGroup_createdAt = reaction["createdAt"]
        userCount = reaction["users"]["totalCount"]
        reactionGroup = ReactionGroup(content=content, createdAt=reactionGroup_createdAt, userCount=userCount)
        num_updated = PullRequestReviewComment.objects(id=event["id"]).update_one(push__reactionGroups=reactionGroup)
        if num_updated != 1:
            raise Exception("Cannot find the commitComment to be updated!")

    return event["id"]


def fetch_commit_or_review_comments_with_pagination(skip, variables_total_count):
    comments = []
    # Identify the specific PullRequestCommitCommentThread, PullRequestReview, or PullRequestReviewThread
    query_comment_first_page = """
    query($owner: String!, $name: String!, $number: Int!, $first: Int!, $skip: Int!) {
      rateLimit{
        cost
        remaining
      }
      repository(owner: $owner, name: $name){
        pullRequest(number: $number){
          timelineItems(first: 1, skip: $skip){
            edges{
              cursor
              node{
                __typename
                ... on PullRequestCommitCommentThread{
                  comments(first: $first){
                    totalCount
                    pageInfo{
                      hasNextPage
                      endCursor
                    }
                    nodes{
                      ...commitComment
                    }
                  }
    
                }
    
                ... on PullRequestReview{
                  comments(first: $first){
                    totalCount
                    pageInfo{
                      hasNextPage
                      endCursor
                    }
                    nodes{
                      ...reviewComment
                      replyTo{
                        ...reviewComment
                        replyTo{
                          ...reviewComment
                        }
                      }
                    }
                  }
    
                }
    
                ... on PullRequestReviewThread{
                  comments(first: $first){
                    totalCount
                    pageInfo{
                      hasNextPage
                      endCursor
                    }
                    nodes{
                      ...reviewComment
                      replyTo{
                        ...reviewComment
                        replyTo{
                          ...reviewComment
                        }
                      }
                    }
                  }
    
                }
    
              }
    
            }
          }
        }
      }
    }
    
    fragment reviewComment on PullRequestReviewComment{
      author{
        login
        __typename
      }
      authorAssociation
      commit{
        oid
      }
      originalCommit{
        oid
      }
      diffHunk
      path
      position
      originalPosition
      outdated
      state
      createdAt
      createdViaEmail
      publishedAt
      updatedAt
      draftedAt
      databaseId
      resourcePath
      url
      isMinimized
      minimizedReason
      body
      bodyHTML
      bodyText
      editor{
        login
        __typename
      }
      includesCreatedEdit
      lastEditedAt
      userContentEdits(first: 50){
        totalCount
        pageInfo{
          hasNextPage
          endCursor
        }
        nodes{
          editor{
            login
            __typename
          }
          createdAt
          editedAt
          updatedAt
          deletedAt
          deletedBy{
            login
            __typename
          }
          diff
        }
      }
      reactionGroups{
        content
        createdAt
        users{
          totalCount
        }
      }
      pullRequest{
        __typename
        repository{
          nameWithOwner
        }
        number
      }
    }
    
    fragment commitComment on CommitComment{
      author{
        login
        __typename
      }
      authorAssociation
      commit{
        oid
      }
      path
      position
      repository{
        nameWithOwner
      }
      createdAt
      createdViaEmail
      publishedAt
      updatedAt
      databaseId
      resourcePath
      url
      isMinimized
      minimizedReason
      body
      bodyHTML
      bodyText
      editor{
        login
        __typename
      }
      includesCreatedEdit
      lastEditedAt
      userContentEdits(first:50){
        totalCount
        nodes{
          editor{
            login
            __typename
          }
          createdAt
          editedAt
          updatedAt
          deletedAt
          deletedBy{
            login
            __typename
          }
          diff
        }
      }
      reactionGroups{
        content
        createdAt
        users{
          totalCount
        }
      }
    }
    """
    variables_comment_first_page = {
        "owner": variables_total_count["owner"],
        "name": variables_total_count["name"],
        "number": variables_total_count["number"],
        "first": first,
        "skip": skip
    }
    hasNextPage, endCursor, nodes = fetch_comment_nodes(query_comment_first_page, variables_comment_first_page)
    comments.extend(nodes)

    after_cursor = endCursor

    while hasNextPage:
        query_comment_next_page = """
        query($owner: String!, $name: String!, $number: Int!, $first: Int!, $skip: Int!, $after_cursor: String!) {
          rateLimit{
            cost
            remaining
          }
          repository(owner: $owner, name: $name){
            pullRequest(number: $number){
              timelineItems(first: 1, skip: $skip){
                edges{
                  cursor
                  node{
                    __typename
                    ... on PullRequestCommitCommentThread{
                      comments(first: $first, after: $after_cursor){
                        totalCount
                        pageInfo{
                          hasNextPage
                          endCursor
                        }
                        nodes{
                          ...commitComment
                        }
                      }
    
                    }
    
                    ... on PullRequestReview{
                      comments(first: $first, after: $after_cursor){
                        totalCount
                        pageInfo{
                          hasNextPage
                          endCursor
                        }
                        nodes{
                          ...reviewComment
                          replyTo{
                            ...reviewComment
                            replyTo{
                              ...reviewComment
                            }
                          }
                        }
                      }
    
                    }
    
                    ... on PullRequestReviewThread{
                      comments(first: $first, after: $after_cursor){
                        totalCount
                        pageInfo{
                          hasNextPage
                          endCursor
                        }
                        nodes{
                          ...reviewComment
                          replyTo{
                            ...reviewComment
                            replyTo{
                              ...reviewComment
                            }
                          }
                        }
                      }
    
                    }
    
                  }
    
                }
              }
            }
          }
        }
    
        fragment reviewComment on PullRequestReviewComment{
          author{
            login
            __typename
          }
          authorAssociation
          commit{
            oid
          }
          originalCommit{
            oid
          }
          diffHunk
          path
          position
          originalPosition
          outdated
          state
          createdAt
          createdViaEmail
          publishedAt
          updatedAt
          draftedAt
          databaseId
          resourcePath
          url
          isMinimized
          minimizedReason
          body
          bodyHTML
          bodyText
          editor{
            login
            __typename
          }
          includesCreatedEdit
          lastEditedAt
          userContentEdits(first: 50){
            totalCount
            pageInfo{
              hasNextPage
              endCursor
            }
            nodes{
              editor{
                login
                __typename
              }
              createdAt
              editedAt
              updatedAt
              deletedAt
              deletedBy{
                login
                __typename
              }
              diff
            }
          }
          reactionGroups{
            content
            createdAt
            users{
              totalCount
            }
          }
          pullRequest{
            __typename
            repository{
              nameWithOwner
            }
            number
          }
        }
        
        fragment commitComment on CommitComment{
          author{
            login
            __typename
          }
          authorAssociation
          commit{
            oid
          }
          path
          position
          repository{
            nameWithOwner
          }
          createdAt
          createdViaEmail
          publishedAt
          updatedAt
          databaseId
          resourcePath
          url
          isMinimized
          minimizedReason
          body
          bodyHTML
          bodyText
          editor{
            login
            __typename
          }
          includesCreatedEdit
          lastEditedAt
          userContentEdits(first:50){
            totalCount
            nodes{
              editor{
                login
                __typename
              }
              createdAt
              editedAt
              updatedAt
              deletedAt
              deletedBy{
                login
                __typename
              }
              diff
            }
          }
          reactionGroups{
            content
            createdAt
            users{
              totalCount
            }
          }
        }
        """
        variables_comment_next_page = {
            "owner": variables_total_count["owner"],
            "name": variables_total_count["name"],
            "number": variables_total_count["number"],
            "first": first,
            "skip": skip,
            "after_cursor": after_cursor
        }
        hasNextPage, endCursor, nodes = fetch_comment_nodes(query_comment_next_page, variables_comment_next_page)
        after_cursor = endCursor
        comments.extend(nodes)

    return comments


def fetch_comment_nodes(query, variables):
    if get_remaining() < cost:
        sleep = sleep_in_seconds(get_reset())
        print("Need to sleep about {} minutes to reset the 5000 scores".format(str(sleep / 60)))
        time.sleep(sleep)
        print("Restart! :-)")

    result = run_query_variable(query, variables)

    if not result["data"]["repository"]:
        raise Exception("Repository not found")

    eventType = result["data"]["repository"]["pullRequest"]["timelineItems"]["edges"][0]["node"]["__typename"]
    if eventType != "PullRequestCommitCommentThread" and eventType != "PullRequestReview" and eventType != \
            "PullRequestReviewThread":
        raise Exception("Cannot get comments for {} type of event!".format(eventType))

    hasNextPage = result["data"]["repository"]["pullRequest"]["timelineItems"]["edges"][0]["node"]["comments"]["pageInfo"]["hasNextPage"]
    endCursor = result["data"]["repository"]["pullRequest"]["timelineItems"]["edges"][0]["node"]["comments"]["pageInfo"]["endCursor"]
    nodes = result["data"]["repository"]["pullRequest"]["timelineItems"]["edges"][0]["node"]["comments"]["nodes"]

    return hasNextPage, endCursor, nodes


def read_json_file(path):
    # read a list of dictionaries
    with open(path) as json_file:
        data = json.load(json_file)  # if data is a list
        for p in data:
            print(p["owner"])
