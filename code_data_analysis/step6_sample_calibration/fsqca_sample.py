"""
Step 6. Select the final sample of release cycles, build the final variables, calibrate them,
and write the CSV files analyzed in fsQCA 3.0.
"""

import pandas as pd
from pprint import pprint
from pymongo import MongoClient
from step6_sample_calibration.calibration import calibrate


# Output folder; it must contain the subfolders contingency_org/, contingency_days/, and
# contingency_task_interdependence/ for the contingency subsamples
folder = '/path/to/project/output/main/'


def construct_sample_r4():
    # Import data from MongoDB to pandas dataframe
    conn_str = 'mongodb://localhost:27017'
    client = MongoClient(conn_str)
    db = client['db2_paper_r4']  # Specify name of the database

    coll = db.sample0  # Specify the collection

    df = pd.DataFrame(list(coll.find({})))  # Within find, we can add conditions by 'FieldName': value

    # Select sample and get descriptive statistics
    # Save the raw sample and origital descriptive statistics as csv files
    df, descriptive = sample_selection_r4(df=df)
    path = folder + 'sample0.csv'
    df.to_csv(path)
    path = folder + 'sample0_descriptive.csv'
    descriptive.to_csv(path)

    # Calculate and save correlation matrix
    get_correlation_matrix_r4(df=df)

    # Calibrate Variables:
    # 1) based on 75, 50, 25 percentiles in the main analyses
    # 2) vary crossover point +/-25 percent for CA variables
    # 3) set full membership and full non-membership as 90th and 10th percentiles
    # 4) change the crossover of secondary integration by issues, whose 50th percentile is noticeably biased
    # toward its 25th percentile (or full nonmembership anchor), as the average of 75th and 25th percentiles
    # (or full membership and full nonmembership anchors).
    df = calibration_r4(df=df, descriptive=descriptive)

    # Select variables for main effect analysis
    save_variables_for_fsQCA_main_r4(df)

    # Select variables for subsample analyses
    subsample_analyses_r4(df=df, descriptive=descriptive)

    return


def sample_selection_r4(df):
    # 18630 release cycles, selected by 1. having a release; 2. having a codebase

    # Impose selection conditions at the release-cycle level

    # 1. Scope to 14 <= days
    df = df.loc[df['days'] >= 14]  # 9191 cases left, 9439 release cycles are deleted

    # 2. Scope to cases that have more than 1 involved developers
    df = df.loc[df['num_developers'] > 1]  # 4699 cases left
    # ***********************
    # 4th round revision
    # 5. Remove release cycles that the number of developers who comment (or do epistemic work) is less than 2
    df = df.loc[df['num_devWithPrimary_comment'] >= 2]  # 4594 cases left
    # ***********************
    # 4699 cases left; 4492 release cycles are deleted,
    # in which 2645 cases have no developers and 1847 cases have 1 involved developer

    # 3. Scope to cases that do not have outputs whose information cannot be fetched due to GitHub limitations
    if 'hasNoChangeInfo' in df.columns:
        df = df.loc[df['hasNoChangeInfo'] != True]  # 4459 cases left, 240 release cycles are deleted
    # 1042 repositories are left

    # 4. Remove release cycles whose speed is 0 (the relation between release and community-based development is low)
    df = df.loc[df['speed'] > 0]  # 4291 cases left, 70 release cycles are deleted
    # 1024 repositories are left

    # ***********************
    # 4th round revision
    # Change pdi as 0 if pdi is None -- !!!This is inappropriate!!！
    # Blau's index for epistemic work is MEANINGLESS if the number of developers is less than 2
    # df.loc[df['total_comments_dev'] == 0, 'pdi'] = 0

    grouped = df.groupby('repository')  # 1004 repositories
    # 1004 repositories are left

    # # Robustness 6: Remove small groups where there are less than 5 developers
    # df = df.loc[df['num_developers'] >= 5]

    # Build the collective-attention variables used in the paper
    df['dpi'] = 1 - df['pdi']  # discursive primary integration
    df['dsi'] = df['sii']  # discursive secondary integration
    df['tpi'] = 1 - df['pdf']  # technical primary integration (file level, main analysis)
    df['tsi'] = df['sif']  # technical secondary integration (file level, main analysis)
    # Robustness 3: folder-level technical primary and secondary integration
    df['tpi_f'] = 1 - df['pdm']
    df['tsi_f'] = df['sim']
    # Task interdependence (stored in MongoDB as task_interdependence_r4, issue_interdependence_r4,
    # and file_interdependence_r4)
    df['task_interdependence'] = df['task_interdependence_r4']  # overall task interdependence (OTI)
    df['discursive_task_interdependence'] = df['issue_interdependence_r4']  # DTI
    df['technical_task_interdependence'] = df['file_interdependence_r4']  # TTI

    df = df[[
        # release identifier
        'repository', 'cycleNumber',

        # collective attention
        'dpi', 'dsi',  # discursive primary integration, discursive secondary integration
        'tpi', 'tsi',  # technical primary integration, technical secondary integration
        # 'tpi_f', 'tsi_f',  # folder-level technical primary and secondary integration (robustness)

        # primary overlap using average proportion of attention overlap;
        # secondary separation using Blau's index
        # 'poi', 'ssi',
        # 'pof', 'ssf',
        # 'pom', 'ssm',

        # DVs
        'speed', 'novelty', 'quality',
        # 'speed_NewFeature', 'speed_BugFixing',

        # Contingencies,
        'task_interdependence',
        'org', 'days',
        # 'discursive_task_interdependence',
        # 'technical_task_interdependence',

        # 'num_developers',
        # 'num_devWithPrimary_comment',
        # 'num_epistemicTasks',
        # 'num_issues',
        # 'num_prs',
        # 'num_files',
    ]]

    # 6. Get descriptive statistics of relevant variables
    descriptive = df[[
        # collective attention
        'dpi', 'dsi',  # discursive primary integration, discursive secondary integration
        'tpi', 'tsi',  # technical primary integration, technical secondary integration
        # 'tpi_f', 'tsi_f',  # folder-level technical primary and secondary integration (robustness)

        # primary overlap using average proportion of attention overlap;
        # secondary separation using Blau's index
        # 'poi', 'ssi',
        # 'pof', 'ssf',
        # 'pom', 'ssm',

        # DVs
        'speed', 'novelty', 'quality',
        # 'speed_NewFeature', 'speed_BugFixing',

        # Contingencies,
        'task_interdependence',
        'org', 'days',
        # 'discursive_task_interdependence',
        # 'technical_task_interdependence',

        # 'num_developers',
        # 'num_devWithPrimary_comment',
        # 'num_issues',
        # 'num_prs',
        # 'num_files',
    ]].describe([.1, .25, .5, .75, .9])

    return df, descriptive


def get_correlation_matrix_r4(df):
    df1 = df[[
        # collective attention
        'dpi', 'dsi',  # discursive primary integration, discursive secondary integration
        'tpi', 'tsi',  # technical primary integration, technical secondary integration
        # 'tpi_f', 'tsi_f',  # folder-level technical primary and secondary integration (robustness)

        # primary overlap using average proportion of attention overlap;
        # secondary separation using Blau's index
        # 'poi', 'ssi',
        # 'pof', 'ssf',
        # 'pom', 'ssm',

        # DVs
        'speed', 'novelty', 'quality',
        # 'speed_NewFeature', 'speed_BugFixing',

        # Contingencies,
        'task_interdependence',
        'org', 'days',
        # 'discursive_task_interdependence',
        # 'technical_task_interdependence',

        # 'num_developers',
        # 'num_devWithPrimary_comment',
        # 'num_issues',
        # 'num_prs',
        # 'num_files',
    ]]
    correlation = df1.corr(method='pearson')
    path = folder + 'correlationPearson_sample0.csv'
    correlation.to_csv(path)
    correlation = df1.corr(method='spearman')
    path = folder + 'correlationSpearman_sample0.csv'
    correlation.to_csv(path)
    return


def calibration_r4(df, descriptive):
    full = '75%'
    cross = '50%'
    non = '25%'

    for var in descriptive.columns:
        # # ********************************
        # # Robustness Test:tuning full- and non-membership of causal conditions
        # # 1. change the value of full as '90%' and non as '10%'
        # # 2. Skip tuning the DVs
        # if var == 'speed' or var == 'speed_NewFeature' or var == 'speed_BugFixing' \
        #         or var == 'novelty' or var == 'quality':
        #     full = '75%'
        #     non = '25%'
        # ********************************

        # Skip the org variable, which is 0 or 1
        if var == 'org':
            continue

        # Name calibrated variable as varName plus 1
        var_calibrated = var + '1'

        # Set the value of anchors
        anchor_full = descriptive.loc[full, var]
        anchor_non = descriptive.loc[non, var]
        anchor_cross = descriptive.loc[cross, var]

        # tune the anchors a bit just in case that the cross percentile is equal to percentiles for full or non
        if anchor_cross != anchor_non:
            anchor_cross = anchor_cross - 0.000001
        elif anchor_cross == anchor_non and anchor_cross != anchor_full:
            anchor_cross = anchor_cross + 0.000001
        elif anchor_cross == anchor_full and anchor_cross == anchor_non:
            anchor_cross = anchor_cross + 0.000001
            anchor_full = anchor_full + 0.000002

        # # ********************************
        # # Robustness test: tuning crossover of causal conditions
        # # 1. make sure that the value of full is 75% and the value of non is 25%
        # # 2. change the parameter in tuning function: 1. percent=-25; 2. percent=25
        # if var != 'speed' and var != 'speed_NewFeature' and var != 'speed_BugFixing' \
        #         and var != 'novelty' and var != 'quality':
        #     anchor_cross = crossover_tuning_r3(
        #         full=anchor_full, cross=anchor_cross, non=anchor_non, percent=25)
        # # ********************************

        # Calibration
        # Set a more sense-making cross over so that we do not have too many solution configurations
        if var == 'novelty' or var == 'quality':
            anchor_cross = (anchor_full + anchor_non) / 2

        # calibrate by using conventional approach
        df[var_calibrated] = calibrate(
            variable=df[[var]],
            full=anchor_full, cross=anchor_cross, non=anchor_non
        )

    pprint(df.columns)

    df.rename(columns={
        'speed1': 's1',
        # 'speed_NewFeature1': 's_f1',
        # 'speed_BugFixing1': 's_b1',

        'novelty1': 'n1',  # Novelty
        'quality1': 'q1',  # Quality

        'task_interdependence1': 'ti1',
        # 'discursive_task_interdependence1': 'dti1',
        # 'technical_task_interdependence1': 'tti1',
        # 'num_developers1': 'numD1',
        # 'num_devWithPrimary_comment1': 'numD_comment1',
    }, inplace=True)

    df['s0'] = 1 - df['s1']
    # df['s_f0'] = 1 - df['s_f1']
    # df['s_b0'] = 1 - df['s_b1']

    df['n0'] = 1 - df['n1']
    df['q0'] = 1 - df['q1']

    return df


def save_variables_for_fsQCA_main_r4(df):
    df = df[[
        'repository', 'cycleNumber',

        # collective attention
        'dpi1', 'dsi1',  # calibrated discursive primary integration, discursive secondary integration
        'tpi1', 'tsi1',  # calibrated technical primary integration, technical secondary integration
        # 'tpi_f1', 'tsi_f1',  # calibrated folder-level technical primary and secondary integration (robustness)

        # primary overlap using average proportion of attention overlap;
        # secondary separation using Blau's index
        # 'poi1', 'ssi1',
        # 'pof1', 'ssf1',
        # 'pom1', 'ssm1',

        # DVs
        's1', 'n1', 'q1',
        's0', 'n0', 'q0',

        # Contingencies
        'ti1', 'org', 'days1',
        # 'dti1', 'tti1',
        # 'numD1',

        # 'num_developers',
        # 'num_devWithPrimary_comment',
        # 'num_epistemicTasks',
        # 'num_issues',
        # 'num_prs',
        # 'num_files',

    ]]

    path = folder + 'sample0_fsQCA.csv'
    df.to_csv(path)

    return


def subsample_analyses_r4(df, descriptive):
    # *******************************
    # Save three sub-samples based on an uncalibrated contingency's 75th and 25th percentiles
    # Star contributors, organization ownership, duration of release cycle, average tenure
    contingencies_raw = [
        'org', 'days',
        'task_interdependence',
        # 'discursive_task_interdependence', 'technical_task_interdependence',
        # 'num_developers',
    ]
    contingencies_calibrated = [
        'org', 'days1',
        'ti1',
        # 'dti1', 'tti1'
        # 'numD1',
    ]
    len_contingencies = len(contingencies_raw)
    for i in range(0, len_contingencies):
        var_raw = contingencies_raw[i]
        var_calibrated = contingencies_calibrated[i]
        if var_raw == 'org':
            # Subsample of OSS projects owned by organizations
            df1 = df.loc[df[var_raw] == 1]
            df1 = df1[[
                'repository', 'cycleNumber',

                # collective attention
                'dpi1', 'dsi1',  # calibrated discursive primary integration, discursive secondary integration
                'tpi1', 'tsi1',  # calibrated technical primary integration, technical secondary integration
                # 'tpi_f1', 'tsi_f1',  # calibrated folder-level technical primary and secondary integration (robustness)

                # primary overlap using average proportion of attention overlap;
                # secondary separation using Blau's index
                # 'poi1', 'ssi1',
                # 'pof1', 'ssf1',
                # 'pom1', 'ssm1',

                # DVs
                's1', 'n1', 'q1',
                's0', 'n0', 'q0',

                # focal contingency
                var_raw, var_calibrated
            ]]
            path = folder + 'contingency_' + var_raw + '/sample0_fsQCA_' + var_raw + '1.csv'
            df1.to_csv(path)
            # Subsample of OSS projects owned by individuals
            df1 = df.loc[df[var_raw] == 0]
            df1 = df1[[
                'repository', 'cycleNumber',
                # collective attention
                'dpi1', 'dsi1',  # calibrated discursive primary integration, discursive secondary integration
                'tpi1', 'tsi1',  # calibrated technical primary integration, technical secondary integration
                # 'tpi_f1', 'tsi_f1',  # calibrated folder-level technical primary and secondary integration (robustness)

                # primary overlap using average proportion of attention overlap;
                # secondary separation using Blau's index
                # 'poi1', 'ssi1',
                # 'pof1', 'ssf1',
                # 'pom1', 'ssm1',

                # DVs
                's1', 'n1', 'q1',
                's0', 'n0', 'q0',
                var_raw, var_calibrated
            ]]
            path = folder + 'contingency_' + var_raw + '/sample0_fsQCA_' + var_raw + '0.csv'
            df1.to_csv(path)
        else:
            up = descriptive.loc['75%', var_raw]
            down = descriptive.loc['25%', var_raw]
            # Subsample for the presence of a contingency, >= 75%
            df1 = df.loc[df[var_raw] >= up]
            df1 = df1[[
                'repository', 'cycleNumber',
                # collective attention
                'dpi1', 'dsi1',  # calibrated discursive primary integration, discursive secondary integration
                'tpi1', 'tsi1',  # calibrated technical primary integration, technical secondary integration
                # 'tpi_f1', 'tsi_f1',  # calibrated folder-level technical primary and secondary integration (robustness)

                # primary overlap using average proportion of attention overlap;
                # secondary separation using Blau's index
                # 'poi1', 'ssi1',
                # 'pof1', 'ssf1',
                # 'pom1', 'ssm1',

                # DVs
                's1', 'n1', 'q1',
                's0', 'n0', 'q0',
                var_raw, var_calibrated
            ]]
            path = folder + 'contingency_' + var_raw + '/sample0_fsQCA_' + var_raw + '1.csv'
            # Subsample for the absence of a contingency, <= 25%
            df1.to_csv(path)
            df1 = df.loc[df[var_raw] <= down]
            df1 = df1[[
                'repository', 'cycleNumber',
                # collective attention
                'dpi1', 'dsi1',  # calibrated discursive primary integration, discursive secondary integration
                'tpi1', 'tsi1',  # calibrated technical primary integration, technical secondary integration
                # 'tpi_f1', 'tsi_f1',  # calibrated folder-level technical primary and secondary integration (robustness)

                # primary overlap using average proportion of attention overlap;
                # secondary separation using Blau's index
                # 'poi1', 'ssi1',
                # 'pof1', 'ssf1',
                # 'pom', 'ssm',

                # DVs
                's1', 'n1', 'q1',
                's0', 'n0', 'q0',
                var_raw, var_calibrated
            ]]
            path = folder + 'contingency_' + var_raw + '/sample0_fsQCA_' + var_raw + '0.csv'
            df1.to_csv(path)
            # Subsample for the middle part, >=25% and <=75%
            df1.to_csv(path)
            df1 = df.loc[(df[var_raw] > down) & (df[var_raw] < up)]
            df1 = df1[[
                'repository', 'cycleNumber',
                # collective attention
                'dpi1', 'dsi1',  # calibrated discursive primary integration, discursive secondary integration
                'tpi1', 'tsi1',  # calibrated technical primary integration, technical secondary integration
                # 'tpi_f1', 'tsi_f1',  # calibrated folder-level technical primary and secondary integration (robustness)

                # primary overlap using average proportion of attention overlap;
                # secondary separation using Blau's index
                # 'poi1', 'ssi1',
                # 'pof1', 'ssf1',
                # 'pom1', 'ssm1',

                # DVs
                's1', 'n1', 'q1',
                's0', 'n0', 'q0',
                var_raw, var_calibrated
            ]]
            path = folder + 'contingency_' + var_raw + '/sample0_fsQCA_' + var_raw + 'M.csv'
            df1.to_csv(path)
    return


def crossover_tuning_r3(full, cross, non, percent):
    if percent > 0:
        new_cross = cross + (full - cross) * percent / 100
    elif percent < 0:
        new_cross = cross + (cross - non) * percent / 100
    else:
        new_cross = cross
    return new_cross
