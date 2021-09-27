#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 10 21:21:46 2021

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
        self.fc1 = Dense(97, 800)
        self.fc2 = Dense(800, 800)
        self.fc3 = Dense(800, 1)
    
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





#学習
for epoch in range(4000):
    loss = 0.0
    n = 0
    m = 0
    for train in trainloader:
        optimizer = optim.Adam(neuralnet.parameters(), lr = lr)
        x = train[0]
        y = train[1]
        if len(y) != batch_size:
            break
        optimizer.zero_grad()
        y_pred = neuralnet.forward(x)
        for i in range(len(y)):
            if y_pred[i] < 0.5:
                pred = 0
            else:
                pred = 1
            if pred == y[i]:
                m += 1
            n += 1
        y = y.view(len(y), 1)
        loss = criterion(y_pred, y)
        loss.backward()
        optimizer.step()
    train_loss = loss
    train_accuracy = m / n
    test_accuracy = 0.0
    n = 0
    m = 0
    for test in testloader:
        x = test[0]
        y = test[1]
        y_pred = neuralnet.forward(x)
        for i in range(len(y)):
            if y_pred[i] < 0.5:
                pred = 0
            else:
                pred = 1
            if pred == y[i]:
                m += 1
            n += 1
    test_accuracy = m / n
    
        
    test_accuracy = m / n
    print(str(epoch + 1) + '回目. ' + 'train loss: ' + str(train_loss) + ' train accuracy: '  + str(train_accuracy) + ' test accuracy: ' + str(test_accuracy))
    

    #アンサンブル学習
    if train_loss > 0.5:
        lr = 0.002
    if train_loss < 0.5 and train_loss > 0.1:
        lr = 0.0005
    else:
        lr = 0.0001

