import pandas as pd
import Tensorflow as tf
from tensorflow import keras
from keras.models import Sequential
from keras.layers import Dense, Activation
import matplotlib.pyplot as plt
import pickle
# pip install -q git+https://github.com/tensorflow/docs
import tensorflow_docs as tfdocs
import tensorflow_docs.plots
import tensorflow_docs.modeling

clustered_10 = pd.read_csv('datasets/clustered_10.csv')

# model for data with 10 clusters 
def build_model_10():
  model1 = Sequential()
  l = len(train_dataset_10.keys())
  model1.add(Dense(64, activation='relu', input_shape=[l]))
  model1.add(Dense(32, activation='relu'))
  model1.add(Dense(8, activation='relu'))
  model1.add(Dense(1)) 
  

  optimizer = tf.keras.optimizers.RMSprop(0.01)

  model1.compile(loss='mse',
                optimizer=optimizer,
                metrics=['mae', 'mse'])
  return model1


model1 = build_model_10()

print(model1.summary())

model1 = build_model_10()
EPOCHS=1000
# The patience parameter is the amount of epochs to check for improvement
early_stop_10 = keras.callbacks.EarlyStopping(monitor='val_loss', patience=15)

early_history_10 = model1.fit(train_dataset_10, train_labels_10, 
                    epochs=EPOCHS, validation_split = 0.2, verbose=0, 
                    callbacks=[early_stop_10, tfdocs.modeling.EpochDots()])

pickle.dump(early_history_10, open('linear_reg.pkl','wb'))
model = pickle.load(open('linear_reg.pkl','rb'))

hist_10 = pd.DataFrame(early_history_10.history)
hist_10['epoch'] = early_history_10.epoch
hist_10.tail()

test_predictions_10 = model1.predict(test_dataset_10).flatten()

example_batch_10 = test_dataset_10.tail(25)
example_result_10 = model1.predict(example_batch_10)
print(example_result_10)