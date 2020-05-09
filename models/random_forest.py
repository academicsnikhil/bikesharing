import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_log_error
from sklearn.metrics import r2_score
import pickle

clustered_10 = pd.read_csv("datasets/clustered_10.csv")

X_10 = clustered_10.iloc[:, 0:4].values
y_10 = clustered_10.iloc[:, 4].values

X_10_train, X_10_test, y_10_train, y_10_test = train_test_split(X_10, y_10, test_size=0.20, random_state=42)

regressor_10 = RandomForestRegressor(n_estimators = 50, random_state = 0, max_leaf_nodes=3,min_samples_split=15)
regressor_10.fit(X_10_train,y_10_train)

pickle.dump(regressor_10, open('models/random_forest.pkl','wb'))

model = pickle.load(open('models/random_forest.pkl','rb'))
