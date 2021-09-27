#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 13 15:57:04 2021

@author: yoshidanaoki
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import normalize
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, Dataset
import lightgbm as lgbm
from sklearn.metrics import accuracy_score

#csv_pathはcsvファイルの場所
#ヘッダーが1行目にあることを想定
class racedata(Dataset):
    
    def __init__(self, csv_path):
        data_set = pd.read_csv(csv_path)
        x = data_set.iloc[:, 1:]
        x = normalize(x)
        y = data_set.iloc[:, 0]
        y = np.array(y)
        self.x = x
        self.y = y
        
    def __getitem__(self, index):
        return self.x[index], self.y[index]
    
    def __len__(self):
        return len(self.x)

dataset = racedata('Kokura.csv')


#trainデータとtestデータに，全体を分ける
#train[0]は入力データ，train[1]は出力データ
trainset, testset = train_test_split(dataset, test_size = 1 / 7, shuffle = True)
x_train = []
y_train = []
x_test = []
y_test = []

for train in trainset:
    x_train.append(train[0])
    y_train.append(train[1])

for test in testset:
    x_test.append(test[0])
    y_test.append(test[1])


x_train = np.array(x_train)
y_train = np.array(y_train)
x_test =  np.array(x_test)
y_test = np.array(y_test)


params = {"objective" : "binary",
          "boosting_type" : "gbdt",
          "metric" : "auc",
          "learning_rate" : 0.1,
          "num_iterations" : 100000,
          "num_leaves" : 200
         }


train_data = lgbm.Dataset(x_train, label = y_train)
test_data = lgbm.Dataset(x_test, label = y_test, reference = train_data)
model = lgbm.train(params, train_data, valid_sets = test_data,
                   early_stopping_rounds = 500, verbose_eval = 50)
model.save_model('Kokura_pred.txt')

preds = model.predict(x_test, num_iteration=model.best_iteration)
trains = model.predict(x_train, num_iteration=model.best_iteration)

y_trains = []
for y in trains:
    if y <= 0.5:
        y_trains.append(0)
    else:
        y_trains.append(1)

print("trains_accuracy: " + str(accuracy_score(y_train, y_trains)))


y_pred = []
for y in preds:
    if y <= 0.5:
        y_pred.append(0)
    else:
        y_pred.append(1)

print("test_accuracy: " + str(accuracy_score(y_test, y_pred)))




