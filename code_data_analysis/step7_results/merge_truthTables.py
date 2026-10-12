"""
Step 7. Merge the truth tables that fsQCA 3.0 exports (truthTable_ca_*.csv) into the tables reported in the paper.
  paper_tables_r4(): main analysis -- all outcomes (Table A.1) and all contingency subsamples (Table A.2)
  merge_main_robustness_truthTables_r4(): main analysis next to Robustness 2-6, for each high-performance outcome,
      in the full sample and in each contingency subsample (Table B.2)
Conditions: dpi1, dsi1, tpi1, tsi1 (Robustness 3, folder level: tpi_f1, tsi_f1); outcomes: s1, n1, q1, s0, n0, q0.
"""
import pandas as pd

# Folder that holds the fsQCA outputs, organized as in data_truthTables_results/ (main/, robust2_.../, ...,
# merged_truthTables/)
results_folder = '/path/to/data_truthTables_results/'


def paper_tables_r4():
    save_folder = results_folder + 'merged_truthTables/'
    # ca --> all DVs
    source_folder = results_folder + 'main/'
    s1 = pd.read_csv(source_folder + 'truthTable_ca_s1.csv')
    n1 = pd.read_csv(source_folder + 'truthTable_ca_n1.csv')
    q1 = pd.read_csv(source_folder + 'truthTable_ca_q1.csv')
    s0 = pd.read_csv(source_folder + 'truthTable_ca_s0.csv')
    n0 = pd.read_csv(source_folder + 'truthTable_ca_n0.csv')
    q0 = pd.read_csv(source_folder + 'truthTable_ca_q0.csv')
    truthTables = s1.merge(n1, on=['dpi1', 'dsi1', 'tpi1', 'tsi1'], suffixes=('_s1', '_n1'))
    truthTables = truthTables.merge(q1, on=['dpi1', 'dsi1', 'tpi1', 'tsi1'], suffixes=('', '_q1'))
    truthTables = truthTables.merge(s0, on=['dpi1', 'dsi1', 'tpi1', 'tsi1'], suffixes=('', '_s0'))
    truthTables = truthTables.merge(n0, on=['dpi1', 'dsi1', 'tpi1', 'tsi1'], suffixes=('', '_n0'))
    truthTables = truthTables.merge(q0, on=['dpi1', 'dsi1', 'tpi1', 'tsi1'], suffixes=('', '_q0'))
    save_path = save_folder + 'ca_allDVs.xlsx'
    truthTables.to_excel(save_path)
    # UserV: ca --> all DVs
    source_folder = \
        results_folder + 'main/contingency_task_interdependence/'
    truthTables_ti = contingency_tables_r4(source_folder=source_folder, conMark='ti')
    save_path = save_folder + 'ca_allDVs_ti.xlsx'
    truthTables_ti.to_excel(save_path)
    # Org: ca --> all DVs
    source_folder = \
        results_folder + 'main/contingency_org/'
    truthTables_org = contingency_tables_r4(source_folder=source_folder, conMark='org')
    save_path = save_folder + 'ca_allDVs_org.xlsx'
    truthTables_org.to_excel(save_path)
    # Days: ca --> all DVs
    source_folder = \
        results_folder + 'main/contingency_days/'
    truthTables_days = contingency_tables_r4(source_folder=source_folder, conMark='days')
    save_path = save_folder + 'ca_allDVs_days.xlsx'
    truthTables_days.to_excel(save_path)
    # Merge all contingency tables
    truthTables_contingency = truthTables_ti.merge(
        truthTables_org, on=['dpi1', 'dsi1', 'tpi1', 'tsi1'], suffixes=('ti1', 'org1')
    )
    truthTables_contingency = truthTables_contingency.merge(
        truthTables_days, on=['dpi1', 'dsi1', 'tpi1', 'tsi1'], suffixes=('', 'days1')
    )
    save_path = save_folder + 'ca_allDVs_allContingencies.xlsx'
    truthTables_contingency.to_excel(save_path)

    return


def contingency_tables_r4(source_folder, conMark):

    if conMark == 'ti' or conMark == 'days':
        s1_con1 = pd.read_csv(source_folder + 'truthTable_ca_s1_' + conMark + '1.csv')
        n1_con1 = pd.read_csv(source_folder + 'truthTable_ca_n1_' + conMark + '1.csv')
        q1_con1 = pd.read_csv(source_folder + 'truthTable_ca_q1_' + conMark + '1.csv')
        s1_conM = pd.read_csv(source_folder + 'truthTable_ca_s1_' + conMark + 'M.csv')
        n1_conM = pd.read_csv(source_folder + 'truthTable_ca_n1_' + conMark + 'M.csv')
        q1_conM = pd.read_csv(source_folder + 'truthTable_ca_q1_' + conMark + 'M.csv')
        s1_con0 = pd.read_csv(source_folder + 'truthTable_ca_s1_' + conMark + '0.csv')
        n1_con0 = pd.read_csv(source_folder + 'truthTable_ca_n1_' + conMark + '0.csv')
        q1_con0 = pd.read_csv(source_folder + 'truthTable_ca_q1_' + conMark + '0.csv')
        truthTables = s1_con1.merge(
            n1_con1, on=['dpi1', 'dsi1', 'tpi1', 'tsi1'], suffixes=('_s1_' + conMark + '1', '_n1_' + conMark + '1'))
        truthTables = truthTables.merge(
            q1_con1, on=['dpi1', 'dsi1', 'tpi1', 'tsi1'], suffixes=('', '_q1_' + conMark + '1'))
        truthTables = truthTables.merge(
            s1_conM, on=['dpi1', 'dsi1', 'tpi1', 'tsi1'], suffixes=('', '_s1_' + conMark + 'M'))
        truthTables = truthTables.merge(
            n1_conM, on=['dpi1', 'dsi1', 'tpi1', 'tsi1'], suffixes=('', '_n1_' + conMark + 'M'))
        truthTables = truthTables.merge(
            q1_conM, on=['dpi1', 'dsi1', 'tpi1', 'tsi1'], suffixes=('', '_q1_' + conMark + 'M'))
        truthTables = truthTables.merge(
            s1_con0, on=['dpi1', 'dsi1', 'tpi1', 'tsi1'], suffixes=('', '_s1_' + conMark + '0'))
        truthTables = truthTables.merge(
            n1_con0, on=['dpi1', 'dsi1', 'tpi1', 'tsi1'], suffixes=('', '_n1_' + conMark + '0'))
        truthTables = truthTables.merge(
            q1_con0, on=['dpi1', 'dsi1', 'tpi1', 'tsi1'], suffixes=('', '_q1_' + conMark + '0'))
    elif conMark == 'org':
        s1_con1 = pd.read_csv(source_folder + 'truthTable_ca_s1_' + conMark + '1.csv')
        n1_con1 = pd.read_csv(source_folder + 'truthTable_ca_n1_' + conMark + '1.csv')
        q1_con1 = pd.read_csv(source_folder + 'truthTable_ca_q1_' + conMark + '1.csv')
        s1_con0 = pd.read_csv(source_folder + 'truthTable_ca_s1_' + conMark + '0.csv')
        n1_con0 = pd.read_csv(source_folder + 'truthTable_ca_n1_' + conMark + '0.csv')
        q1_con0 = pd.read_csv(source_folder + 'truthTable_ca_q1_' + conMark + '0.csv')
        truthTables = s1_con1.merge(
            n1_con1, on=['dpi1', 'dsi1', 'tpi1', 'tsi1'], suffixes=('_s1_' + conMark + '1', '_n1_' + conMark + '1'))
        truthTables = truthTables.merge(
            q1_con1, on=['dpi1', 'dsi1', 'tpi1', 'tsi1'], suffixes=('', '_q1_' + conMark + '1'))
        truthTables = truthTables.merge(
            s1_con0, on=['dpi1', 'dsi1', 'tpi1', 'tsi1'], suffixes=('', '_s1_' + conMark + '0'))
        truthTables = truthTables.merge(
            n1_con0, on=['dpi1', 'dsi1', 'tpi1', 'tsi1'], suffixes=('', '_n1_' + conMark + '0'))
        truthTables = truthTables.merge(
            q1_con0, on=['dpi1', 'dsi1', 'tpi1', 'tsi1'], suffixes=('', '_q1_' + conMark + '0'))
    else:
        raise Exception("{} is unrecognized contingency".format(conMark))

    return truthTables


# **********************************************************
# Merge truth tables from main analyses and robustness tests
def merge_main_robustness_truthTables_r4():
    # Folder to store the merged truthTables
    folder = results_folder + 'merged_truthTables/'

    # Full sample
    # collective attention --> high speed
    truthTables = merge_ca_truthTables_r4(tableName='truthTable_ca_s1.csv')
    save_path = folder + 'ca_s1.xlsx'
    truthTables.to_excel(save_path)

    # collective attention --> high novelty
    truthTables = merge_ca_truthTables_r4(tableName='truthTable_ca_n1.csv')
    save_path = folder + 'ca_n1.xlsx'
    truthTables.to_excel(save_path)

    # collective attention --> high quality
    truthTables = merge_ca_truthTables_r4(tableName='truthTable_ca_q1.csv')
    save_path = folder + 'ca_q1.xlsx'
    truthTables.to_excel(save_path)

    # Subsample: Task interdependence (module-centric issue connectivity)
    # # Presence of task interdependence: ti1
    # contingency_r4(folder, 'task_interdependence', 'ti', '1')
    # Moderate task interdependence: tiM
    contingency_r4(folder, 'task_interdependence', 'ti', 'M')
    # Absence of task interdependence: ti0
    contingency_r4(folder, 'task_interdependence', 'ti', '0')

    # Subsample: Organization Ownership
    # Presence of organization ownership: Org1
    contingency_r4(folder, 'org', 'org', '1')
    # # Absence of organization ownership: Org0
    # contingency_r4(folder, 'org', 'org', '0')

    # Subsample: Days (Duration of Release Cycle)
    # Long release cycle: days1
    contingency_r4(folder, 'days', 'days', '1')
    # Mid-length release cycle: daysM
    contingency_r4(folder, 'days', 'days', 'M')
    # Short release cycle: days0
    contingency_r4(folder, 'days', 'days', '0')


def merge_ca_truthTables_r4(tableName):
    global_folder = results_folder
    path_main = global_folder + 'main/' + tableName
    path_r2_90th10th = global_folder + 'robust2_calibaration_90th_10th/' + tableName
    path_r2_down25 = global_folder + 'robust2_calibaration_crossover_down25/' + tableName
    path_r2_up25 = global_folder + 'robust2_calibaration_crossover_up25/' + tableName
    path_r3 = global_folder + 'robust3_folder/' + tableName
    path_r4_2nd = global_folder + 'robust4_sample2_primary1st2ndHighest/' + tableName
    path_r4_quin = global_folder + 'robust4_sample2_primary1stQuantile/' + tableName
    path_r5 = global_folder + 'robust5_sample1_scopeDevelopers/' + tableName
    path_r6 = global_folder + 'robust6_remove_smallCollectives_noLessThan5/' + tableName

    main = pd.read_csv(path_main)
    r2_90th10th = pd.read_csv(path_r2_90th10th)
    r2_down25 = pd.read_csv(path_r2_down25)
    r2_up25 = pd.read_csv(path_r2_up25)
    r3 = pd.read_csv(path_r3)
    r4_2nd = pd.read_csv(path_r4_2nd)
    r4_quin = pd.read_csv(path_r4_quin)
    r5 = pd.read_csv(path_r5)
    r6 = pd.read_csv(path_r6)

    # merge r2: calibartion 90th, 50th, and 10th
    truthTables = main.merge(r2_90th10th, on=['dpi1', 'dsi1', 'tpi1', 'tsi1'], suffixes=('', '_r2_90th10th'))
    # merge r2: calibartion crossover_down25
    truthTables = truthTables.merge(r2_down25, on=['dpi1', 'dsi1', 'tpi1', 'tsi1'], suffixes=('', '_r2_down25'))
    # merge r2: calibartion crossover_up25
    truthTables = truthTables.merge(r2_up25, on=['dpi1', 'dsi1', 'tpi1', 'tsi1'], suffixes=('', '_r2_up25'))
    # merge r3: folder
    truthTables = truthTables.merge(r3, left_on=['dpi1', 'dsi1', 'tpi1', 'tsi1'],
                                    right_on=['dpi1', 'dsi1', 'tpi_f1', 'tsi_f1'], suffixes=('', '_r3'))
    truthTables = truthTables.drop(columns=['tpi_f1', 'tsi_f1'])
    # merge r4: redefine primary by including the second highest rank
    truthTables = truthTables.merge(r4_2nd, on=['dpi1', 'dsi1', 'tpi1', 'tsi1'], suffixes=('', '_r4_2nd'))
    # merge r4: redefine primary by use the highest quintile
    truthTables = truthTables.merge(r4_quin, on=['dpi1', 'dsi1', 'tpi1', 'tsi1'], suffixes=('', '_r4_quin'))
    # merge r5: scope developers
    truthTables = truthTables.merge(r5, on=['dpi1', 'dsi1', 'tpi1', 'tsi1'], suffixes=('', '_r5'))
    # merge r6: remove small groups
    truthTables = truthTables.merge(r6, on=['dpi1', 'dsi1', 'tpi1', 'tsi1'], suffixes=('', '_r6'))

    return truthTables


def contingency_r4(folder, folerMark, tableMark, subsampleMark):

    # collective attention --> high speed
    tableName = 'contingency_' + folerMark + '/truthTable_ca_s1_' + tableMark + subsampleMark + '.csv'
    truthTables = merge_ca_truthTables_r4(tableName=tableName)
    save_path = folder + 'ca_s1_' + tableMark + subsampleMark + '.xlsx'
    truthTables.to_excel(save_path)

    # collective attention --> high novelty
    tableName = 'contingency_' + folerMark + '/truthTable_ca_n1_' + tableMark + subsampleMark + '.csv'
    truthTables = merge_ca_truthTables_r4(tableName=tableName)
    save_path = folder + 'ca_n1_' + tableMark + subsampleMark + '.xlsx'
    truthTables.to_excel(save_path)

    # collective attention --> both high
    tableName = 'contingency_' + folerMark + '/truthTable_ca_q1_' + tableMark + subsampleMark + '.csv'
    truthTables = merge_ca_truthTables_r4(tableName=tableName)
    save_path = folder + 'ca_q1_' + tableMark + subsampleMark + '.xlsx'
    truthTables.to_excel(save_path)




