"""
Step 5d. Number of developers with a primary discursive focus (num_devWithPrimary_comment),
used for sample selection in step6.
"""

from classes.releasecycle.release_cycle import ReleaseCycle
from classes.releasecycle.release_cycle import ReleaseCycleInvolvedDeveloper


def update_numDev_with_PrimarySecondary(repository, cycleNumber):
    # This information will be used when we select samples
    involvedDevelopers = ReleaseCycleInvolvedDeveloper.objects(repository=repository, cycleNumber=cycleNumber)
    # Calculate the number of developers who have secondary foci within this release cycle
    num_devWithSecondary_comment = 0
    num_devWithPrimary_comment = 0
    for d in involvedDevelopers:
        if d['num_secondaryIssues'] is not None and d['num_secondaryIssues'] > 0:
            num_devWithSecondary_comment += 1
        if d['num_primaryIssues'] is not None and d['num_primaryIssues'] > 0:
            num_devWithPrimary_comment += 1
    num_devWithSecondary_code = 0
    num_devWithPrimary_code = 0
    for d in involvedDevelopers:
        if d['num_secondaryFiles'] is not None and d['num_secondaryFiles'] > 0:
            num_devWithSecondary_code += 1
        if d['num_primaryFiles'] is not None and d['num_primaryFiles'] > 0:
            num_devWithPrimary_code += 1

    # update the information in MongoDB
    num_updated = ReleaseCycle.objects(repository=repository, cycleNumber=cycleNumber).update(
        num_devWithSecondary_comment=num_devWithSecondary_comment, num_devWithSecondary_code=num_devWithSecondary_code,
        num_devWithPrimary_comment=num_devWithPrimary_comment, num_devWithPrimary_code=num_devWithPrimary_code
    )
    if num_updated != 1:
        raise Exception("Debug!!")

    return
