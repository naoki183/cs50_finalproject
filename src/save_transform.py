#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 18 20:25:07 2021

@author: yoshidanaoki
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import Normalizer
from torch.utils.data import DataLoader, Dataset
from pickle import dump

class racedata(Dataset):
    
    def __init__(self, csv_path):
        data_set = pd.read_csv(csv_path)
        x = data_set.iloc[:, 1:]
        nm = Normalizer()
        x = nm.fit_transform(x)
        dump(nm, open("Kokura_scaler.pickle", "wb"))
        y = data_set.iloc[:, 0]
        y = np.array(y)
        self.x = x
        self.y = y
        
    def __getitem__(self, index):
        return self.x[index], self.y[index]
    
    def __len__(self):
        return len(self.x)

dataset = racedata('Kokura.csv')