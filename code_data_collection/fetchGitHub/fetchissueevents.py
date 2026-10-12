import time

from Classes.event.assign.assigned import AssignedEvent
from Classes.event.assign.unassigned import UnassignedEvent
from Classes.event.comment.commentdeleted import CommentDeletedEvent
from Classes.event.comment.issuecomment import IssueComment
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
from Classes.event.subscription.subscribed import SubscribedEvent
from Classes.event.subscription.unsubscribed import UnsubscribedEvent
from Classes.event.title.renamedtitle import RenamedTitleEvent
from Classes.event.userblock.userblocked import UserBlockedEvent
from Classes.issuecollection.edit import Edit
from Classes.issuecollection.issue import Issue
from Classes.issuecollection.pullrequest import PullRequest
from Classes.issuecollection.reactiongroup import ReactionGroup
from Classes.issuecollection.timelineitem import TimelineItem
from setup.graphql import run_query_variable, get_remaining, sleep_in_seconds, get_reset

first = 10
cost = 3


# Update 30 types of TimelineItem objects associated with an issue
def update_issue_timeline(owner, name, number):
    print("Working on issue #{} of repo {}/{}".format(str(number), owner, name))

    variables_total_count = {
        "owner": owner,
        "name": name,
        "number": number
    }

    # Get nodes of timelineItems associated with the specific issue
    query_total_count = """
    query($owner: String!, $name: String!, $number: Int!) {
      repository(owner: $owner, name: $name){
        issue(number: $number){
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
        issue(number: $number){
          timelineItems(first: $first){
            totalCount
            pageInfo{
              hasNextPage
              endCursor
            }
            nodes{
              
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
                  ... on Issue{
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
                  ... on Issue{
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
                issue{
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
        issue(number: $number){
          timelineItems(first: $first, after: $after_cursor){
            totalCount
            pageInfo{
              hasNextPage
              endCursor
            }
            nodes{
              
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
                  ... on Issue{
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
                  ... on Issue{
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
                issue{
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
              
            }
          }
        }
      }
    }
    """
    fetch_with_pagination(query_total_count=query_total_count, variables_total_count=variables_total_count,
                          query_first_page=query_first_page, query_next_page=query_next_page)


def fetch_with_pagination(query_total_count, variables_total_count, query_first_page, query_next_page):
    events = []

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

    total_count = result["data"]["repository"]["issue"]["timelineItems"]["totalCount"]
    print("There are in total {} timeline items.".format(str(total_count)))

    if total_count == 0:
        print("------------------------------------------------------------")
        return

    # ------------------------------------
    # Traverse the list by pagination

    page = 1
    variables_first_page = variables_total_count
    variables_first_page["first"] = first

    hasNextPage, endCursor, nodes = fetch_event_nodes(query=query_first_page, variables=variables_first_page)
    events.extend(nodes)

    after_cursor = endCursor
    variables_next_page = variables_total_count
    variables_next_page["after_cursor"] = after_cursor
    while hasNextPage:
        page = page + 1
        hasNextPage, after_cursor, nodes = fetch_event_nodes(query=query_next_page, variables=variables_next_page)
        variables_next_page["after_cursor"] = after_cursor
        events.extend(nodes)

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
        "UserBlockedEvent": 0
    }
    for event in events:
        eventType = event["__typename"]
        if eventType == "AssignedEvent":
            save_assigned_event(event)
        elif eventType == "UnassignedEvent":
            save_unassigned_event(event)
        elif eventType == "IssueComment":
            save_issue_comment(event)
        elif eventType == "CommentDeletedEvent":
            save_comment_deleted_event(event, variables_total_count)
        elif eventType == "ConnectedEvent":
            save_connected_event(event)
        elif eventType == "DisconnectedEvent":
            save_disconnected_event(event)
        elif eventType == "CrossReferencedEvent":
            save_cross_referenced_event(event)
        elif eventType == "ReferencedEvent":
            save_referenced_event(event)
        elif eventType == "TransferredEvent":
            save_transferred_event(event)
        elif eventType == "LabeledEvent":
            save_labeled_event(event)
        elif eventType == "UnlabeledEvent":
            save_unlabeled_event(event)
        elif eventType == "MentionedEvent":
            save_mentioned_event(event, variables_total_count)
        elif eventType == "MilestonedEvent":
            save_milestoned_event(event)
        elif eventType == "DemilestonedEvent":
            save_demilestoned_event(event)
        elif eventType == "ClosedEvent":
            save_closed_event(event)
        elif eventType == "ReopenedEvent":
            save_reopened_event(event)
        elif eventType == "LockedEvent":
            save_locked_event(event)
        elif eventType == "UnlockedEvent":
            save_unlocked_event(event)
        elif eventType == "PinnedEvent":
            save_pinned_event(event)
        elif eventType == "UnpinnedEvent":
            save_unpinned_event(event)
        elif eventType == "MarkedAsDuplicateEvent":
            save_marked_as_duplicate_event(event, variables_total_count)
        elif eventType == "UnmarkedAsDuplicateEvent":
            save_unmarked_as_duplicate_event(event, variables_total_count)
        elif eventType == "AddedToProjectEvent":
            save_added_to_project_event(event, variables_total_count)
        elif eventType == "RemovedFromProjectEvent":
            save_removed_from_project_event(event, variables_total_count)
        elif eventType == "MovedColumnsInProjectEvent":
            save_moved_columns_in_project_event(event, variables_total_count)
        elif eventType == "ConvertedNoteToIssueEvent":
            save_converted_note_to_issue_event(event, variables_total_count)
        elif eventType == "SubscribedEvent":
            save_subscribed_event(event)
        elif eventType == "UnsubscribedEvent":
            save_unsubscribed_event(event)
        elif eventType == "RenamedTitleEvent":
            save_renamed_title_event(event)
        elif eventType == "UserBlockedEvent":
            save_user_blocked_event(event, variables_total_count)
        else:
            raise Exception("{} is an unexpected event type of issue timeline items".format(eventType))
        count[eventType] = count[eventType] + 1

    print("------------------------------------------------------------")
    print("{} events are added to the timeline of issue #{} in repo {}/{} -- MongoDB database".
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
    :param cost: Estimated cost of this call
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

    if not result["data"]["repository"]:
        raise Exception("Repository not found")
    else:
        hasNextPage = result["data"]["repository"]["issue"]["timelineItems"]["pageInfo"]["hasNextPage"]
        endCursor = result["data"]["repository"]["issue"]["timelineItems"]["pageInfo"]["endCursor"]
        nodes = result["data"]["repository"]["issue"]["timelineItems"]["nodes"]

        return hasNextPage, endCursor, nodes


def save_assigned_event(node):
    """
    Save the event objects/documents and save the timeline items of those events
    :param node: Node of the event
    :return: No return; the information is saved in the MongoDB database
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

    # Save the event object info in the timeline
    eventId = event["id"]  # Note that in Mongoengine the auto ID is "id"; in mongo shell, it is "_id"
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=eventId)
    num_updated = Issue.objects(repository=repository, number=number).update_one(push__timeline=timelineItem)
    if num_updated != 1:
        raise Exception("No issue with number {} in repo {} -- MongoDB database".format(str(number), repository))


def save_unassigned_event(node):
    """
    Save the event objects/documents and save the timeline items of those events
    :param node: Node of the event
    :return: No return; the information is saved in the MongoDB database
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

    # Save the event object info in the timeline
    eventId = event["id"]  # Note that in Mongoengine the auto ID is "id"; in mongo shell, it is "_id"
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=eventId)
    num_updated = Issue.objects(repository=repository, number=number).update_one(push__timeline=timelineItem)
    if num_updated != 1:
        raise Exception("No issue with number {} in repo {} -- MongoDB database".format(str(number), repository))


def save_issue_comment(node):
    """
    Save the event objects/documents and save the timeline items of those events
    :param node: Node of the event
    :return: No return; the information is saved in the MongoDB database
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

    subjectType = node["issue"]["__typename"]
    repository = node["issue"]["repository"]["nameWithOwner"]
    number = node["issue"]["number"]
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

    # Save the event object info in the timeline
    eventId = event["id"]  # Note that in Mongoengine the auto ID is "id"; in mongo shell, it is "_id"
    timelineItem = TimelineItem(actor=author, actorType=authorType, createdAt=node["createdAt"],
                                eventType=node["__typename"], eventId=eventId)
    num_updated = Issue.objects(repository=repository, number=number).update_one(push__timeline=timelineItem)
    if num_updated != 1:
        raise Exception("No issue with number {} in repo {} -- MongoDB database".format(str(number), repository))


def save_comment_deleted_event(node, variables_total_count):
    """
    Save the event objects/documents and save the timeline items of those events
    :param variables_total_count: information about issue number as well as repository owner and name
    :param node: Node of the event
    :return: No return; the information is saved in the MongoDB database
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

    event = CommentDeletedEvent(actor=actor, actorType=actorType, createdAt=createdAt, databaseId=databaseId,
                                subjectType=subjectType, repository=repository, number=number, subjectId=subjectId)
    event.save()

    # Save the corresponding timelineItem
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])
    num_updated = Issue.objects(repository=repository, number=number).update_one(push__timeline=timelineItem)
    if num_updated != 1:
        raise Exception("No issue with number {} in repo {} -- MongoDB database".format(str(number), repository))


def save_connected_event(node):
    """
    Save the event objects/documents and save the timeline items of those events
    :param node: Node of the event
    :return: No return; the information is saved in the MongoDB database
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

    # Save the corresponding timelineItem
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])
    num_updated = Issue.objects(repository=sourceRepository, number=sourceNumber).\
        update_one(push__timeline=timelineItem)
    if num_updated != 1:
        raise Exception("No issue with number {} in repo {} -- MongoDB database".
                        format(str(sourceNumber), sourceRepository))


def save_disconnected_event(node):
    """
    Save the event objects/documents and save the timeline items of those events
    :param node: Node of the event
    :return: No return; the information is saved in the MongoDB database
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

    # Save the corresponding timelineItem
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])
    num_updated = Issue.objects(repository=sourceRepository, number=sourceNumber). \
        update_one(push__timeline=timelineItem)
    if num_updated != 1:
        raise Exception("No issue with number {} in repo {} -- MongoDB database".
                        format(str(sourceNumber), sourceRepository))


def save_cross_referenced_event(node):
    """
    Save the event objects/documents and save the timeline items of those events
    :param node: Node of the event
    :return: No return; the information is saved in the MongoDB database
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

    # Save the corresponding timelineItem
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])
    num_updated = Issue.objects(repository=targetRepository, number=targetNumber). \
        update_one(push__timeline=timelineItem)
    if num_updated != 1:
        raise Exception("No issue with number {} in repo {} -- MongoDB database".
                        format(str(sourceNumber), sourceRepository))


def save_referenced_event(node):
    """
    Save the event objects/documents and save the timeline items of those events
    :param node: Node of the event
    :return: No return; the information is saved in the MongoDB database
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

    # Save the corresponding timeline item
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])
    num_updated = Issue.objects(repository=repository, number=number).update_one(push__timeline=timelineItem)
    if num_updated != 1:
        raise Exception("No issue with number {} in repo {} -- MongoDB database".
                        format(str(number), repository))


def save_transferred_event(node):
    """
    Save the event objects/documents and save the timeline items of those events
    :param node: Node of the event
    :return: No return; the information is saved in the MongoDB database
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

    subjectType = node["issue"]["__typename"]
    repository = node["issue"]["repository"]["nameWithOwner"]
    number = node["issue"]["number"]
    subjectId = get_issue_or_pr_id(type_issue_or_pr=subjectType, repository=repository, number=number)

    event = TransferredEvent(actor=actor, actorType=actorType, createdAt=createdAt, fromRepository=fromRepository,
                             subjectType=subjectType, repository=repository,
                             number=number, subjectId=subjectId)
    event.save()

    # Save the corresponding timelineItem
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])
    num_updated = Issue.objects(repository=repository, number=number). \
        update_one(push__timeline=timelineItem)
    if num_updated != 1:
        raise Exception("No issue with number {} in repo {} -- MongoDB database".
                        format(str(number), repository))


def save_labeled_event(node):
    """
    Save the event objects/documents and save the timeline items of those events
    :param node: Node of the event
    :return: No return; the information is saved in the MongoDB database
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

    # Save the corresponding timelineItem
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])
    num_updated = Issue.objects(repository=repository, number=number). \
        update_one(push__timeline=timelineItem)
    if num_updated != 1:
        raise Exception("No issue with number {} in repo {} -- MongoDB database".
                        format(str(number), repository))


def save_unlabeled_event(node):
    """
    Save the event objects/documents and save the timeline items of those events
    :param node: Node of the event
    :return: No return; the information is saved in the MongoDB database
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

    # Save the corresponding timelineItem
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])
    num_updated = Issue.objects(repository=repository, number=number). \
        update_one(push__timeline=timelineItem)
    if num_updated != 1:
        raise Exception("No issue with number {} in repo {} -- MongoDB database".
                        format(str(number), repository))


def save_mentioned_event(node, variables_total_count):
    """
    Save the event objects/documents and save the timeline items of those events
    :param variables_total_count: information about repository owner and name as well as issue number
    :param node: Node of the event
    :return: No return; the information is saved in the MongoDB database
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

    event = MentionedEvent(actor=actor, actorType=actorType, createdAt=createdAt, databaseId=databaseId,
                           subjectType=subjectType, repository=repository, number=number, subjectId=subjectId)
    event.save()

    # Save the corresponding timelineItem
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])
    num_updated = Issue.objects(repository=repository, number=number).update_one(push__timeline=timelineItem)
    if num_updated != 1:
        raise Exception("No issue with number {} in repo {} -- MongoDB database".format(str(number), repository))


def save_milestoned_event(node):
    """
    Save the event objects/documents and save the timeline items of those events
    :param node: Node of the event
    :return: No return; the information is saved in the MongoDB database
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

    # Save the corresponding timelineItem
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])
    num_updated = Issue.objects(repository=repository, number=number).update_one(push__timeline=timelineItem)
    if num_updated != 1:
        raise Exception("No issue with number {} in repo {} -- MongoDB database".format(str(number), repository))


def save_demilestoned_event(node):
    """
    Save the event objects/documents and save the timeline items of those events
    :param node: Node of the event
    :return: No return; the information is saved in the MongoDB database
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

    # Save the corresponding timelineItem
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])
    num_updated = Issue.objects(repository=repository, number=number).update_one(push__timeline=timelineItem)
    if num_updated != 1:
        raise Exception("No issue with number {} in repo {} -- MongoDB database".format(str(number), repository))


def save_closed_event(node):
    """
    Save the event objects/documents and save the timeline items of those events
    :param node: Node of the event
    :return: No return; the information is saved in the MongoDB database
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

    # Save the corresponding timelineItem
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])
    num_updated = Issue.objects(repository=repository, number=number).update_one(push__timeline=timelineItem)
    if num_updated != 1:
        raise Exception("No issue with number {} in repo {} -- MongoDB database".format(str(number), repository))


def save_reopened_event(node):
    """
    Save the event objects/documents and save the timeline items of those events
    :param node: Node of the event
    :return: No return; the information is saved in the MongoDB database
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

    # Save the corresponding timelineItem
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])
    num_updated = Issue.objects(repository=repository, number=number).update_one(push__timeline=timelineItem)
    if num_updated != 1:
        raise Exception("No issue with number {} in repo {} -- MongoDB database".format(str(number), repository))


def save_locked_event(node):
    """
    Save the event objects/documents and save the timeline items of those events
    :param node: Node of the event
    :return: No return; the information is saved in the MongoDB database
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

    # Save the corresponding timelineItem
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])
    num_updated = Issue.objects(repository=repository, number=number).update_one(push__timeline=timelineItem)
    if num_updated != 1:
        raise Exception("No issue with number {} in repo {} -- MongoDB database".format(str(number), repository))


def save_unlocked_event(node):
    """
    Save the event objects/documents and save the timeline items of those events
    :param node: Node of the event
    :return: No return; the information is saved in the MongoDB database
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

    # Save the corresponding timelineItem
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])
    num_updated = Issue.objects(repository=repository, number=number).update_one(push__timeline=timelineItem)
    if num_updated != 1:
        raise Exception("No issue with number {} in repo {} -- MongoDB database".format(str(number), repository))


def save_pinned_event(node):
    """
    Save the event objects/documents and save the timeline items of those events
    :param node: Node of the event
    :return: No return; the information is saved in the MongoDB database
    """
    actor = node["actor"]
    if not actor:
        actor = ""
        actorType = ""
    else:
        actor = node["actor"]["login"]
        actorType = node["actor"]["__typename"]
    createdAt = node["createdAt"]

    subjectType = node["issue"]["__typename"]
    repository = node["issue"]["repository"]["nameWithOwner"]
    number = node["issue"]["number"]
    subjectId = get_issue_or_pr_id(type_issue_or_pr=subjectType, repository=repository, number=number)

    event = PinnedEvent(actor=actor, actorType=actorType, createdAt=createdAt,
                        subjectType=subjectType, repository=repository, number=number, subjectId=subjectId)
    event.save()

    # Save the corresponding timelineItem
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])
    num_updated = Issue.objects(repository=repository, number=number). \
        update_one(push__timeline=timelineItem)
    if num_updated != 1:
        raise Exception("No issue with number {} in repo {} -- MongoDB database".
                        format(str(number), repository))


def save_unpinned_event(node):
    """
    Save the event objects/documents and save the timeline items of those events
    :param node: Node of the event
    :return: No return; the information is saved in the MongoDB database
    """
    actor = node["actor"]
    if not actor:
        actor = ""
        actorType = ""
    else:
        actor = node["actor"]["login"]
        actorType = node["actor"]["__typename"]
    createdAt = node["createdAt"]

    subjectType = node["issue"]["__typename"]
    repository = node["issue"]["repository"]["nameWithOwner"]
    number = node["issue"]["number"]
    subjectId = get_issue_or_pr_id(type_issue_or_pr=subjectType, repository=repository, number=number)

    event = UnpinnedEvent(actor=actor, actorType=actorType, createdAt=createdAt,
                        subjectType=subjectType, repository=repository, number=number, subjectId=subjectId)
    event.save()

    # Save the corresponding timelineItem
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])
    num_updated = Issue.objects(repository=repository, number=number). \
        update_one(push__timeline=timelineItem)
    if num_updated != 1:
        raise Exception("No issue with number {} in repo {} -- MongoDB database".
                        format(str(number), repository))


def save_marked_as_duplicate_event(node, variables_total_count):
    """
    Save the event objects/documents and save the timeline items of those events
    :param variables_total_count: information about the focal issue number and repository
    :param node: Node of the event
    :return: No return; the information is saved in the MongoDB database
    """
    actor = node["actor"]
    if not actor:
        actor = ""
        actorType = ""
    else:
        actor = node["actor"]["login"]
        actorType = node["actor"]["__typename"]
    createdAt = node["createdAt"]

    subjectType = "Issue"
    repository = variables_total_count["owner"] + "/" + variables_total_count["name"]
    number = variables_total_count["number"]
    subjectId = get_issue_or_pr_id(type_issue_or_pr=subjectType, repository=repository, number=number)

    event = MarkedAsDuplicateEvent(actor=actor, actorType=actorType, createdAt=createdAt,
                                   subjectType=subjectType, repository=repository, number=number, subjectId=subjectId)
    event.save()

    # Save the corresponding timelineItem
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])
    num_updated = Issue.objects(repository=repository, number=number).update_one(push__timeline=timelineItem)
    if num_updated != 1:
        raise Exception("No issue with number {} in repo {} -- MongoDB database".format(str(number), repository))


def save_unmarked_as_duplicate_event(node, variables_total_count):
    """
    Save the event objects/documents and save the timeline items of those events
    :param variables_total_count: information about the focal issue and repository
    :param node: Node of the event
    :return: No return; the information is saved in the MongoDB database
    """
    actor = node["actor"]
    if not actor:
        actor = ""
        actorType = ""
    else:
        actor = node["actor"]["login"]
        actorType = node["actor"]["__typename"]
    createdAt = node["createdAt"]

    subjectType = "Issue"
    repository = variables_total_count["owner"] + "/" + variables_total_count["name"]
    number = variables_total_count["number"]
    subjectId = get_issue_or_pr_id(type_issue_or_pr=subjectType, repository=repository, number=number)

    event = UnmarkedAsDuplicateEvent(actor=actor, actorType=actorType, createdAt=createdAt,
                                     subjectType=subjectType, repository=repository, number=number, subjectId=subjectId)
    event.save()

    # Save the corresponding timelineItem
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])
    num_updated = Issue.objects(repository=repository, number=number).update_one(push__timeline=timelineItem)
    if num_updated != 1:
        raise Exception("No issue with number {} in repo {} -- MongoDB database".format(str(number), repository))


def save_added_to_project_event(node, variables_total_count):
    """
    Save the event objects/documents and save the timeline items of those events
    :param variables_total_count: information about the focal issue and repository
    :param node: Node of the event
    :return: No return; the information is saved in the MongoDB database
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

    event = AddedToProjectEvent(actor=actor, actorType=actorType, createdAt=createdAt, databaseId=databaseId,
                                subjectType=subjectType, repository=repository, number=number, subjectId=subjectId)
    event.save()

    # Save the corresponding timelineItem
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])
    num_updated = Issue.objects(repository=repository, number=number).update_one(push__timeline=timelineItem)
    if num_updated != 1:
        raise Exception("No issue with number {} in repo {} -- MongoDB database".format(str(number), repository))


def save_removed_from_project_event(node, variables_total_count):
    """
    Save the event objects/documents and save the timeline items of those events
    :param variables_total_count: information about the focal issue and repository
    :param node: Node of the event
    :return: No return; the information is saved in the MongoDB database
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

    event = RemovedFromProjectEvent(actor=actor, actorType=actorType, createdAt=createdAt, databaseId=databaseId,
                                    subjectType=subjectType, repository=repository, number=number, subjectId=subjectId)
    event.save()

    # Save the corresponding timelineItem
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])
    num_updated = Issue.objects(repository=repository, number=number).update_one(push__timeline=timelineItem)
    if num_updated != 1:
        raise Exception("No issue with number {} in repo {} -- MongoDB database".format(str(number), repository))


def save_moved_columns_in_project_event(node, variables_total_count):
    """
    Save the event objects/documents and save the timeline items of those events
    :param variables_total_count: information about the focal issue and repository
    :param node: Node of the event
    :return: No return; the information is saved in the MongoDB database
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

    event = MovedColumnsInProjectEvent(actor=actor, actorType=actorType, createdAt=createdAt, databaseId=databaseId,
                                       subjectType=subjectType, repository=repository, number=number,
                                       subjectId=subjectId)
    event.save()

    # Save the corresponding timelineItem
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])
    num_updated = Issue.objects(repository=repository, number=number).update_one(push__timeline=timelineItem)
    if num_updated != 1:
        raise Exception("No issue with number {} in repo {} -- MongoDB database".format(str(number), repository))


def save_converted_note_to_issue_event(node, variables_total_count):
    """
    Save the event objects/documents and save the timeline items of those events
    :param variables_total_count: information about the focal issue and repository
    :param node: Node of the event
    :return: No return; the information is saved in the MongoDB database
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

    # Save the corresponding timelineItem
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])
    num_updated = Issue.objects(repository=repository, number=number).update_one(push__timeline=timelineItem)
    if num_updated != 1:
        raise Exception("No issue with number {} in repo {} -- MongoDB database".format(str(number), repository))


def save_subscribed_event(node):
    """
    Save the event objects/documents and save the timeline items of those events
    :param node: Node of the event
    :return: No return; the information is saved in the MongoDB database
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

    # Save the corresponding timelineItem
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])
    num_updated = Issue.objects(repository=repository, number=number).update_one(push__timeline=timelineItem)
    if num_updated != 1:
        raise Exception("No issue with number {} in repo {} -- MongoDB database".format(str(number), repository))


def save_unsubscribed_event(node):
    """
    Save the event objects/documents and save the timeline items of those events
    :param node: Node of the event
    :return: No return; the information is saved in the MongoDB database
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

    # Save the corresponding timelineItem
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])
    num_updated = Issue.objects(repository=repository, number=number).update_one(push__timeline=timelineItem)
    if num_updated != 1:
        raise Exception("No issue with number {} in repo {} -- MongoDB database".format(str(number), repository))


def save_renamed_title_event(node):
    """
    Save the event objects/documents and save the timeline items of those events
    :param node: Node of the event
    :return: No return; the information is saved in the MongoDB database
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

    # Save the corresponding timelineItem
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])
    num_updated = Issue.objects(repository=repository, number=number).update_one(push__timeline=timelineItem)
    if num_updated != 1:
        raise Exception("No issue with number {} in repo {} -- MongoDB database".format(str(number), repository))


def save_user_blocked_event(node, variables_total_count):
    """
    Save the event objects/documents and save the timeline items of those events
    :param node: Node of the event
    :param variables_total_count: information about the focal issue and repository
    :return: No return; the information is saved in the MongoDB database
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

    subjectType = "Issue"
    repository = variables_total_count["owner"] + "/" + variables_total_count["name"]
    number = variables_total_count["number"]
    subjectId = get_issue_or_pr_id(type_issue_or_pr=subjectType, repository=repository, number=number)

    event = UserBlockedEvent(actor=actor, actorType=actorType, createdAt=createdAt,
                             blockDuration=blockDuration, blockedUser=blockedUser, blockedUserType=blockedUserType,
                             subjectType=subjectType, repository=repository, number=number, subjectId=subjectId)
    event.save()

    # Save the corresponding timelineItem
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])
    num_updated = Issue.objects(repository=repository, number=number).update_one(push__timeline=timelineItem)
    if num_updated != 1:
        raise Exception("No issue with number {} in repo {} -- MongoDB database".format(str(number), repository))


def get_issue_or_pr_id(type_issue_or_pr, repository, number):
    """
    Return the objectId of an issue or a pullRequest
    :param type_issue_or_pr: Issue or PullRequest
    :param repository: owner/name
    :param number: int
    :return: The objectId of the searched issue or pullRequest
    """
    if type_issue_or_pr == "Issue":
        issue = Issue.objects(repository=repository, number=number).only("id")
        if len(issue) == 1:
            obj_id = issue[0]["id"]
        else:
            raise Exception("There are no {} or multiple {} with number {} in repo {} -- MongoDB database".
                            format(type_issue_or_pr, type_issue_or_pr, str(number), repository))
    elif type_issue_or_pr == "PullRequest":
        pr = PullRequest.objects(repository=repository, number=number).only("id")
        if len(pr) == 1:
            obj_id = pr[0]["id"]
        else:
            raise Exception("There are no {} or multiple {} with number {} in repo {} -- MongoDB database".
                            format(type_issue_or_pr, type_issue_or_pr, str(number), repository))
    else:
        raise Exception("{} type is not expected. Only Issue or PullRequest are expected.".format(type_issue_or_pr))

    return obj_id
