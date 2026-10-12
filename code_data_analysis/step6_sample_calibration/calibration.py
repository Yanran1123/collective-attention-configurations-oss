"""
Ragin's direct method of calibration (fuzzy-set membership scores).
"""

import math


def calibrate(variable, full, cross, non):
    # Get deviations from the crossover   
    v1 = variable - cross

    # Calculate scalars of the positive and negative deviations
    scalar_positive = 3.0 / (full - cross)
    scalar_negative = -3.0 / (non - cross)

    begin = 0
    end = variable.shape[0]  # The number of rows

    for i in range(begin, end):
        dev = v1.iloc[i, 0]
        # Calculate log_odds of each value
        if dev > 0:
            log_odds = dev * scalar_positive
        elif dev < 0:
            log_odds = dev * scalar_negative
        else:
            log_odds = 0

        # Calculate the membership
        if log_odds > 100:
            membership = 1
        else:
            membership = math.exp(log_odds) / (1 + math.exp(log_odds))

        v1.iloc[i, 0] = membership

    return v1
