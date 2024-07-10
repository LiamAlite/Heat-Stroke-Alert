from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import os
import pandas as pd
import re

# Chromeオプション設定
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

# chromedriverのパス指定
chromedriver_path = '/usr/local/bin/chromedriver-linux64/chromedriver'

# WebDriverサービス開始
service = Service(chromedriver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# URLにアクセス
driver.get('https://www.wbgt.env.go.jp/alert.php')

# ページが完全に読み込まれるまで待機
time.sleep(5)

# ページの内容を取得
page_content = driver.page_source

# ドライバーを終了
driver.quit()

# コンテンツをパース
soup = BeautifulSoup(page_content, 'html.parser')

table = soup.find('table')  # 最初の<table>要素を取得
rows = table.find_all('tr')  # すべての<tr>要素を取得

first_row = rows[0]
first_row_cells = first_row.find_all('th') + first_row.find_all('td')
today_date_raw = first_row_cells[1].get_text(strip=True)
print(f"Debug: 今日の日付の生データ: {today_date_raw}")  # デバッグ用

# 正規表現で日付部分を抽出
match = re.search(r'\d+月\d+日', today_date_raw)
if match:
    today_date_cleaned = match.group()
else:
    today_date_cleaned = "日付情報が見つかりませんでした"

rows = rows[1:]

# テーブルの各行をループしてデータを抽出
all_data = []
max_columns = 0
for row in rows:

    headers = row.find_all('th')
    cells = row.find_all('td')
    
    header_data = [header.get_text(strip=True) for header in headers]
    
    cell_data = [cell.get_text(strip=True) for cell in cells]
    
    row_data = header_data + cell_data
    all_data.append(row_data)
    
    if len(row_data) > max_columns:
        max_columns = len(row_data)

# データを整形して列数を揃える
for i in range(len(all_data)):
    while len(all_data[i]) < max_columns:
        all_data[i].append('')

# 「関東甲信」が最初の要素である行を見つけ、その行のインデックスを取得
index = next((i for i, row in enumerate(all_data) if row[0] == '関東甲信'), None)

# 条件を満たす行とその下9行分を抜き出し
if index is not None:
    subset_data = all_data[index:index+10]
else:
    subset_data = []

# 4番目と5番目の要素を削除
subset_data = [row[:3] + row[5:] for row in subset_data]

new_data = []


header = ['関東甲信', '熱中症特別警戒アラート', '熱中症警戒アラート']

for row in subset_data:
    prefecture = row[0]
    special_alert = row[1]
    alert = row[2]
    
    # 特別警戒アラートと警戒アラートをチェックして新しい値を設定
    if special_alert == '●':
        new_data.append([prefecture, '特別警戒'])
    elif alert == '●':
        new_data.append([prefecture, '警戒'])
    else:
        new_data.append([prefecture, ''])

for row in new_data:
    print(row)