#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 13 18:42:32 2021

@author: yoshidanaoki
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import normalize
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, Dataset
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torch
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
        y = torch.from_numpy(y).float()
        x = torch.from_numpy(x).float()
        self.x = x
        self.y = y
        
    def __getitem__(self, index):
        return self.x[index], self.y[index]
    
    def __len__(self):
        return len(self.x)

dataset = racedata('test2.csv')

batch_size = 256

#trainデータとtestデータに，全体を分ける
#train[0]は入力データ，train[1]は出力データ
trainset, testset = train_test_split(dataset, test_size = 1 / 7, shuffle = True)

#batch_sizeの分だけ訓練データからデータを取ってくる
#それぞれのtrainloaderは[0]が入力データ(項数97 * batch_sizeのベクトル), [1]が入力データ(項数1 * batch_sizeのベクトル)
trainloader = DataLoader(trainset, batch_size = batch_size, shuffle = True)
testloader = DataLoader(testset, batch_size = len(testset), shuffle = False)

rng = np.random.RandomState(1234)
random_state = 42

#全結合層の定義
class Dense(nn.Module):
    
    def __init__(self, in_dim, out_dim, function = lambda x: x):
        super().__init__()
        self.W = nn.Parameter(torch.tensor(rng.uniform(low = -np.sqrt(6 / in_dim), high = np.sqrt(6 / in_dim), size = (in_dim, out_dim)).astype('float32')))
        self.b = nn.Parameter(torch.tensor(np.zeros([out_dim]).astype('float32')))
        self.function = function
        
    def forward(self, x):
        return self.function(torch.matmul(x, self.W) + self.b)
    

class Net(nn.Module):
    
    def __init__(self):
        super(Net, self).__init__()
        self.fc1 = Dense(97, 1000)
        self.fc2 = Dense(1000, 1000)
        self.fc3 = Dense(1000, 2)
    
    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        """
        x = F.relu(self.fc3(x))
        x = F.relu(self.fc4(x))
        x = F.relu(self.fc5(x))
        x = F.relu(self.fc6(x))
        """
        return torch.sigmoid(x)

neuralnet = Net()
lr = 0.002
criterion = nn.BCELoss()
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



y_train = []
y_test = np.array(y_test)
y_test = torch.from_numpy(y_test).long()





#学習
for epoch in range(4000):
    y_train = []
    loss = 0.0
    n = 0
    m = 0
    pred = []
    for train in trainloader:
        optimizer = optim.Adam(neuralnet.parameters(), lr = lr)
        x = train[0]
        y = train[1]
        for i in range(len(y)):
            y_train.append(y[i])
        y_hot = torch.eye(2)[y.long()]
        optimizer.zero_grad()
        y_preds = neuralnet.forward(x)
        loss = criterion(y_preds, y_hot)
        loss.backward()
        optimizer.step()
        for i in range(len(y)):
            if y_preds[i][0] > y_preds[i][1]:
                y_pred = 0
            else:
                y_pred = 1
            pred.append(y_pred)  
    y_train = np.array(y_train)
    y_train = torch.from_numpy(y_train).long()
    train_loss = loss
    
    train_accuracy = accuracy_score(y_train, pred)
    test_accuracy = 0.0
    pred = []
    neuralnet.eval()
    for test in testloader:
        x = test[0]
        y = test[1]
        y_preds = neuralnet.forward(x)
        for i in range(len(y)):
            if y_preds[i][0] > y_preds[i][1]:
                y_pred = 0
            else:
                y_pred = 1
            
            pred.append(y_pred)
    test_accuracy = accuracy_score(y_test, pred)
    
    print(str(epoch + 1) + '回目. ' + 'train loss: ' + str(train_loss) + ' train accuracy: '  + str(train_accuracy) + ' test accuracy: ' + str(test_accuracy))
    

    #アンサンブル学習
    if train_loss > 0.5:
        lr = 0.002
    if train_loss < 0.5 and train_loss > 0.1:
        lr = 0.0005
    else:
        lr = 0.0001