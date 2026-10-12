"""
Step 5e (part 1). Flag the release cycles in the final sample (inSample = 1), using the same criteria as
sample_selection_r4() in step 6.
"""

from classes.releasecycle.release_cycle import ReleaseCycle
from classes.releasecycle.release_cycle import ReleaseCycleInvolvedDeveloper
from classes.releasecycle.release_cycle import ReleaseCycleInvolvedFile
from classes.releasecycle.release_cycle import ReleaseCycleInvolvedIssue
from classes.releasecycle.release_cycle import ReleaseCycleInvolvedModule
from classes.releasecycle.release_cycle import ReleaseCycleInvolvedPullRequest


def update_inSample_r4():
    # Sample selection criterias:
    # 1. Scope to 14 <= days
    # 2. Scope to cases that have more than 1 involved developers
    # 3. Scope to cases that do not have outputs whose information cannot be fetched due to GitHub limitations
    # 4. Remove release cycles whose speed is 0 (the relation between release and community-based development is low)
    # 5. Remove release cycles that the number of developers who comment (or do epistemic work) is less than 2
    releases = ReleaseCycle.objects().only(
        'repository', 'cycleNumber',
        'days', 'num_developers', 'hasNoChangeInfo', 'speed', 'num_devWithPrimary_comment'
    )
    for release in releases:
        repository = release['repository']
        cycleNumber = release['cycleNumber']
        days = release['days']
        num_developers = release['num_developers']
        hasNoChangeInfo = release['hasNoChangeInfo']
        speed = release['speed']
        num_devWithPrimary_comment = release['num_devWithPrimary_comment']
        if days >= 14 \
                and num_developers is not None and num_developers > 1 \
                and num_devWithPrimary_comment is not None and num_devWithPrimary_comment > 1 \
                and hasNoChangeInfo is not True \
                and speed is not None and speed > 0:
            inSample = 1
        else:
            inSample = 0
        # Update values in sample0 and the related involved developers, issues, prs, files, and modules
        num_updated = ReleaseCycle.objects(repository=repository, cycleNumber=cycleNumber).update(
            inSample=inSample
        )
        num_updated = ReleaseCycleInvolvedDeveloper.objects(repository=repository, cycleNumber=cycleNumber).update(
            inSample=inSample
        )
        num_updated = ReleaseCycleInvolvedIssue.objects(repository=repository, cycleNumber=cycleNumber).update(
            inSample=inSample
        )
        num_updated = ReleaseCycleInvolvedPullRequest.objects(repository=repository, cycleNumber=cycleNumber).update(
            inSample=inSample
        )
        num_updated = ReleaseCycleInvolvedFile.objects(repository=repository, cycleNumber=cycleNumber).update(
            inSample=inSample
        )
        num_updated = ReleaseCycleInvolvedModule.objects(repository=repository, cycleNumber=cycleNumber).update(
            inSample=inSample
        )

    return
