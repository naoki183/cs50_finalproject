#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 14 13:01:26 2021

@author: yoshidanaoki
"""

import numpy as np
import torch
import requests
from bs4 import BeautifulSoup
import re
import time
import pandas as pd
import csv
from flask import Flask, redirect, render_template, request
import pickle
from torch.utils.data import Dataset
import lightgbm as lgbm



app = Flask(__name__)


def getracedata(url):
    html = requests.get(url)
    soup = BeautifulSoup(html.content, 'html.parser')
    elems = soup.select('.RaceData01 > span:nth-child(1)')
    if len(elems) != 1:
        
        return "有効なURLを入力してください"
    elem = elems[0].text
    number = re.sub(r"\D", "", elem)
    
    #レースの距離を取得
    dist = int(number)
    dist /= 3000
    
    #レースのfieldを取得
    if 'ダ' in elem:
        field = 1
    elif '芝' in elem:
        field = 2
    else:
        return "ダートか芝のレースを入力してください"
    field /= 2
    
    elems = soup.select('.RaceData01')
    elem = elems[0].text
    
    
    #レースの天候を取得
    if "晴" in elem:
        weather = 1
    elif "曇" in elem:
        weather = 2
    elif "小雨" in elem:
        weather = 3
    elif "雨" in elem:
        weather = 4
    elif "小雪" in elem:
        weather = 5
    elif "雪" in elem:
        weather = 6
    else:
        return "レースデータが最新ではありません:天気を取得できません"
    weather /= 6
        
    #レースのコンディションを取得
    if "良" in elem:
        condi = 1
    elif "稍" in elem:
        condi = 2
    elif "重" in elem:
        condi = 3
    elif "不" in elem:
        condi = 4
    else:
        return "レースデータが最新ではありません:馬場コンディションを取得できません"
    condi /= 4
    
    #レースの場所を取得
    elems = soup.select('.RaceData02')
    if len(elems) == 0:
        return "レース情報に不備があります:レース場所が取得できません"
    elem = elems[0].text
    if "札幌" in elem:
        place = "Sapporo"
    elif "函館" in elem:
        place = "Hakodate"
    elif "福島" in elem:
        place = "Fukushima"
    elif "中山" in elem:
        place = "Nakayama"
    elif "東京" in elem:
        place = "Tokyo"
    elif "新潟" in elem:
        place = "Niigata"
    elif "中京" in elem:
        place = "Chukyo"
    elif "京都" in elem:
        place = "Kyoto"
    elif "阪神" in elem:
        place = "Hanshin"
    elif "小倉" in elem:
        place = "Kokura"
    else:
        return "レース情報に不備があります:レース場所が取得できません"
    
    #日付を取得
    elems = soup.select('#RaceList_DateList > dd.Active > a')
    if len(elems) != 1:
        return "レース情報に不備があります:レース日時が取得できません"
    elem = elems[0].get('title')
    numbers = re.findall(r"\d+", elem)
    if len(numbers) != 2:
        return "レース情報に不備があります:レース日時が取得できません"
    if int(numbers[0]) < 10:
        numbers[0] = "0" + numbers[0]
    if int(numbers[1]) < 10:
        numbers[1] = "0" + numbers[1]
    years = re.sub(r"\D", "", url)
    year = years[0] + years[1] + years[2] + years[3]
    day = year + "/" + numbers[0] + "/" + numbers[1]
    
    elems1 = soup.select('.HorseList')
    if len(elems1) == 0:
        return "レース情報に不備があります:出走馬を取得できません"
    horsenum = len(elems1)
    horses = [0] * horsenum
    for i in range(horsenum):
        horses[i] = []
        horseid = elems1[i].get('id')
        #馬のurlを取得
        elems = soup.select("#" + horseid + " > td.HorseInfo > div > div > span > a")
        if len(elems) != 1:
            return "レース情報に不備があります:出走馬のurlを取得できません"
        horseurl = elems[0].get('href')
        horsename = elems[0].get('title')
        #馬の性別を取得
        elems = soup.select("#" + horseid + " > td.Barei.Txt_C")
        if len(elems) != 1:
            return "レース情報に不備があります:出走馬の性別を取得できません"
        horsesex = elems[0].text
        if "牡" in horsesex:
            sex = 1
        elif "牝" in horsesex:
            sex = 2
        elif "セ" in horsesex:
            sex = 3
        else:
            return "レース情報に不備があります:出走馬の性別(牡or牝orセ)を取得できません"
        #馬のジョッキーを取得
        elems = soup.select("#" + horseid + " > td.Jockey > a")
        if len(elems) != 1:
            return "レース情報が最新ではありません:ジョッキーを取得できません"
        jockey = elems[0].get("href")
        #馬の体重増減を取得
        elems = soup.select("#" + horseid + " > td.Weight > small")
        if len(elems) != 1:
            return "レース情報が最新ではありません:馬の体重増減を取得できません"
        elem = elems[0].text
        numbers = re.findall(r"\d+", elem)
        if len(numbers) == 0:
            weightchange = 0
        else:
            number = numbers[0]
            if "-" in elem:
                weightchange = -int(number)
            elif "+" in elem:
                weightchange = int(number)
            elif number == "0":
                weightchange = 0
            else:
                return "レース情報が最新ではありません:馬の体重増減を取得できません"
        weightchange /= 20
        
        horses[i].append(horseurl)
        horses[i].append(sex)
        horses[i].append(jockey)
        horses[i].append(weightchange)
        horses[i].append(horsename)
    
        
        
         
    
    
    
    
    
    data = [0] * 5
    data[0] = dist
    data[1] = field
    data[2] = weather
    data[3] = condi
    return [data, day, horses, place]
    

def gethorseinfo(day, url, sex, jockey, weightchange):
    
    html = requests.get(url)
    soup = BeautifulSoup(html.content, 'html.parser')
    
    #馬mの適正フィールドを取得
    elems = soup.select('#db_main_box > div.db_main_deta > div > div.db_prof_area_01 > div.db_prof_box > dl > dd > table > tr:nth-of-type(1) > td > img:nth-of-type(1)')
    if len(elems) != 1:
        return "none2-1"
    width1 = elems[0].attrs['width']
    width1 = int(width1)
    elems = soup.select('#db_main_box > div.db_main_deta > div > div.db_prof_area_01 > div.db_prof_box > dl > dd > table > tr:nth-of-type(1) > td > img:nth-of-type(2)')
    width2 = elems[0].attrs['width']
    width2 = int(width2)
    m_field = width1 + width2
    if not 1 <= m_field and m_field <= 170:
        return "none2-2"
    m_field /= 170
    
    #馬mの適正コンディションを取得
    elems = soup.select('#db_main_box > div.db_main_deta > div > div.db_prof_area_01 > div.db_prof_box > dl > dd > table > tr:nth-of-type(5) > td > img:nth-of-type(1)')
    if len(elems) != 1:
        return "none3-1"
    width1 = elems[0].attrs['width']
    width1 = int(width1)
    elems = soup.select('#db_main_box > div.db_main_deta > div > div.db_prof_area_01 > div.db_prof_box > dl > dd > table > tr:nth-of-type(5) > td > img:nth-of-type(2)')
    if len(elems) != 1:
        return "none3-2"
    width2 = elems[0].attrs['width']
    width2 = int(width2)
    m_condi = width1 + width2
    if not 1 <= m_condi and m_condi <= 170:
        return "none3-3"
    m_condi /= 170
    
    #馬mの適正距離を取得
    elems = soup.select('#db_main_box > div.db_main_deta > div > div.db_prof_area_01 > div.db_prof_box > dl > dd > table > tr:nth-of-type(2) > td > img:nth-of-type(1)')
    width1 = elems[0].attrs['width']
    if len(elems) != 1:
        return "none4-1"
    width1 = int(width1)
    elems = soup.select('#db_main_box > div.db_main_deta > div > div.db_prof_area_01 > div.db_prof_box > dl > dd > table > tr:nth-of-type(2) > td > img:nth-of-type(2)')
    if len(elems) != 1:
        return "none4-2"
    width2 = elems[0].attrs['width']
    width2 = int(width2)
    m_dist = width1 + width2
    if not 1 <= m_dist and m_dist <= 170:
        return "none4-3"
    m_dist /= 170
    
    #馬mの脚質を取得
    elems = soup.select('#db_main_box > div.db_main_deta > div > div.db_prof_area_01 > div.db_prof_box > dl > dd > table > tr:nth-of-type(3) > td > img:nth-of-type(1)')
    if len(elems) != 1:
        return "none5-1"
    width1 = elems[0].attrs['width']
    width1 = int(width1)
    elems = soup.select('#db_main_box > div.db_main_deta > div > div.db_prof_area_01 > div.db_prof_box > dl > dd > table > tr:nth-of-type(3) > td > img:nth-of-type(2)')
    if len(elems) != 1:
        return "none5-2"
    width2 = elems[0].attrs['width']
    width2 = int(width2)
    m_style = width1 + width2
    if not 1 <= m_style and m_style <= 170:
        return "none5-3"
    m_style /= 170
     
    #馬mの成長特性を取得
    elems = soup.select('#db_main_box > div.db_main_deta > div > div.db_prof_area_01 > div.db_prof_box > dl > dd > table > tr:nth-of-type(4) > td > img:nth-of-type(1)')
    if len(elems) != 1:
        return "none6-1"
    width1 = elems[0].attrs['width']
    width1 = int(width1)
    elems = soup.select('#db_main_box > div.db_main_deta > div > div.db_prof_area_01 > div.db_prof_box > dl > dd > table > tr:nth-of-type(4) > td > img:nth-of-type(2)')
    if len(elems) != 1:
        return "none6-2"
    width2 = elems[0].attrs['width']
    width2 = int(width2)
    m_grow = width1 + width2
    if not 1 <= m_grow and m_grow <= 170:
        return "none6-3"
    m_grow /= 170
        
    #馬mの過去のレースデータを取得
    #馬mのそのレースにおける直近の過去3レースを取得
    day1 = re.sub(r"\D", "", day)
    day2 = re.findall(r"\d+", day)
    if len(day2) != 3:
        return "none7-1"
    day1 = int(day1)
    str1 = '#contents > div.db_main_race.fc > div > table > tbody > tr:nth-child('
    str3 = ') > td:nth-child(1) > a'
    for i in range(1, 1000, 1):
        elems = soup.select(str1 + str(i) + str3)
        if len(elems) != 1:
            return "none7-2"
        elem = elems[0].text
        number = re.sub(r"\D", "", elem)
        number = int(number)
        
        if number == day1:
            break
        elif i == 1 and number < day1:
            i = 0
            break
        
    #馬mの前回レースの100mあたりのタイムを取得
    #i+j番目の行に該当
    m_p_time = [0, 0, 0]
    for j in range(1, 1000, 1):      
        elems = soup.select('#contents > div.db_main_race.fc > div > table > tbody > tr:nth-child(' + str(i + j) + ') > td:nth-child(18)')
        if len(elems) != 1:
            return "none8-1"
        elem = elems[0]
        numbers = re.findall(r"\d+", elem.text)
        elems = soup.select('#contents > div.db_main_race.fc > div > table > tbody > tr:nth-child(' + str(i + j) + ') > td:nth-child(15)')
        if len(elems) != 1:
            return "none8-2"
        elem = elems[0]
        numbers1 = re.findall(r"\d+", elem.text)
        number = int(numbers1[0]) / 10
        elems = soup.select('#contents > div.db_main_race.fc > div > table > tbody > tr:nth-child(' + str(i + j) + ') > td:nth-child(1) > a')
        if len(elems) != 1:
            return "none8-3"
        elem = elems[0].text
        if len(numbers) == 3:
            m_p_time[0] = (60 * int(numbers[0]) + int(numbers[1]) + int(numbers[2]) / 10) / number
            m_p_time[0] *= 1.6
            break
        elif len(elem) > 0:
            j += 1
        else:
            return "none8-4"
        
    #馬mの前々回レースの100mあたりのタイムを取得
    #i+l番目の行に該当
    for l in range(j + 1, 1000, 1):      
        elems = soup.select('#contents > div.db_main_race.fc > div > table > tbody > tr:nth-child(' + str(i + l) + ') > td:nth-child(18)')
        if len(elems) != 1:
            return "none9-1"
        elem = elems[0]
        numbers = re.findall(r"\d+", elem.text)
        elems = soup.select('#contents > div.db_main_race.fc > div > table > tbody > tr:nth-child(' + str(i + l) + ') > td:nth-child(15)')
        if len(elems) != 1:
            return "none9-2"
        elem = elems[0]
        numbers1 = re.findall(r"\d+", elem.text)
        number = int(numbers1[0]) / 10
        elems = soup.select('#contents > div.db_main_race.fc > div > table > tbody > tr:nth-child(' + str(i + l) + ') > td:nth-child(1) > a')
        if len(elems) != 1:
            return "none9-3"
        elem = elems[0].text
        if len(numbers) == 3:
            m_p_time[1] = (60 * int(numbers[0]) + int(numbers[1]) + int(numbers[2]) / 10) / number
            m_p_time[1] *= 1.6
            break
        elif len(elem) > 0:
            l += 1
        else:
            return "none9-4"
    
    #馬mの前々前回レースの100mあたりのタイムを取得
    #i+k番目の行に該当   
    for k in range(l + 1, 1000, 1):      
        elems = soup.select('#contents > div.db_main_race.fc > div > table > tbody > tr:nth-child(' + str(i + k) + ') > td:nth-child(18)')
        if len(elems) != 1:
            return "none10-1"
        elem = elems[0]
        numbers = re.findall(r"\d+", elem.text)
        elems = soup.select('#contents > div.db_main_race.fc > div > table > tbody > tr:nth-child(' + str(i + k) + ') > td:nth-child(15)')
        if len(elems) != 1:
            return "none10-2"
        elem = elems[0]
        numbers1 = re.findall(r"\d+", elem.text)
        number = int(numbers1[0]) / 10
        elems = soup.select('#contents > div.db_main_race.fc > div > table > tbody > tr:nth-child(' + str(i + k) + ') > td:nth-child(1) > a')
        if len(elems) != 1:
            return "none10-3"
        elem = elems[0].text
        if len(numbers) == 3:
            m_p_time[2] = (60 * int(numbers[0]) + int(numbers[1]) + int(numbers[2]) / 10) / number
            m_p_time[2] *= 1.6
            break
        elif len(elem) > 0:
            k += 1
        else:
            return "none10-4"
        
    row1 = [0] * 3   
    #馬mの前回レースの100mあたりのタイムを取得
    #i+j番目の行に該当
    for j1 in range(1, 1000, 1):      
        elems = soup.select('#contents > div.db_main_race.fc > div > table > tbody > tr:nth-child(' + str(i + j1) + ') > td:nth-child(2) > a')
        if len(elems) != 1:
            return("none10-5")
        elem = elems[0].text
        if "札幌"  in elem or "函館" in elem or "福島" in elem or "中山" in elem or "東京" in elem or "新潟" in elem or "中京" in elem or "京都" in elem or "阪神" in elem or "小倉" in elem:
            elems = soup.select('#contents > div.db_main_race.fc > div > table > tbody > tr:nth-child(' + str(i + j1) + ') > td:nth-child(18)')
            elem = elems[0].text
            numbers = re.findall(r"\d+", elem)
            if len(numbers) == 0:
                continue
            time = int(numbers[0]) * 60 + int(numbers[1]) + int(numbers[2]) / 10
            elems = soup.select('#contents > div.db_main_race.fc > div > table > tbody > tr:nth-child(' + str(i + j1) + ') > td:nth-child(15)')
            elem = elems[0].text
            dist = re.sub(r"\D", "", elem)
            dist = int(dist)
            dist /= 10
            m_p_time[0] = time * 1.6 / dist
            row1[0] = i + j1
            break
    #馬mの前々回レースの100mあたりのタイムを取得
    #i+k1番目の行に該当
    for k1 in range(j1 + 1, 1000, 1):      
        elems = soup.select('#contents > div.db_main_race.fc > div > table > tbody > tr:nth-child(' + str(i + k1) + ') > td:nth-child(2) > a')
        if len(elems) != 1:
            return("none10-5")
        elem = elems[0].text
        if "札幌" in elem or "函館" in elem or "福島" in elem or "中山" in elem or "東京" in elem or "新潟" in elem or "中京" in elem or "京都" in elem or "阪神" in elem or "小倉" in elem:
            elems = soup.select('#contents > div.db_main_race.fc > div > table > tbody > tr:nth-child(' + str(i + k1) + ') > td:nth-child(18)')
            elem = elems[0].text
            numbers = re.findall(r"\d+", elem)
            if len(numbers) == 0:
                continue
            time = int(numbers[0]) * 60 + int(numbers[1]) + int(numbers[2]) / 10
            elems = soup.select('#contents > div.db_main_race.fc > div > table > tbody > tr:nth-child(' + str(i + k1) + ') > td:nth-child(15)')
            elem = elems[0].text
            dist = re.sub(r"\D", "", elem)
            dist = int(dist)
            dist /= 10
            m_p_time[1] = time * 1.6 / dist
            row1[1] = i + k1
            break
    
    #馬mの前々前回レースの100mあたりのタイムを取得
    #i+l1番目の行に該当   
    for l1 in range(k1 + 1, 1000, 1):      
        elems = soup.select('#contents > div.db_main_race.fc > div > table > tbody > tr:nth-child(' + str(i + l1) + ') > td:nth-child(2) > a')
        if len(elems) != 1:
            return("none10-5")
        elem = elems[0].text
        if "札幌" in elem or "函館" in elem or "福島" in elem or "中山" in elem or "東京" in elem or "新潟" in elem or "中京" in elem or "京都" in elem or "阪神" in elem or "小倉" in elem:
            elems = soup.select('#contents > div.db_main_race.fc > div > table > tbody > tr:nth-child(' + str(i + l1) + ') > td:nth-child(18)')
            elem = elems[0].text
            numbers = re.findall(r"\d+", elem)
            if len(numbers) == 0:
                continue
            time = int(numbers[0]) * 60 + int(numbers[1]) + int(numbers[2]) / 10
            elems = soup.select('#contents > div.db_main_race.fc > div > table > tbody > tr:nth-child(' + str(i + l1) + ') > td:nth-child(15)')
            elem = elems[0].text
            dist = re.sub(r"\D", "", elem)
            dist = int(dist)
            dist /= 10
            m_p_time[2] = time * 1.6 / dist
            row1[2] = i + l1
            break
    
 
    
    row = [0, 0, 0, 0]
    row[0] = i + j
    row[1] = i + l
    row[2] = i + k
    m_p_weather = [0, 0, 0]
    m_p_field = [0, 0, 0]
    m_p_dist = [0, 0, 0]
    m_p_condi = [0, 0, 0]
    m_p_3time = [0, 0, 0]
    m_p_place = [0, 0, 0]
    m_p_weightchange = [0, 0]
    m_p_timespan = [0, 0]
    m_p_age = [0, 0, 0]
    m_p_jockey = [0, 0, 0]
    
    for n in range(3):
        #馬mの前回レースの天候を取得
        elems = soup.select('#contents > div.db_main_race.fc > div > table > tbody > tr:nth-child(' + str(row1[n]) + ') > td:nth-child(3)')
        if len(elems) != 1:
            return "none12-1-" + str(n)
        elem = elems[0].text
        if elem == "晴":
            m_p_weather[n] = 1
        elif elem == "曇":
            m_p_weather[n] = 2
        elif elem == "小雨":
            m_p_weather[n] = 3
        elif elem == "雨":
            m_p_weather[n] = 4
        elif elem == "小雪":
            m_p_weather[n] = 5
        elif elem == "雪":
            m_p_weather[n] = 6
        else:
            return "none12-2-" + str(n)
        m_p_weather[n] /= 6
        
        #馬mの前回レースのfieldを取得
        elems = soup.select('#contents > div.db_main_race.fc > div > table > tbody > tr:nth-child(' + str(row1[n]) + ') > td:nth-child(15)')
        if len(elems) != 1:
            return "none13-1-" + str(n)
        elem = elems[0].text
        if "ダ" in elem:
            m_p_field[n] = 1
        elif "芝" in elem:
            m_p_field[n] = 2
        else:
            return "none13-2-" + str(n)
        m_p_field[n] /= 2
        
        #馬mの前回レースの距離を取得
        elems = soup.select('#contents > div.db_main_race.fc > div > table > tbody > tr:nth-child(' + str(row1[n]) + ') > td:nth-child(15)')
        if len(elems) != 1:
            return "none14-1-" + str(n)
        elem = elems[0].text
        number = re.sub(r"\D", "", elem)
        if len(number) != 4:
            return "none14-2-" + str(n)
        m_p_dist[n] = int(number) / 3000
        
        #馬mの前回レースのconditionを取得
        elems = soup.select('#contents > div.db_main_race.fc > div > table > tbody > tr:nth-child(' + str(row1[n]) + ') > td:nth-child(16)')
        if len(elems) != 1:
            return "none15-1-" + str(n)
        elem = elems[0].text
        if "良" in elem:
            m_p_condi[n] = 1
        elif "稍" in elem:
            m_p_condi[n] = 2
        elif "重" in elem:
            m_p_condi[n] = 3
        elif "不" in elem:
            m_p_condi[n] = 4
        else:
            return "none15-2-" + str(n)
        m_p_condi[n] /= 4
        
            
        #馬mの前回レースの上がり3ハロンのタイムを取得
        elems = soup.select('#contents > div.db_main_race.fc > div > table > tbody > tr:nth-child(' + str(row1[n]) + ') > td:nth-child(23)')
        if len(elems) != 1:
            return "none16-1-" + str(n)
        elem = elems[0].text
        numbers = re.findall(r"\d+", elem)
        if len(numbers) != 2:
            return "none16-2-" + str(n)
        m_p_3time[n] = int(numbers[0]) + int(numbers[1]) / 10
        m_p_3time[n] /= 40
        
        #馬mの前回レースの場所を取得
        elems = soup.select('#contents > div.db_main_race.fc > div > table > tbody > tr:nth-child(' + str(row1[n]) + ') > td:nth-child(2) > a')
        if len(elems) != 1:
            return "none17-1-" + str(n)
        elem = elems[0].text
        if "札幌" in elem:
            m_p_place[n] = 1
        elif "函館" in elem:
            m_p_place[n] = 2
        elif "福島" in elem:
            m_p_place[n] = 3
        elif "中山" in elem:
            m_p_place[n] = 4
        elif "東京" in elem:
            m_p_place[n] = 5
        elif "新潟" in elem:
            m_p_place[n] = 6
        elif "中京" in elem:
            m_p_place[n] = 7
        elif "京都" in elem:
            m_p_place[n] = 8
        elif "阪神" in elem:
            m_p_place[n] = 9
        elif "小倉" in elem:
            m_p_place[n] = 10
        else:
            return "none17-2-" + str(n)
        m_p_place[n] /= 10
        
        #馬mの前回レースの体重増減を取得
        if n <= 1:
            elems = soup.select('#contents > div.db_main_race.fc > div > table > tbody > tr:nth-child(' + str(row[n]) + ') > td:nth-child(24)')
            if len(elems) != 1:
                m_p_weightchange[n] = 0
            else:
                elem = elems[0].text
                numbers1 = re.findall(r"\d+", elem)
                if len(numbers1) != 2:
                    m_p_weightchange[n] = 0
                else:
                    elems = soup.select('#contents > div.db_main_race.fc > div > table > tbody > tr:nth-child(' + str(row[n + 1]) + ') > td:nth-child(24)')
                    if len(elems) != 1:
                        m_p_weightchange[n] = 0
                    else:
                        elem = elems[0].text
                        numbers2 = re.findall(r"\d+", elem)
                        if len(numbers2) != 2:
                            m_p_weightchange[n] = 0
                        else:
                            m_p_weightchange[n] = int(numbers1[0]) - int(numbers2[0])
            m_p_weightchange[n] /= 20 #正規化
        
        #馬mの前回レースの経過時間を取得
        if n <= 1:
            elems = soup.select('#contents > div.db_main_race.fc > div > table > tbody > tr:nth-child(' + str(row[n]) + ') > td:nth-child(1)')
            if len(elems) != 1:
                return "none19-1-" + str(n)
            elem = elems[0].text
            numbers1 = re.findall(r"\d+", elem)
            if len(numbers1) != 3:
                return "none19-2-" + str(n)
            elems = soup.select('#contents > div.db_main_race.fc > div > table > tbody > tr:nth-child(' + str(row[n + 1]) + ') > td:nth-child(1)')
            if len(elems) != 1:
                return "none19-3-" + str(n)
            elem = elems[0].text
            numbers2 = re.findall(r"\d+", elem)
            if len(numbers2) != 3:
                return "none19-4-" + str(n)
            m_p_timespan[n] = (int(numbers1[0]) - int(numbers2[0])) * 365 + (int(numbers1[1]) - int(numbers2[1])) * 30 + (int(numbers1[2]) - int(numbers2[2]))
            m_p_timespan[n] /= 365 #正規化
        
        #馬mの前回レースの年齢を取得
        elems = soup.select('#contents > div.db_main_race.fc > div > table > tbody > tr:nth-child(' + str(row1[n]) + ') > td:nth-child(1)')
        if len(elems) != 1:
            return "none19-5-" + str(n)
        elem = elems[0].text
        numbers1 = re.findall(r"\d+", elem)
        if len(numbers1) != 3:
            return "none19-6-" + str(n)
        elems = soup.select('#db_main_box > div.db_main_deta > div > div.db_prof_area_02 > table > tr:nth-child(1) > td')
        if len(elems) != 1:
            return "none20-1-" + str(n)
        elem = elems[0].text
        numbers3 = re.findall(r"\d+", elem)
        if len(numbers3) != 3:
            return "none20-2-" + str(n)
        m_p_age[n] = int(numbers1[0]) - int(numbers3[0]) + (int(numbers1[1]) - int(numbers3[1])) / 12
        m_p_age[n] /= 6 #正規化
        
        #馬mの前回レースのジョッキーの前年度順位を取得
        elems = soup.select('#contents > div.db_main_race.fc > div > table > tbody > tr:nth-child(' + str(row1[n]) + ') > td:nth-child(13)')
        elem = str(elems[0])
        numbers = re.findall(r"\d+", elem)
        if len(numbers) != 1:
            return "none20-3-" + str(n)
        number = numbers[0]
        url1 = "https://db.netkeiba.com/jockey/result/" + number + "/"
        html1 = requests.get(url1)
        soup1 = BeautifulSoup(html1.content, 'html.parser')
        year = numbers1[0]
        str1 = '#contents_liquid > table > tr:nth-child('
        str3 = ') > td.txt_c'
        for a in range(4, 100, 1):
            elems = soup1.select(str1 + str(a) + str3)
            if len(elems) == 0:
                return "none20-4-" + str(n)
            elem = elems[0].text
            if year in elem:
                break
        elems = soup1.select('#contents_liquid > table > tr:nth-child(' + str(a + 1) + ') > td:nth-child(2)')
        if len(elems) == 0:
            m_p_jockey[n] = 0
        else:
            elem = elems[0].text
            m_p_jockey[n] = int(elem)
        m_p_jockey[n] /= 130
    
    #馬mのレース当日の年齢を取得
    day2 = re.findall(r"\d+", day)
    elems = soup.select('#db_main_box > div.db_main_deta > div > div.db_prof_area_02 > table > tr:nth-child(1) > td')
    if len(elems) != 1:
        return "none21-1"
    elem = elems[0].text
    m_birthday = re.findall(r"\d+", elem)
    if len(m_birthday) != 3:
        return "none21-2"
    m_age = int(day2[0]) - int(m_birthday[0]) + (int(day2[1]) - int(m_birthday[1])) / 12
    m_age /= 6
    
    #馬mのレース当日の前回レースからの経過時間を取得
    elems = soup.select('#contents > div.db_main_race.fc > div > table > tbody > tr:nth-child(' + str(row[0]) + ') > td:nth-child(1)')
    elem = elems[0].text
    numbers1 = re.findall(r"\d+", elem)
    m_timespan = (int(day2[0]) - int(numbers1[0])) * 365 + (int(day2[1]) - int(numbers1[1])) * 30 + (int(day2[2]) - int(numbers1[2]))
    m_timespan /= 365 #正規化
    
    #馬mのレース当日の体重増減を取得
    m_weightchange = weightchange
    
    #馬mの当日のジョッキーの前年度成績を取得
    url1 = jockey
    numbers = re.findall(r"\d+", url1)
    if len(numbers) != 1:
        return "none21-6"
    number = numbers[0]
    url1 = "https://db.netkeiba.com/jockey/result/" + number + "/"
    html1 = requests.get(url1)
    soup1 = BeautifulSoup(html1.content, 'html.parser')
    numbers = re.findall(r"\d+", day)
    if len(numbers) != 3:
        return "none21-7"
    year = numbers[0]
    str1 = '#contents_liquid > table > tr:nth-child('
    str3 = ') > td.txt_c'
    for a in range(4, 100, 1):
        elems = soup1.select(str1 + str(a) + str3)
        if len(elems) == 0:
            return "none21-8"
        elem = elems[0].text
        if year in elem:
            break
    elems = soup1.select('#contents_liquid > table > tr:nth-child(' + str(a + 1) + ') > td:nth-child(2)')
    if len(elems) == 0:
        return "none21-9"
    elem = elems[0].text
    m_jockey = int(elem)
    m_jockey /= 130
    
    
    if m_p_jockey[0] == 0:
        m_p_jockey[0] = m_jockey
    if m_p_jockey[1] == 0:
        m_p_jockey[1] = m_jockey
    if m_p_jockey[2] == 0:
        m_p_jockey[2] = m_jockey
    #馬mの性別を取得
    m_sex = sex
    
    #馬mのそのレース時点での通算成績を取得
    m_record1 = 0
    m_record2 = 0
    m_record3 = 0
    m_record4 = 0
    for n in range(1, 1000, 1):
        elems = soup.select('#contents > div.db_main_race.fc > div > table > tbody > tr:nth-child(' + str(n + i) +  ')> td:nth-child(1) > a')
        if len(elems) == 0:
            break
        elems = soup.select('#contents > div.db_main_race.fc > div > table > tbody > tr:nth-child(' + str(n + i) + ') > td.txt_right')
        elem = elems[6].text
        if elem == "1":
            m_record1 += 1
        elif elem == "2":
            m_record2 += 1
        elif elem == "3":
            m_record3 += 1
        elif elem.isdecimal() == True and 4 <= int(elem) and int(elem) <= 18:
            m_record4 += 1
    total = m_record1 + m_record2 + m_record3 + m_record4
    m_record1 = m_record1 / total
    m_record2 = m_record2 / total
    m_record3 = m_record3 / total
    m_record4 = m_record4 / total
    m_total = total
    m_total /= 100
            
    

    
    data = []
    data.append(m_record1)
    data.append(m_record2)
    data.append(m_record3)
    data.append(m_record4)
    data.append(m_total)
    data.append(m_condi)
    data.append(m_dist)
    data.append(m_field)
    data.append(m_grow)
    data.append(m_style)
    
    for i in range(3):
        data.append(m_p_time[i])
        data.append(m_p_weather[i])
        data.append(m_p_field[i])
        data.append(m_p_dist[i])
        data.append(m_p_condi[i])
        data.append(m_p_3time[i])
        data.append(m_p_place[i])
        if i <= 1:
            data.append(m_p_weightchange[i])
            data.append(m_p_timespan[i])
        data.append(m_p_age[i])
        data.append(m_p_jockey[i])
    data.append(m_age)
    data.append(m_timespan)
    data.append(m_weightchange)
    data.append(m_jockey)
    data.append(m_sex)
    
    
     
    return data


def getdata(url):
    horseinfo = getracedata(url)
    time.sleep(1)
    if len(horseinfo) != 4:
        return horseinfo
    day = horseinfo[1]
    racedata = horseinfo[0]
    place = horseinfo[3]
    horsenum = len(horseinfo[2])
    #出走馬の情報を枠順にしたがって入れる(データが足りない時はアラート(nonexx)の内容が入る)
    horses = [0] * horsenum
    horsenames = [0] * horsenum
    for i in range(horsenum):
         horses[i] = gethorseinfo(day, horseinfo[2][i][0], horseinfo[2][i][1], horseinfo[2][i][2], horseinfo[2][i][3])
         horsenames[i] = horseinfo[2][i][4]
         time.sleep(1)
    return [racedata, horses, horsenum, horsenames, place]


#入力データを生成
def dataload(place, data):
    sc = pickle.load(open(place + "_scaler.pickle", "rb"))
    x = sc.transform(data)
    return x

def apology(sentence):
    return render_template("index.html", sentence = sentence)

@app.route("/", methods=["GET", "POST"])
def predict():
    if request.method == "GET":
        return render_template("index.html", sentence = 0)
    else:
        url = request.form.get("url")
        if not 'https://race.netkeiba.com/race/shutuba.html?race_id=' in url:
            return apology("有効なURLを入力してください")
        data = getdata(url)
        if len(data) != 5:
            return apology(data)
        place = data[4]
        model = lgbm.Booster(model_file = place + "_pred.txt")
        #horselist(インデックスは馬番を表す), horsenumlist(インデックスは0から，値は馬番)は情報がある馬のリスト
        #errorlistは情報がない馬のリスト
        horselist = [0] * 19
        errorlist = []
        horsenumlist = []
        horsenum = data[2]
        for i in range(horsenum):
            if len(data[1][i]) == 46:
                horselist[i + 1] = {}
                horselist[i + 1]["num"] = i + 1
                horselist[i + 1]["name"] = str(i + 1) + ". " + data[3][i]
                horsenumlist.append(i + 1)
            else:
                errorlist.append(str(i + 1) + ". " + data[3][i] + ": " + data[1][i])
        #レース結果をresultに入れる(result[][]は前者が勝ちなら0，後者が勝ちなら1)
        #indexは馬番(1から始まる)なので注意
        result = [2] * 19
        for i in range(19):
            result[i] = [2] * 19
        #inputdata1は馬1が馬番が小さい方で，input2は馬1が馬番が大きい方になるように代入
        inputdata1 = [0] * 96
        inputdata2 = [0] * 96
        for i in range(4):
            inputdata1[i] = data[0][i]
            inputdata2[i] = data[0][i]
        for i in horsenumlist:
            for j in horsenumlist:
                if i < j:
                    for n in range(len(data[1][i - 1])):
                        inputdata1[4 + n] = data[1][i - 1][n]
                        inputdata2[50 + n] = data[1][i - 1][n]
                    for n in range(len(data[1][j - 1])):
                        inputdata1[50 + n] = data[1][j - 1][n]
                        inputdata2[4 + n] = data[1][j - 1][n]
                    inputdata = []
                    inputdata.append(inputdata1)
                    inputdata.append(inputdata2)
                    inputdata = dataload(place, inputdata)
                    pred = model.predict(inputdata)
                    if pred[0] < pred[1]:
                        result[i][j] = 0
                        result[j][i] = 1
                    else:
                        result[i][j] = 1
                        result[j][i] = 0
            result[i][i] = -1
        
        horsenum = len(horsenumlist)
            
        #馬番horsenumlist[n]の馬が勝つ回数がwinnum[n]
        winnum = [0] * horsenum
        for i in range(horsenum):
            for j in range(horsenum):
                if result[horsenumlist[i]][horsenumlist[j]] == 0:
                    winnum[i] += 1
        winnum1 = [0] * horsenum
        winnum2 = winnum.copy()
        winnum2.sort(reverse = True)
        
        

        for i in range(horsenum):
            for j in range(horsenum):
                if winnum2[i] == winnum[j]:
                    winnum1[i] = j
                    winnum[j] = -100
                    break
                
      
        
        for i in range(horsenum):
            winnum[i] = horselist[horsenumlist[winnum1[i]]]["name"] + ":" + str(winnum2[i]) + "勝"
        horsenum1 = horsenum - 1
        return render_template("predict.html", sentence=0, horsenum=horsenum, horselist=horselist, errorlist=errorlist, result=result, winnum=winnum, horsenum1 = horsenum1)
                   
if __name__ == '__main__':
    app.run()             
                        
                        
        
        
        
        
        
        
        
    
    
    
             
    


