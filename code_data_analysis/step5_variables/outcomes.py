"""
Step 5a. OSS development performance: speed (outputs per day), novelty (count of NewFeature
outputs), quality (count of BugFixing outputs).
"""

from classes.releasecycle.release_cycle import ReleaseCycle
from classes.releasecycle.release_cycle import ReleaseCycleInvolvedPullRequest


def calculate_performance_outcomes(repository, cycleNumber, startTime, endTime, days):
    # Get all involved pull request of the release cycle
    invPRs = ReleaseCycleInvolvedPullRequest.objects(repository=repository, cycleNumber=cycleNumber)
    num_invPRs = len(invPRs)

    if num_invPRs < 1:
        return

    # num_outputs, speed, novelty, quality
    num_outputs = 0
    novelty = 0
    quality = 0
    for pr in invPRs:
        isResolved = pr['isResolved']
        if isResolved is not None and isResolved is True:
            # isResolved can be
            # (1) none if the pr has only comments in the focal release cycle,
            # (2) False if developers made commits but did not merge the work,
            # (3) True if developers made commits and merged the work
            output_type = pr['output_type']
            num_outputs = num_outputs + 1
            if output_type == 'NewFeature':
                novelty = novelty + 1
            elif output_type == 'BugFixing':
                quality = quality + 1
            if not pr["mergedLines"] and pr["mergedLines"] != 0:  # Mark missing value due to GitHub restrictions
                # that we cannot fetch how many lines are changed
                # Note that not issue["mergedLines"] is True if issue["mergedLines"] = 0
                num_updated = ReleaseCycle.objects(repository=repository, cycleNumber=cycleNumber).update(
                    set__hasNoChangeInfo=True
                )
                if num_updated != 1:
                    raise Exception("Debug calculate_productivity(case)!!")
                return  # Those that have missing values due to GitHub restrictions are skipped
    # calculate speed
    if days != 0:
        speed = num_outputs / days
        speed_NewFeature = novelty / days
        speed_BugFixing = quality / days
    else:
        delta = endTime - startTime
        seconds = delta.days * 24 * 60 * 60 + delta.seconds
        days = seconds / 60 / 60 / 24
        speed_NewFeature = novelty / days
        speed_BugFixing = quality / days
        speed = num_outputs / days
    # Update information about outcomes
    num_updated = ReleaseCycle.objects(repository=repository, cycleNumber=cycleNumber).update(
        set__num_outputs=num_outputs, set__speed=speed, set__novelty=novelty, set__quality=quality,
        set__speed_NewFeature=speed_NewFeature, set__speed_BugFixing=speed_BugFixing,
    )
    if num_updated != 1:
        raise Exception("Debug calculate_performance_outcomes!!")

    return
