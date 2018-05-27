#!/usr/bin/Rscript
#
# JUPAS scores prediction using multivariate linear regression with 
# L1 regularization 
#
# Reference:
#   Rothman, A.J., Levina, E., and Zhu, J. (2010). Sparse multivariate 
#     regression with covariance estimation. Journal of Computational and 
#     Graphical Statistics 19:974–962.
#

library(MRCE)
library(data.table)

# Read the dataset
dataset <- fread("dataset/preprocessed_JupasAdmData.csv")

# Add Program code
dataset$JS_Code <- ""
dataset[REMARKS == "PolyU CS program", JS_Code := "JS3868"]
dataset[REMARKS == "PolyU Nursing program", JS_Code := "JS3648"]
dataset[REMARKS == "PolyU Broad Disciple Business", JS_Code := "JS3131"]
dataset[REMARKS == "HKU Eng program", JS_Code := "JS6963"]
dataset[REMARKS == "HKU Science program", JS_Code := "JS6901"]
dataset[REMARKS == "HKU BBA program", JS_Code := "JS6808"]
dataset[REMARKS == "HKU Nursing program", JS_Code := "JS6848"]
dataset[REMARKS == "CUHK Engineering program", JS_Code := "JS4401"]
dataset[REMARKS == "CUHK Science program", JS_Code := "JS4601"]
dataset[REMARKS == "CUHK BBA program", JS_Code := "JS4202"]
dataset[REMARKS == "CUHK Nursing program", JS_Code := "JS4513"]

# Compute the Band A offer to applicants ratio
dataset <- dataset[, admission_rate := BAND_A_OFFER / BAND_A_APPL]

# Extract the dataset
dataset_Y <- dataset[!is.na(UpperQ) & Year != 2012 & Year != 2013, 
                     .(Year, JS_Code, UpperQ, Median, LowerQ)]
dataset_X <- dataset[!is.na(UpperQ) & Year != 2017 & Year != 2012, 
                     .(Year, JS_Code, admission_rate, Average,
                       ATU_MAX, ATU_MIN, ATU_AVG, is_science, is_BBA, 
                       is_nursing, is_engineering)]

# Construct the matrix
mat_Y <- as.matrix(dataset_Y[, .(UpperQ, Median, LowerQ)])
mat_X <- as.matrix(dataset_X[, .(admission_rate, ATU_MAX, ATU_MIN, ATU_AVG,
                                 is_science, is_BBA, is_nursing, 
                                 is_engineering)])

# Initialize the regularization parameter
lambdas <- rev(seq(from = 0, to = 1, by = 0.01))

# Fit a multivariate linear regression with L1 regularization on the regression
# coefficients and on the inverse covariance matrix with 5-fold cross validation
model_fit <- mrce(X = mat_X, Y = mat_Y, lam1.vec = lambdas, lam2.vec = lambdas, 
                  method = "cv")

# Construct the dataset for the score prediction from year 2013 to 2017
dataset_X_predict <- dataset[is.na(UpperQ) & Year != 2017]

# Construct the matrix
X_predict <- as.matrix(dataset_X_predict[, .(admission_rate, ATU_MAX, ATU_MIN, 
                                             ATU_AVG, is_science, is_BBA, 
                                             is_nursing, is_engineering)])

# Predict upper quantile, median, and lower quantile
Y_hat <- X_predict %*% model_fit$Bhat + matrix(rep(model_fit$muhat, nrow(X_predict)), 
                                               nrow = nrow(X_predict), 
                                               ncol = length(model_fit$muhat),
                                               byrow = TRUE)

# Compute the deviation
deviation_hat <- cbind(dataset_X_predict$ATU_MAX - Y_hat[, 2],
                       dataset_X_predict$ATU_MIN - Y_hat[, 2])

# Compute the maximun and minimum score prediction
Y_max_min_hat <- Y_hat[, c(1,3)] + deviation_hat
Y_max_min_hat_df <- as.data.table(cbind(
  Y_max_min_hat, dataset_X_predict[, .(Year+1, JS_Code, REMARKS)]))
colnames(Y_max_min_hat_df) <- c("Maximum", "Minimum", "Year", 
                                colnames(Y_max_min_hat_df)[-(1:3)])
fwrite(Y_max_min_hat_df, "submission/jupas_prediction_2013_to_2017.csv")

# Prepare dataset for 2018 prediction
dataset_X_predict_2018 <- dataset[is.na(UpperQ) & Year == 2017]
X_predict_2018 <- as.matrix(dataset_X_predict_2018[, .(admission_rate, ATU_MAX, ATU_MIN, 
                                                       ATU_AVG, is_science, is_BBA, 
                                                       is_nursing, is_engineering)])

# Predict upper quantile, median, and lower quantile for 2018
Y_hat_2018 <- X_predict_2018 %*% model_fit$Bhat + matrix(rep(model_fit$muhat, nrow(X_predict_2018)), 
                                               nrow = nrow(X_predict_2018), 
                                               ncol = length(model_fit$muhat),
                                               byrow = TRUE)

# Compute the deviation for 2018
deviation_hat_2018 <- cbind(dataset_X_predict_2018$ATU_MAX - Y_hat_2018[, 2],
                       dataset_X_predict_2018$ATU_MIN - Y_hat_2018[, 2])

# Compute the maximun and minimum score prediction for 2018
Y_max_min_hat_2018 <- Y_hat_2018[, c(1,3)] + deviation_hat_2018
Y_max_min_hat_2018_df <- as.data.table(cbind(
  Y_max_min_hat_2018, dataset_X_predict_2018[, .(Year+1, JS_Code, REMARKS)]))
colnames(Y_max_min_hat_2018_df) <- c("Maximum", "Minimum", "Year", 
                                colnames(Y_max_min_hat_2018_df)[-(1:3)])
fwrite(Y_max_min_hat_2018_df, "submission/jupas_prediction_2018.csv")

