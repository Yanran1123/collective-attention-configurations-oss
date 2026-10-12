"""
Robustness 4: relax the definition of primary focus (second-highest rank, or top decile), then
re-run calculate_primaryDivision / calculate_secondaryIntegration on a copy of the collections.
"""

import numpy as np
from classes.releasecycle.release_cycle import ReleaseCycleInvolvedDeveloper


quantile = 10  # If 10, we regard items (issues/modules/files) at the highest decile as primary focus


def update_involvedDevelopers_primaryChange(repository, cycleNumber, change_primary_secondary):
    invDevs = ReleaseCycleInvolvedDeveloper.objects(repository=repository, cycleNumber=cycleNumber)
    for dev in invDevs:
        dev_id = dev['id']
        pIssues = dev['primaryIssues']
        pFiles = dev['primaryFiles']
        pModules = dev['primaryModules']
        sIssues = dev['secondaryIssues']
        sFiles = dev['secondaryFiles']
        sModules = dev['secondaryModules']
        if len(sIssues) > 0:
            new_pIssues, new_sIssues, primaryTotal = change_primary_secondary(pIssues, sIssues)
            num_primaryIssues = len(new_pIssues)
            num_secondaryIssues = len(new_sIssues)
            primaryRate_issue = primaryTotal / dev['contribution_comment']
            num_updated = ReleaseCycleInvolvedDeveloper.objects(id=dev_id).update(
                primaryIssues=new_pIssues, secondaryIssues=new_sIssues,
                num_primaryIssues=num_primaryIssues, num_secondaryIssues=num_secondaryIssues,
                primaryRate_issue=primaryRate_issue
            )
            if num_updated != 1:
                raise Exception("Debug! update_involvedDevelopers_primaryChange")
        if len(sFiles) > 0:
            new_pFiles, new_sFiles, primaryTotal = change_primary_secondary(pFiles, sFiles)
            num_primaryFiles = len(new_pFiles)
            num_secondaryFiles = len(new_sFiles)
            primaryRate_file = primaryTotal / dev['contribution_code']
            num_updated = ReleaseCycleInvolvedDeveloper.objects(id=dev_id).update(
                primaryFiles=new_pFiles, secondaryFiles=new_sFiles,
                num_primaryFiles=num_primaryFiles, num_secondaryFiles=num_secondaryFiles,
                primaryRate_file=primaryRate_file
            )
            if num_updated != 1:
                raise Exception("Debug! update_involvedDevelopers_primaryChange")
        if len(sModules) > 0:
            new_pModules, new_sModules, primaryTotal = change_primary_secondary(pModules, sModules)
            num_primaryModules = len(new_pModules)
            num_secondaryModules = len(new_sModules)
            primaryRate_module = primaryTotal / dev['contribution_code']
            num_updated = ReleaseCycleInvolvedDeveloper.objects(id=dev_id).update(
                primaryModules=new_pModules, secondaryModules=new_sModules,
                num_primaryModules=num_primaryModules, num_secondaryModules=num_secondaryModules,
                primaryRate_module=primaryRate_module
            )
            if num_updated != 1:
                raise Exception("Debug! update_involvedDevelopers_primaryChange")
    return


def change_primary_secondary_1st2ndHighest(pItems, sItems):
    new_pItems = []
    new_sItems = []

    primaryTotal = 0
    for item in pItems:
        new_pItems.append(item)
        primaryTotal = primaryTotal + item[1]

    # Calculate the maximum attention in the secondary focus
    values = []
    for item in sItems:
        values.append(item[1])
    max_lines = max(values)

    # Move items having the maximum secondary attention to the primary focus
    # remove items having the maximum secondary attention in the secondary focus
    for item in sItems:
        if item[1] == max_lines:
            new_pItems.append(item)
            primaryTotal = primaryTotal + max_lines
        else:
            new_sItems.append(item)

    return new_pItems, new_sItems, primaryTotal


def change_primary_secondary_1stQuantile(pItems, sItems):
    new_pItems = []
    new_sItems = []

    # Calculate the threshold for the highest quintile
    # 1. Get the lines of change associated with each item
    values = []
    for item in pItems:
        values.append(item[1])
    for item in sItems:
        values.append(item[1])
    # 2. Calculate the benchmark for items in the highest specified quantile
    if len(values) <= quantile:  # If less than 10 items, then keep it as the same
        benchmark = pItems[0][1]
    else:
        benchmark = np.quantile(values, 1-1/quantile)  # quantile in NumPy https://numpy.org/doc/stable/reference/generated/numpy.quantile.html

    # Update primary items, secondary items, and primary total
    # 1. Copy all primary items in the original measure, i.e., ones at the highest rank
    primaryTotal = 0
    for item in pItems:
        new_pItems.append(item)
        primaryTotal = primaryTotal + item[1]
    # 2. Add ones in the old secondary whose lines of change are no less than the highest_quantile
    for item in sItems:
        if item[1] >= benchmark:
            new_pItems.append(item)
            primaryTotal = primaryTotal + item[1]
        else:
            new_sItems.append(item)

    return new_pItems, new_sItems, primaryTotal
