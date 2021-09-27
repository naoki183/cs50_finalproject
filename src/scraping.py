import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.autograd as autograd
import torch.nn.functional as F
from torchvision import datasets, transforms, models
import requests
from bs4 import BeautifulSoup
import time
import re
import pandas as pd
import csv


  
#dayはレースの日付("2021/08/05"など)
#馬のプロフィールサイトから馬mのデータを取ってくる関数
#urlは馬のプロフィールサイト
def gethorseinfo(url, day):
    
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
        elems = soup.select('#contents > div.db_main_race.fc > div > table > tbody > tr:nth-child(' + str(row[n]) + ') > td:nth-child(3)')
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
        elems = soup.select('#contents > div.db_main_race.fc > div > table > tbody > tr:nth-child(' + str(row[n]) + ') > td:nth-child(15)')
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
        elems = soup.select('#contents > div.db_main_race.fc > div > table > tbody > tr:nth-child(' + str(row[n]) + ') > td:nth-child(15)')
        if len(elems) != 1:
            return "none14-1-" + str(n)
        elem = elems[0].text
        number = re.sub(r"\D", "", elem)
        if len(number) != 4:
            return "none14-2-" + str(n)
        m_p_dist[n] = int(number) / 3000
        
        #馬mの前回レースのconditionを取得
        elems = soup.select('#contents > div.db_main_race.fc > div > table > tbody > tr:nth-child(' + str(row[n]) + ') > td:nth-child(16)')
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
        elems = soup.select('#contents > div.db_main_race.fc > div > table > tbody > tr:nth-child(' + str(row[n]) + ') > td:nth-child(23)')
        if len(elems) != 1:
            return "none16-1-" + str(n)
        elem = elems[0].text
        numbers = re.findall(r"\d+", elem)
        if len(numbers) != 2:
            return "none16-2-" + str(n)
        m_p_3time[n] = int(numbers[0]) + int(numbers[1]) / 10
        m_p_3time[n] /= 40
        
        #馬mの前回レースの場所を取得
        elems = soup.select('#contents > div.db_main_race.fc > div > table > tbody > tr:nth-child(' + str(row[n]) + ') > td:nth-child(2) > a')
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
                return "none18-1-" + str(n)
            elem = elems[0].text
            numbers1 = re.findall(r"\d+", elem)
            if len(numbers1) != 2:
                return "none18-2-" + str(n)
            elems = soup.select('#contents > div.db_main_race.fc > div > table > tbody > tr:nth-child(' + str(row[n + 1]) + ') > td:nth-child(24)')
            if len(elems) != 1:
                return "none18-3-" + str(n)
            elem = elems[0].text
            numbers2 = re.findall(r"\d+", elem)
            if len(numbers2) != 2:
                return "none18-4-" + str(n)
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
        elems = soup.select('#contents > div.db_main_race.fc > div > table > tbody > tr:nth-child(' + str(row[n]) + ') > td:nth-child(13)')
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
            return "none20-5-" + str(n)
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
    elems = soup.select('#contents > div.db_main_race.fc > div > table > tbody > tr:nth-child(' + str(i) + ') > td:nth-child(24)')
    if len(elems) == 0:
        return "none21-3"
    elem = elems[0].text
    numbers = re.findall(r"\d+", elem)
    if len(numbers) != 2:
        return "none21-4"
    if "+" in elem:
        m_weightchange = int(numbers[1])
    elif "-" in elem:
        m_weightchange = -int(numbers[1])
    elif int(numbers[1]) == 0:
        m_weightchange = 0
    else:
        return "none21-5"
    m_weightchange /= 20
    
    #馬mの当日のジョッキーの前年度成績を取得
    elems = soup.select('#contents > div.db_main_race.fc > div > table > tbody > tr:nth-child(' + str(i) + ') > td:nth-child(13)')
    elem = str(elems[0])
    numbers = re.findall(r"\d+", elem)
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
    for n in range(len(data)):
        if data[n] <= -2 or data[n] >= 2:
            return "none22-3"
     
    return data



#レースページからデータを取ってくる
#urlはレースページのurl
#[日付, レースデータ, 1位の馬から順番になっているプロフィールurl]を返す
def getraceinfo(url):
    
    html = requests.get(url)
    soup = BeautifulSoup(html.content, 'html.parser')
        
    #レースの距離を取得
    elems = soup.select('#main > div > div > div > diary_snap > div > div > dl > dd > p > diary_snap_cut > span')
    if len(elems) == 0:
        return "none23-1"
    elem = elems[0].text
    numbers = re.findall(r"\d+", elem)
    if len(numbers) != 3:
        return "none23-2"
    dist = int(numbers[0])
    dist /= 3000
        
    #レースのfieldを取得
    if "障" in elem:
        return "none24-1"
    elif "ダ" in elem:
        field = 1
    elif "芝" in elem:
        field = 2
    else:
        return "none24-2"
    field /= 2
        
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
        return "none25-1"
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
        return "none26-1"
    condi /= 4
        
    #レースの場所を取得
    elems = soup.select('#main > div > div > div > diary_snap > div > div > p')
    if len(elems) == 0:
        return "none27-1"
    elem = elems[0].text
    if "札幌" in elem:
        place = 1
    elif "函館" in elem:
        place = 2
    elif "福島" in elem:
        place = 3
    elif "中山" in elem:
        place = 4
    elif "東京" in elem:
        place = 5
    elif "新潟" in elem:
        place = 6
    elif "中京" in elem:
        place = 7
    elif "京都" in elem:
        place = 8
    elif "阪神" in elem:
        place = 9
    elif "小倉" in elem:
        place = 10
    else:
        return "none27-2"
    place /= 10
        
    #レースの日付を取得(要素数3のlist)
    numbers = re.findall(r"\d+", elem)
    if len(numbers) < 3:
        return "none28-1"
    if int(numbers[1]) < 10:
        numbers[1] = "0" + numbers[1]
    if int(numbers[2]) < 10:
        numbers[2] = "0" + numbers[2]
    day = numbers[0] + "/" + numbers[1] + "/" + numbers[2]
        
    #レース結果と性別を取得(1位から順番にプロフィールurlを並べる)
    result = []
    sex = []
    for i in range(2, 20, 1):
        elems = soup.select('#contents_liquid > table > tr:nth-child(' + str(i) + ') > td:nth-child(1)')
        if len(elems) == 0 and i == 2:
            return "none29-1"
        elif len(elems) == 0 and i != 2:
            break
        numbers = re.findall(r"\d+", str(elems[0]))
        if len(numbers) != 1:
            break
        elems = soup.select('#contents_liquid > table > tr:nth-child(' + str(i) + ') > td:nth-child(4)')
        numbers = re.findall(r"\d+", str(elems[0]))
        if len(numbers) == 0:
            return "none29-2"
        url2 = "https://db.netkeiba.com/horse/" + numbers[0] + "/"
        result.append(url2)
        elems = soup.select('#contents_liquid > table > tr:nth-child(' + str(i) + ') > td:nth-child(5)')
        if len(elems) != 1:
            return "none29-3"
        elem = elems[0].text
        if "牡" in elem:
            m_sex = 1
        elif "牝" in elem:
            m_sex = 2
        elif "セ" in elem:
            m_sex = 3
        sex.append(m_sex)
    
    
    data = []
    data.append(dist)
    data.append(field)
    data.append(weather)
    data.append(condi)
    data.append(place)
    for n in range(len(data)):
        if data[n] <= -2 or data[n] >= 2:
            return "none29-3"
    return [day, data, result, sex]



#レースデータのurlから[正解データ(勝：0，負:1), 入力データ(list)]のlistを取ってきてData(list)に入れる
#前の馬が勝ったら0，負けたら1
def makedata(Data, url):
    racedata = getraceinfo(url)
    if "none" in racedata:
        return "racedata is wrong. Error code: " + racedata + " URL: " + url
    horsenum = len(racedata[2])
    if horsenum < 2:
        return "racedata is wrong." + " URL: " +  url
    day = racedata[0]
    horseinfo = []
    time.sleep(1)
    for i in range(horsenum):
        #出走馬のデータ一覧(list)
        #1位から順に並ぶ
        a = gethorseinfo(racedata[2][i], day)
        if "none" in a:
            print(str(i + 1) + "th horse data is wrong. Error code: " + a + " URL: " + url)
            
        else:
            a.append(racedata[3][i])
            horseinfo.append(a)
            
        
        time.sleep(1)
        
    horsenum = len(horseinfo)
    if horsenum < 2:
        return "racedata is wrong." + " URL: " +  url
    for i in range(horsenum):
        if (i + 1) <= horsenum - 1:
            for j in range(i + 1, horsenum, 1):
                data = []
                data.append(0)
                for n in range(len(racedata[1])):
                    data.append(racedata[1][n])
                for n in range(len(horseinfo[i])):    
                    data.append(horseinfo[i][n])
                for n in range(len(horseinfo[j])):
                    data.append(horseinfo[j][n])
                Data.append(data)
        if i >= 1:
            for j in range(i):
                data = []
                data.append(1)
                for n in range(len(racedata[1])):
                    data.append(racedata[1][n])
                for n in range(len(horseinfo[i])):    
                    data.append(horseinfo[i][n])
                for n in range(len(horseinfo[j])):
                    data.append(horseinfo[j][n])
                Data.append(data)
        
    return 0

#レースデータのurlから正解ラベル，　入力データのcsvファイルを作る
#fileは'ファイルの場所'
def makecsv(file, url):
    Data = []
    with open(file, 'a') as f:
        writer = csv.writer(f)
        data = makedata(Data,url)
        if data == 0:
            writer.writerows(Data)
            return 0
        else:
            return data



#レースの日付の一覧を返す関数
#yearは何年から何年までか('2018,2020'など)
def makedaylist(year):
    days = []
    years = re.findall(r'\d+', year)
    year1 = int(years[0])
    year2 = int(years[1])
    for i in range(year1, year2 + 1, 1):
        for j in range(12):
            url = 'https://race.netkeiba.com/top/calendar.html?year=' + str(i) + '&month=' + str(j + 1)
            html = requests.get(url)
            soup = BeautifulSoup(html.content, 'html.parser')
            for k in range(2, 8, 1):
                for l in range(7):
                    elems = soup.select('.Race_Calendar_Main > table > tbody > tr:nth-child(' + str(k) + ') > td:nth-child(' + str(l + 1) + ') > a')
                    if len(elems) != 1:
                        continue
                    if len(elems[0].get('href')) == 0:
                        continue
                    day = elems[0].get('href')
                    day = re.findall(r'\d+', day)
                    day = day[0]
                    days.append(day)
            time.sleep(1)
    return days
                    
                    
                    
                    
                    
#レースの日付からレースのurlのリストをurllistに追加する関数
#dayは'20210808'など
#ダートか芝のみ
def getraceurl(day, urllist):
    url = 'https://db.netkeiba.com/race/list/' + day + '/'
    html = requests.get(url)
    soup = BeautifulSoup(html.content, 'html.parser')
    #iは何列目か
    for i in range(10):
        #jは何行目か
        for j in range(20):
            elems = soup.select('#main > div:nth-child(2) > div > div > dl:nth-child(' + str(i + 1) + ') > dd > ul > li:nth-child(' + str(j + 1) + ') > dl > dd > div')
            if len(elems) != 1:
                break
            elem = elems[0].text
            if 'ダ' or '芝' in elem:
                elems = soup.select('#main > div:nth-child(2) > div > div > dl:nth-child(' + str(i + 1) + ') > dd > ul > li:nth-child(' + str(j + 1) + ') > dl > dd > a')
                if len(elems) != 1:
                    continue
                elem = elems[0].get('href')
                url = 'https://db.netkeiba.com' + elem
                urllist.append(url)
        if j == 0:
            break
    return 0



#yearからyearまでの全てのurlのレースデータをfileにcsvとして追加する
#yearは'2018, 2020'など
def scraping(file, year):
    days = makedaylist(year)
    n = len(days)
    urllist = []
    for i in range(n):
        getraceurl(days[i], urllist)
    for i in range(len(urllist)):
        print(makecsv(file, urllist[i]))
        
scraping('data.csv', '2018, 2020')

#print(len(getraceurl('20201225')))
            
    
"""
url = 'https://db.netkeiba.com/race/list/20201227/'
Data = []
makedata(Data, url)
"""


#print(makecsv('test.csv', 'https://db.netkeiba.com/race/201606030811/'))

#print(makedaylist('2020, 2020'))



    
    
"""  
#レースのurlの取得
url = 'https://db.netkeiba.com/race/list/20201227/'
html = requests.get(url)
soup = BeautifulSoup(html.content, 'html.parser')
i = 0
j = 0
elems = soup.select('#main > div:nth-child(2) > div > div > dl:nth-child(' + str(i + 1) + ') > dd > ul > li:nth-child(' + str(j + 1) + ') > dl > dd > a')
print(elems[0].get('href'))
"""

"""
#レースの一覧のurlの取得
url = 'https://race.netkeiba.com/top/calendar.html?year=2020&month=8'
html = requests.get(url)
soup1 = BeautifulSoup(html.content, 'html.parser')
elems = soup1.select('.Race_Calendar_Main > table > tbody > tr:nth-child(2) > td:nth-child(6) > a')
#print(elems)
print(elems[0].get('href'))
"""



"""
url = 'https://db.netkeiba.com/race/201606030811/'
print(gethorseinfo(getraceinfo(url)[2][2], getraceinfo(url)[0]))
"""

"""
url = 'https://db.netkeiba.com/horse/2013104704/'
print(gethorseinfo(url, '2016/04/17'))
"""


      
