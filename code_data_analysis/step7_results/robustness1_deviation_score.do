// Robustness 1: deviation score analyses (Table B1).
// For each solution configuration, the distance of each case from the configuration's ideal type
// (Euclidean distance over the conditions in the solution) predicts membership in the outcome
// (two-limit Tobit, standard errors clustered by repository). Run in Stata 14 with outreg2 installed.
// Input: the fsQCA files written by step 6 (sample0_fsQCA*.csv), copied into the folder below.

cd "/path/to/data_truthTables_results/robust1_deviationScore"

log using regression

cls


//  Results used for ca --> DVs
drop _all
import delimited "/path/to/data_truthTables_results/robust1_deviationScore/sample0_fsQCA.csv"

gen HS1 = sqrt((dpi1)^2 + (1-dsi1)^2 + (tpi1)^2 + (1-tsi1)^2)

gen HN1 = sqrt((dpi1)^2 + (1-dsi1)^2 + (tpi1)^2 + (1-tsi1)^2)

gen HQ1 = sqrt((dpi1)^2 + (1-dsi1)^2 + (tpi1)^2 + (1-tsi1)^2)

tobit s1 HS1, ll ul vce(cluster repository)
	outreg2 using table1_ca_allDVs, ctitle(Membership to high speed) bdec(2) word replace
tobit n1 HN1, ll ul vce(cluster repository)
	outreg2 using table1_ca_allDVs, ctitle(Membership to high novelty) bdec(2) word append
tobit q1 HQ1, ll ul vce(cluster repository)
	outreg2 using table1_ca_allDVs, ctitle(Membership to high quality) bdec(2) word append


// ti0: Results for low task interdependence
drop _all
import delimited "/path/to/data_truthTables_results/robust1_deviationScore/sample0_fsQCA_task_interdependence0.csv"

gen HS1_ti0 = sqrt((tpi1)^2 + (1-tsi1)^2)
gen HS2_ti0 = sqrt((dpi1)^2 + (1-tsi1)^2)
gen HS3_ti0 = sqrt((1-dsi1)^2 + (1-tsi1)^2)
gen HS4_ti0 = sqrt((dpi1)^2 + (1-dsi1)^2 + (tpi1)^2)
gen HS_ti0_ideal = - min(HS1_ti0, HS2_ti0, HS3_ti0, HS4_ti0)

gen HN1_ti0 = sqrt((tpi1)^2 + (1-tsi1)^2)
gen HN2_ti0 = sqrt((dpi1)^2 + (1-tsi1)^2)
gen HN3_ti0 = sqrt((1-dsi1)^2 + (1-tsi1)^2)
gen HN4_ti0 = sqrt((dpi1)^2 + (1-dsi1)^2 + (tpi1)^2)
gen HN_ti0_ideal = - min(HN1_ti0, HN2_ti0, HN3_ti0, HN4_ti0)

gen HQ1_ti0 = sqrt((tpi1)^2 + (1-tsi1)^2)
gen HQ2_ti0 = sqrt((dpi1)^2 + (1-tsi1)^2)
gen HQ3_ti0 = sqrt((1-dsi1)^2 + (1-tsi1)^2)
gen HQ4_ti0 = sqrt((dpi1)^2 + (1-dsi1)^2 + (tpi1)^2)
gen HQ_ti0_ideal = - min(HQ1_ti0, HQ2_ti0, HQ3_ti0, HQ4_ti0)

tobit s1 HS_ti0_ideal, ll ul vce(cluster repository)
	outreg2 using table1_ca_s1_ti0, ctitle(Membership to high speed) bdec(2) word replace
tobit s1 HS1_ti0, ll ul vce(cluster repository)
	outreg2 using table1_ca_s1_ti0, ctitle(Membership to high speed) bdec(2) word append
tobit s1 HS2_ti0, ll ul vce(cluster repository)
	outreg2 using table1_ca_s1_ti0, ctitle(Membership to high speed) bdec(2) word append
tobit s1 HS3_ti0, ll ul vce(cluster repository)
	outreg2 using table1_ca_s1_ti0, ctitle(Membership to high speed) bdec(2) word append
tobit s1 HS4_ti0, ll ul vce(cluster repository)
	outreg2 using table1_ca_s1_ti0, ctitle(Membership to high speed) bdec(2) word append


tobit n1 HN_ti0_ideal, ll ul vce(cluster repository)
	outreg2 using table1_ca_n1_ti0, ctitle(Membership to high novelty) bdec(2) word replace
tobit n1 HN1_ti0, ll ul vce(cluster repository)
	outreg2 using table1_ca_n1_ti0, ctitle(Membership to high novelty) bdec(2) word append
tobit n1 HN2_ti0, ll ul vce(cluster repository)
	outreg2 using table1_ca_n1_ti0, ctitle(Membership to high novelty) bdec(2) word append
tobit n1 HN3_ti0, ll ul vce(cluster repository)
	outreg2 using table1_ca_n1_ti0, ctitle(Membership to high novelty) bdec(2) word append
tobit n1 HN4_ti0, ll ul vce(cluster repository)
	outreg2 using table1_ca_n1_ti0, ctitle(Membership to high novelty) bdec(2) word append
	

tobit q1 HQ_ti0_ideal, ll ul vce(cluster repository)
	outreg2 using table1_ca_q1_ti0, ctitle(Membership to high quality) bdec(2) word replace
tobit q1 HQ1_ti0, ll ul vce(cluster repository)
	outreg2 using table1_ca_q1_ti0, ctitle(Membership to high quality) bdec(2) word append
tobit q1 HQ2_ti0, ll ul vce(cluster repository)
	outreg2 using table1_ca_q1_ti0, ctitle(Membership to high quality) bdec(2) word append
tobit q1 HQ3_ti0, ll ul vce(cluster repository)
	outreg2 using table1_ca_q1_ti0, ctitle(Membership to high quality) bdec(2) word append
tobit q1 HQ4_ti0, ll ul vce(cluster repository)
	outreg2 using table1_ca_q1_ti0, ctitle(Membership to high quality) bdec(2) word append


// tiM: Results for low task interdependence
drop _all
import delimited "/path/to/data_truthTables_results/robust1_deviationScore/sample0_fsQCA_task_interdependenceM.csv"

gen HS1_tiM = sqrt((dpi1)^2 + (1-dsi1)^2 + (tpi1)^2 + (1-tsi1)^2)

gen HN1_tiM = sqrt((dpi1)^2 + (1-dsi1)^2 + (tpi1)^2 + (1-tsi1)^2)

gen HQ1_tiM = sqrt((dpi1)^2 + (1-dsi1)^2 + (tpi1)^2 + (1-tsi1)^2)

tobit s1 HS1_tiM, ll ul vce(cluster repository)
	outreg2 using table1_ca_allDVs_tiM, ctitle(Membership to high speed) bdec(2) word replace
tobit n1 HN1_tiM, ll ul vce(cluster repository)
	outreg2 using table1_ca_allDVs_tiM, ctitle(Membership to high novelty) bdec(2) word append
tobit q1 HQ1_tiM, ll ul vce(cluster repository)
	outreg2 using table1_ca_allDVs_tiM, ctitle(Membership to high quality) bdec(2) word append
	
	
// Org1

drop _all
import delimited "/path/to/data_truthTables_results/robust1_deviationScore/sample0_fsQCA_org1.csv"

gen HS1_Org1 = sqrt((1-(1-dpi1))^2 + (1-dsi1)^2 + (1-(1-tpi1))^2)
gen HS2_Org1 = sqrt((1-(1-dpi1))^2 + (1-(1-tpi1))^2 + (1-tsi1)^2)
gen HS_Org1_ideal = - min(HS1_Org1, HS2_Org1)

gen HN1_Org1 = sqrt((1-(1-dpi1))^2 + (1-dsi1)^2 + (1-(1-tpi1))^2 + (1-tsi1)^2)

gen HQ1_Org1 = sqrt((1-(1-dpi1))^2 + (1-dsi1)^2 + (1-(1-tpi1))^2 + (1-tsi1)^2)


tobit s1 HS_Org1_ideal, ll ul vce(cluster repository)
	outreg2 using table1_ca_allDVs_org1, ctitle(Membership to high speed) bdec(2) word replace
tobit s1 HS1_Org1, ll ul vce(cluster repository)
	outreg2 using table1_ca_allDVs_org1, ctitle(Membership to high speed) bdec(2) word append
tobit s1 HS2_Org1, ll ul vce(cluster repository)
	outreg2 using table1_ca_allDVs_org1, ctitle(Membership to high speed) bdec(2) word append

tobit n1 HN1_Org1, ll ul vce(cluster repository)
	outreg2 using table1_ca_allDVs_org1, ctitle(Membership to high novelty) bdec(2) word append
	
tobit q1 HQ1_Org1, ll ul vce(cluster repository)
	outreg2 using table1_ca_allDVs_org1, ctitle(Membership to high quality) bdec(2) word append



// Days1
drop _all
import delimited "/path/to/data_truthTables_results/robust1_deviationScore/sample0_fsQCA_days1.csv"

gen HN1_Days1 = sqrt((1-(1-dpi1))^2 + (1-dsi1)^2 + (1-(1-tpi1))^2)
gen HN2_Days1 = sqrt((1-(1-dpi1))^2 + (1-dsi1)^2 + (1-tsi1)^2)
gen HN3_Days1 = sqrt((1-(1-dpi1))^2 + (1-(1-tpi1))^2 + (1-tsi1)^2)
gen HN4_Days1 = sqrt((1-dsi1)^2 + (1-(1-tpi1))^2 + (1-tsi1)^2)
gen HN_Days1_ideal = - min(HN1_Days1, HN2_Days1, HN3_Days1, HN4_Days1)

gen HQ1_Days1 = sqrt((1-(1-dpi1))^2 + (1-dsi1)^2 + (1-(1-tpi1))^2 + (1-tsi1)^2)

tobit n1 HN_Days1_ideal, ll ul vce(cluster repository)
	outreg2 using table1_ca_allDVs_days1, ctitle(Membership to high novelty) bdec(2) word replace
tobit n1 HN1_Days1, ll ul vce(cluster repository)
	outreg2 using table1_ca_allDVs_days1, ctitle(Membership to high novelty) bdec(2) word append
tobit n1 HN2_Days1, ll ul vce(cluster repository)
	outreg2 using table1_ca_allDVs_days1, ctitle(Membership to high novelty) bdec(2) word append
tobit n1 HN3_Days1, ll ul vce(cluster repository)
	outreg2 using table1_ca_allDVs_days1, ctitle(Membership to high novelty) bdec(2) word append
tobit n1 HN4_Days1, ll ul vce(cluster repository)
	outreg2 using table1_ca_allDVs_days1, ctitle(Membership to high novelty) bdec(2) word append

tobit q1 HQ1_Days1, ll ul vce(cluster repository)
	outreg2 using table1_ca_allDVs_days1, ctitle(Membership to high quality) bdec(2) word append


// DaysM
drop _all
import delimited "/path/to/data_truthTables_results/robust1_deviationScore/sample0_fsQCA_daysM.csv"

gen HS1_DaysM = sqrt((dpi1)^2 + (1-dsi1)^2 + (tpi1)^2)
gen HS2_DaysM = sqrt((dpi1)^2 + (tpi1)^2 + (1-tsi1)^2)
gen HS3_DaysM = sqrt((dpi1)^2 + (1-dsi1)^2 + (1-tsi1)^2)
gen HS_DaysM_ideal = - min(HS1_DaysM, HS2_DaysM, HS3_DaysM)

gen HN1_DaysM = sqrt((dpi1)^2 + (1-dsi1)^2 + (tpi1)^2 + (1-tsi1)^2)

gen HQ1_DaysM = sqrt((dpi1)^2 + (1-dsi1)^2 + (tpi1)^2 + (1-tsi1)^2)

tobit s1 HS_DaysM_ideal, ll ul vce(cluster repository)
	outreg2 using table1_ca_allDVs_daysM, ctitle(Membership to high speed) bdec(2) word replace
tobit s1 HS1_DaysM, ll ul vce(cluster repository)
	outreg2 using table1_ca_allDVs_daysM, ctitle(Membership to high speed) bdec(2) word append
tobit s1 HS2_DaysM, ll ul vce(cluster repository)
	outreg2 using table1_ca_allDVs_daysM, ctitle(Membership to high speed) bdec(2) word append
tobit s1 HS3_DaysM, ll ul vce(cluster repository)
	outreg2 using table1_ca_allDVs_daysM, ctitle(Membership to high speed) bdec(2) word append

tobit n1 HN1_DaysM, ll ul vce(cluster repository)
	outreg2 using table1_ca_allDVs_daysM, ctitle(Membership to high novelty) bdec(2) word append
	
tobit q1 HQ1_DaysM, ll ul vce(cluster repository)
	outreg2 using table1_ca_allDVs_daysM, ctitle(Membership to high quality) bdec(2) word append

	
// Days0
drop _all
import delimited "/path/to/data_truthTables_results/robust1_deviationScore/sample0_fsQCA_days0.csv"

gen HS1_Days0 = sqrt((1-(1-dpi1))^2)
gen HS2_Days0 = sqrt((1-dsi1)^2 + (1-(1-tpi1))^2)
gen HS3_Days0 = sqrt((1-dsi1)^2 + (1-tsi1)^2)
gen HS4_Days0 = sqrt((1-(1-tpi1))^2 + (1-tsi1)^2)
gen HS_Days0_ideal = - min(HS1_Days0, HS2_Days0, HS3_Days0, HS4_Days0)

gen HQ1_Days0 = sqrt((1-(1-dpi1))^2 + (1-dsi1)^2 + (1-(1-tpi1))^2 + (1-tsi1)^2)

tobit s1 HS_Days0_ideal, ll ul vce(cluster repository)
	outreg2 using table1_ca_allDVs_days0, ctitle(Membership to high speed) bdec(2) word replace
tobit s1 HS1_Days0, ll ul vce(cluster repository)
	outreg2 using table1_ca_allDVs_days0, ctitle(Membership to high speed) bdec(2) word append
tobit s1 HS2_Days0, ll ul vce(cluster repository)
	outreg2 using table1_ca_allDVs_days0, ctitle(Membership to high speed) bdec(2) word append
tobit s1 HS3_Days0, ll ul vce(cluster repository)
	outreg2 using table1_ca_allDVs_days0, ctitle(Membership to high speed) bdec(2) word append
tobit s1 HS4_Days0, ll ul vce(cluster repository)
	outreg2 using table1_ca_allDVs_days0, ctitle(Membership to high speed) bdec(2) word append
	
tobit q1 HQ1_Days0, ll ul vce(cluster repository)
	outreg2 using table1_ca_allDVs_days0, ctitle(Membership to high quality) bdec(2) word append

log close
