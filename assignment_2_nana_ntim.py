# -*- coding: utf-8 -*-
"""Assignment_2_Nana_Ntim.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1V9ahvZKB1s9V9hr8Gwi4Z2n-Qimhg-lk

# Data Preprocessing and Feature Engineering

## Imports
"""

# Essential Imports
import pandas as pd
import numpy as np
from google.colab import drive
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import OneHotEncoder
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split, GridSearchCV, KFold
from sklearn.preprocessing import StandardScaler
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import SimpleImputer, IterativeImputer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.ensemble import AdaBoostRegressor
from sklearn.tree import DecisionTreeRegressor
import pickle as pkl
from sklearn.model_selection import cross_val_score
import joblib
pd.options.mode.copy_on_write = True

drive.mount('/content/drive')
legacy_data = pd.read_csv('/content/drive/My Drive/male_players (legacy).csv')
players_22 = pd.read_csv('/content/drive/My Drive/players_22.csv')

"""## Exploratory Data Analysis"""

# Gives an overview about data
print(legacy_data.describe())

# Gives a count of missing values
print(legacy_data.isnull().sum())

# Gives a description of the data
print(legacy_data.describe())

"""## Imputation Function"""

# Cleans the data pased to it
def data_cleaning(data):

  # Drops data that has more 30% missing values or more
  threshold = len(data) * 0.7
  data = data.dropna(axis = 1, thresh = threshold)

  # Separates the data into numeric
  numeric = data.select_dtypes(include = np.number)

  # Separates the data into non-numeric
  non_numeric = data.select_dtypes(include = ['object'])

  # Calculates the mean values
  mean_values = numeric.mean()

  # Imputers missing values in numeric data and rounds to
  # the nearest integer
  data.loc[:, numeric.columns] = numeric.fillna(mean_values)

  # Finds the mode of the data and uses it
  # for the NA values
  for x in non_numeric:
    mode_value = non_numeric[x].mode()[0]
    non_numeric[x].fillna(mode_value, inplace = True)

  # Updates the main cleaned data with the new
  # cleaned non-numeric data
  data.update(non_numeric)

  # The columns that hold little influence over the
  # data are deleted here
  to_be_dropped = ['player_url', 'fifa_version', 'fifa_update',
    'fifa_update_date', 'player_face_url', 'short_name',
    'long_name', 'player_id', 'dob', 'league_name', 'league_id',
    'club_team_id', 'nationality_name', 'real_face',
    'club_jersey_number', 'club_position', 'player_positions',
    'club_contract_valid_until_year', 'club_name','club_joined_date'
    ]

  # Creates a loop to check if the column is in the new data
  # and deletes it
  for col in data.columns:

    # Checks for the column name from the list of names above
    if col in to_be_dropped:

      # drops the column once it's found in the list
      data.drop(col, axis = 1, inplace = True)

  # Returns the cleaned data after
  # cleaning is complete
  return pd.DataFrame(data)

"""## Removing Unwanted Columns"""

# Removing the data about players that shows what they could have as points
# if they had specific positions as it doesn't have a significant impact on
# the overall value the player has
def remove_extra(data):
  # Saves the filtered out columns
  filtered_columns = []

  # Loops through the columns
  for col in data.columns:

    # Removes the columns with more than 3 letters
    if len(col) > 3 or col == 'age':

      # Appends the column with the columns having more than 3 letters
      filtered_columns.append(col)

  # Gets the filtered data
  filtered_data = data[filtered_columns]

  # Returns the filtered data
  return filtered_data

def categorical_cleaner(data):

  # Gets the non-numeric data
  non_numeric = data.select_dtypes(include = ['object'])

  # Greates a dataframe for the categorical data
  categorical_data = pd.DataFrame(non_numeric)

  # Encode the data
  encoded_data = one_hot_encode(categorical_data)

  # Returns the final data
  return encoded_data

# Uses one hot encoding to encode the categorical
# variables
def one_hot_encode(categorical):

  # Creates the encoding instance
  converter = OneHotEncoder()

  # Encoding categorical values
  finished_conversion = (converter.fit_transform(categorical)).toarray()

  # Returns the encoded data and gets the feature names
  # for each category
  return pd.DataFrame(finished_conversion, columns = converter.get_feature_names_out(categorical.columns))

# Gets the correlation for your data for a specific target
def correlation(data, target):
  bad_correlation = []

  # Calculates the correlation matrix
  correlation_matrix = data.corr()

  # Gets the correlation values for the target variable
  # abs is used to make sure negative is not a factor
  target_correlation = correlation_matrix[target]

  # Sorts the correlation values in descending order
  sorted_correlation = target_correlation.sort_values(ascending = False)

  for col in sorted_correlation.index:
    if col != 'overall' and abs(sorted_correlation[col]) < 0.5:
      bad_correlation.append(col)

  final_data = data.drop(columns = bad_correlation, axis = 1)
  final_data.drop('overall', axis = 1)

  return final_data

def data_processing(data):

  # Removes the columns that are not needed
  data = remove_extra(data)

  # First level of cleaning clears NA values
  cleaned = data_cleaning(data)

  # Separates the cleaned numeric data
  numeric = cleaned.select_dtypes(include = np.number)

  # Separates the cleaned non-numeric data
  non_numeric = cleaned.select_dtypes(include = ['object'])

  # One-hot encodes the low cardinality columns
  encoded_data = categorical_cleaner(non_numeric)

  # Concatenates both numeric and non_numeric
  # dataframes
  final_numeric = pd.concat([numeric, encoded_data], axis = 1)

  # Get's the data with the highest 20 correlations
  corr_values = correlation(final_numeric, 'overall')

  # Returns the final cleaned data
  return corr_values

def scaling(data):
  # Creates an instance of StandardScalar
  scalar = StandardScaler()

  # Scales the data for reducing variability
  X_scaled = scalar.fit_transform(data)

  # Returns the scaled data
  return X_scaled

legacy_data_processed = data_processing(legacy_data)
legacy_data_processed

"""The features selected are: potential, value_eur, wage_eur, passing, dribbling, movement_reactions, mentality_composure

# Training
"""

X = legacy_data_processed.drop('overall', axis = 1)
y = legacy_data_processed['overall']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 42)

def random_forest_regressor(X_train, y_train, X_test, y_test):
  # Initializes the RandomForestRegressor
  regressor = RandomForestRegressor()

  # Trains the model
  regressor.fit(X_train, y_train)

  # Make predictions
  y_pred = regressor.predict(X_test)

  # Calculates the mean squared error
  r2score = r2_score(y_pred, y_test)
  mae = mean_absolute_error(y_pred, y_test)
  mse = mean_squared_error(y_pred, y_test)
  rmse = np.sqrt(mse)

  # Returns the mean squared error
  print(f""" Random Forest Regressor Results
    Mean Absolute Error={mae}
    Mean Squared Error={mse}
    Root Mean Squared Error={rmse}
    R2 score={r2score}
  """)

  return regressor

def xgboost(X_train, X_test, y_train, y_test):

  # Initializes the xgboost
  regressor = XGBRegressor()

  # Trains the model
  regressor.fit(X_train, y_train)

  # Make predictions
  y_pred = regressor.predict(X_test)

  # Calculates the mean squared error
  r2score = r2_score(y_pred, y_test)
  mae = mean_absolute_error(y_pred, y_test)
  mse = mean_squared_error(y_pred, y_test)
  rmse = np.sqrt(mse)

  # Returns the mean squared error
  print(f""" XGBoost Regressor Results
    Mean Absolute Error={mae}
    Mean Squared Error={mse}
    Root Mean Squared Error={rmse}
    R2 score={r2score}
  """)

  return regressor

def decision_tree_regressor(X_train, y_train, X_test, y_test):
  # Initializes the DecisionTreeRegressor
  regressor = DecisionTreeRegressor()

  # Trains the model
  regressor.fit(X_train, y_train)

  # Make predictions
  y_pred = regressor.predict(X_test)

  # Calculates the mean squared error
  r2score = r2_score(y_pred, y_test)
  mae = mean_absolute_error(y_pred, y_test)
  mse = mean_squared_error(y_pred, y_test)
  rmse = np.sqrt(mse)

  # Returns the mean squared error
  print(f""" Decision Tree Regressor Results
    Mean Absolute Error={mae}
    Mean Squared Error={mse}
    Root Mean Squared Error={rmse}
    R2 score={r2score}
  """)

  return regressor

def cross_validation(regressor, X_train, y_train, CV):

  # Initializes K-fold
  kfold = KFold(n_splits = 5, shuffle = True, random_state = 42)

  # Gets Cross validation scores for RandomFores
  cv_scores_rf = cross_val_score(regressor, X_train, y_train, cv = CV, scoring = 'r2')

  # Displays the r2 scores from the cross validation
  print(f'{type(regressor).__name__} Cross-Validation r2: {cv_scores_rf}')

  # Shows the mean for the values found
  return cv_scores_rf.mean()

def grid_search(regressor, X_train, y_train, CV):
  param_grid_ = {}

  if regressor.__class__.__name__ == 'RandomForestRegressor':
    param_grid_ = {
        'n_estimators': [200],
        'max_depth': [10, 20],
        'min_samples_split': [5],
        'min_samples_leaf': [1, 2]
  }
  elif regressor.__class__.__name__ == 'XGBRegressor':
    param_grid_ = {
        'n_estimators': [100, 200],
        'max_depth': [2, 3, 7],
        'learning_rate': [0.05, 0.2],
        'max_depth': [3, 7],
        'subsample': [0.8, 1.0]
  }
  elif regressor.__class__.__name__ == 'DecisionTreeRegressor':
    param_grid_ = {
        'max_depth': [10, 20],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4]
  }

  # Uses grid search for each regressor
  grid_search_run = GridSearchCV(estimator = regressor, param_grid = param_grid_, cv = CV, scoring = 'r2', n_jobs=-1)

  # Trains with the Grid search
  grid_search_run.fit(X_train, y_train)

  # Prints the best parameters and best score
  print(f'{type(regressor).__name__} Best Parameters: {grid_search_run.best_params_}')
  print(f'{type(regressor).__name__} Best Score: {grid_search_run.best_score_}')

  return grid_search_run.best_estimator_

def k_fold_cross_validation(regressors, X_train, y_train):
  # Initializes K-fold
  CV = KFold(n_splits = 5, shuffle = True, random_state = 42)

  values = []

  # Loops through each regressor
  for regressor in regressors:

    # Uses cross validation for each regressor
    value = cross_validation(regressor, X_train, y_train, CV)

    values.append(value)

  return values

def hyperparameter_tuning(regressor, X_train, y_train):

  # Initializes K-fold
  CV = KFold(n_splits = 5, shuffle = True, random_state = 42)

  # Uses grid search for each regressor
  model = grid_search(regressor, X_train, y_train, CV)

  return model

def pipe(X_train, X_test, y_train, y_test):

  # Runs the models to check their scores
  rf = random_forest_regressor(X_train, y_train, X_test, y_test)
  xg = xgboost(X_train, X_test, y_train, y_test)
  dt = decision_tree_regressor(X_train, y_train, X_test, y_test)

  regressors = [rf, xg, dt]

  # # Does Cross Evaluation
  values = k_fold_cross_validation(regressors, X_train, y_train)

  maximum = max(values)

  for index in range(len(regressors)):
    if values[index] == maximum:
      best_model = hyperparameter_tuning(regressors[index], X_train, y_train)
      break

  return best_model

overall_model = pipe(X_train, X_test, y_train, y_test)

important_features = ['potential', 'value_eur', 'wage_eur', 'passing', 'dribbling', 'movement_reactions', 'mentality_composure']

def model_evaluation(model, X_test, Y_test):

  prediction = model.predict(X_test)

  # Calculates the mean squared error
  r2score = r2_score(Ytest, prediction)
  mae = mean_absolute_error(prediction, Y_test)
  mse = mean_squared_error(prediction, Y_test)
  rmse = np.sqrt(mse)

  # Imports the model
  with open('/content/drive/My Drive/Regression_Model.pkl', 'wb') as model_file:
    pkl.dump(model, model_file)

  # Prints the metrics
  print(f'R2 Score: {r2score}')
  print(f'Mean Absolute Error: {mae}')
  print(f'Mean Squared Error: {mse}')
  print(f'Root Mean Squared Error: {rmse}')

Xtest = players_22[important_features]
Xtest = data_cleaning(Xtest)
Xtest = scaling(Xtest)
Ytest = players_22['overall']

model_evaluation(overall_model, Xtest, Ytest)