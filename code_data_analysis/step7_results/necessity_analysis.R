# Necessity analyses (Section 6.1): consistency (inclN), relevance of necessity (RoN), and coverage (covN)
# of each collective attention condition for high speed (s1), novelty (n1), and quality (q1).
#
# The original analyses were run in the R console with the QCA package (see the logs in
# data_truthTables_results/main/necessity_analysis/). They ran the same 12 tests on each sample below; this script
# repeats those tests in a loop. The original runs read copies of the step-6 files (sample0_fsQCA_*_necessity.csv);
# this script reads the step-6 files directly. In the QCA package, "~x" denotes the negation of x (1 - x).

library(QCA)

# Folder with the files written by step 6 (step6_sample_calibration/fsqca_sample.py)
folder <- "/path/to/output/main/"

samples <- c(
  full_sample                 = "sample0_fsQCA.csv",
  task_interdependence_mid    = "contingency_task_interdependence/sample0_fsQCA_task_interdependenceM.csv",
  task_interdependence_low    = "contingency_task_interdependence/sample0_fsQCA_task_interdependence0.csv",
  organization_owned          = "contingency_org/sample0_fsQCA_org1.csv",
  release_cycle_long          = "contingency_days/sample0_fsQCA_days1.csv",
  release_cycle_mid           = "contingency_days/sample0_fsQCA_daysM.csv",
  release_cycle_short         = "contingency_days/sample0_fsQCA_days0.csv"
)

tests <- c(
  "~dpi1 <- s1", "dsi1 <- s1", "~tpi1 <- s1", "tsi1 <- s1",
  "~dpi1 <- n1", "dsi1 <- n1", "~tpi1 <- n1", "tsi1 <- n1",
  "~dpi1 <- q1", "dsi1 <- q1", "~tpi1 <- q1", "tsi1 <- q1"
)

for (name in names(samples)) {
  data <- read.csv(paste0(folder, samples[[name]]), fileEncoding = "UTF-8-BOM")
  cat("\n==========", name, "(", nrow(data), "release cycles ) ==========\n")
  for (test in tests) {
    print(pof(test, data = data))
  }
}
