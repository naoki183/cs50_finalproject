#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 17 21:16:35 2021

@author: yoshidanaoki
"""

import csv


with open('Sapporo.csv', 'w') as file1:
    writer = csv.writer(file1)
    writer.writerow([])
    with open('data.csv', 'r') as file:
        next(csv.reader(file))
        reader = csv.reader(file)
        for row in reader:
            if len(row) != 0 and row[5] == '0.1':
                data = []
                for i in range(5):
                    data.append(row[i])
                for i in range(6, 98):
                    data.append(row[i])
                writer.writerow(data)
            

with open('Hakodate.csv', 'w') as file1:
    writer = csv.writer(file1)
    writer.writerow([])
    with open('data.csv', 'r') as file:
        next(csv.reader(file))
        reader = csv.reader(file)
        for row in reader:
            if len(row) != 0 and row[5] == '0.2':
                data = []
                for i in range(5):
                    data.append(row[i])
                for i in range(6, 98):
                    data.append(row[i])
                writer.writerow(data)



with open('Fukushima.csv', 'w') as file1:
    writer = csv.writer(file1)
    writer.writerow([])
    with open('data.csv', 'r') as file:
        next(csv.reader(file))
        reader = csv.reader(file)
        for row in reader:
            if len(row) != 0 and row[5] == '0.3':
                data = []
                for i in range(5):
                    data.append(row[i])
                for i in range(6, 98):
                    data.append(row[i])
                writer.writerow(data)

with open('Nakayama.csv', 'w') as file1:
    writer = csv.writer(file1)
    writer.writerow([])
    with open('data.csv', 'r') as file:
        next(csv.reader(file))
        reader = csv.reader(file)
        for row in reader:
            if len(row) != 0 and row[5] == '0.4':
                data = []
                for i in range(5):
                    data.append(row[i])
                for i in range(6, 98):
                    data.append(row[i])
                writer.writerow(data)





with open('Tokyo.csv', 'w') as file1:
    writer = csv.writer(file1)
    writer.writerow([])
    with open('data.csv', 'r') as file:
        next(csv.reader(file))
        reader = csv.reader(file)
        for row in reader:
            if len(row) != 0 and row[5] == '0.5':
                data = []
                for i in range(5):
                    data.append(row[i])
                for i in range(6, 98):
                    data.append(row[i])
                writer.writerow(data)
                

with open('Niigata.csv', 'w') as file1:
    writer = csv.writer(file1)
    writer.writerow([])
    with open('data.csv', 'r') as file:
        next(csv.reader(file))
        reader = csv.reader(file)
        for row in reader:
            if len(row) != 0 and row[5] == '0.6':
                data = []
                for i in range(5):
                    data.append(row[i])
                for i in range(6, 98):
                    data.append(row[i])
                writer.writerow(data)

with open('Chukyo.csv', 'w') as file1:
    writer = csv.writer(file1)
    writer.writerow([])
    with open('data.csv', 'r') as file:
        next(csv.reader(file))
        reader = csv.reader(file)
        for row in reader:
            if len(row) != 0 and row[5] == '0.7':
                data = []
                for i in range(5):
                    data.append(row[i])
                for i in range(6, 98):
                    data.append(row[i])
                writer.writerow(data)

with open('Kyoto.csv', 'w') as file1:
    writer = csv.writer(file1)
    writer.writerow([])
    with open('data.csv', 'r') as file:
        next(csv.reader(file))
        reader = csv.reader(file)
        for row in reader:
            if len(row) != 0 and row[5] == '0.8':
                data = []
                for i in range(5):
                    data.append(row[i])
                for i in range(6, 98):
                    data.append(row[i])
                writer.writerow(data)
                
with open('Hanshin.csv', 'w') as file1:
    writer = csv.writer(file1)
    writer.writerow([])
    with open('data.csv', 'r') as file:
        next(csv.reader(file))
        reader = csv.reader(file)
        for row in reader:
            if len(row) != 0 and row[5] == '0.9':
                data = []
                for i in range(5):
                    data.append(row[i])
                for i in range(6, 98):
                    data.append(row[i])
                writer.writerow(data)

with open('Kokura.csv', 'w') as file1:
    writer = csv.writer(file1)
    writer.writerow([])
    with open('data.csv', 'r') as file:
        next(csv.reader(file))
        reader = csv.reader(file)
        for row in reader:
            if len(row) != 0 and row[5] != '0.1' and row[5] != '0.2' and row[5] != '0.3' and row[5] != '0.4' and row[5] != '0.5' and row[5] != '0.6' and row[5] != '0.7' and row[5] != '0.8' and row[5] != '0.9':
                data = []
                for i in range(5):
                    data.append(row[i])
                for i in range(6, 98):
                    data.append(row[i])
                writer.writerow(data)



