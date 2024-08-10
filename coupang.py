import re

import requests


def Coupang():
    # 相關變數設定
    Website = "酷澎Coupang"  # 平台
    # MinPrice = 5.03  # 上次購入的最低價
    ManyPerDay = 8  # 單日用量
    size = 'L'  # 尺寸
    item = '尿布'  # 品項
    othercritiria = '黏貼'  # 其他條件
    Keyword = f"{item} {othercritiria} {size}"

    # 瀏覽器
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
    content_type = "application/json"
    # origin = "https://www.tw.coupang.com"
    header = {
        "User-Agent": user_agent,
        # "Cookie": cookie,
        "Content-Type": content_type,
    }
    datas = {"sort": ["DEFAULT"], "filter": "", "keyword": Keyword, "start": 0, "limit": 60}
    r = requests.post("https://www.tw.coupang.com/search", headers=header, json=datas)
    arrR = r.json()['data']['products']
    # arrR[1]

    dict_Arr = []
    max = 60
    for i in range(0, max):
        titleArr = arrR[i]['title'].split(",")
        price = arrR[i]['priceInfo']['price']
        brand = titleArr[0]
        if "成人" not in brand and "大人" not in brand:
            # print(i, brand)
            amount = titleArr[2].strip()
            amount = re.findall(r"\d+", amount)[0]
            unitprice = round(float(price) / float(amount), 4)  # 四捨五入
            dict_Arr.append({'廠牌': brand, '價格': price, '總片數': amount, '單價': unitprice})

    dict_Arr = sorted(dict_Arr, key=lambda x: x['單價'])

    message = f"\n｜百萬現在尺寸: {size} , 用量:{ManyPerDay}片/天｜\n"

    message += (
        f"\n平台：{Website}\n項目：{Keyword}\n目前最低價前三名是\n--------------------------\n"
    )
    for i in range(0, 3):

        howlong2use = int(float(dict_Arr[i]["總片數"]) / float(ManyPerDay))
        message += f'第{i + 1}名    單片${dict_Arr[i]["單價"]}\n【{dict_Arr[i]["廠牌"]}】\n${dict_Arr[i]["價格"]} 共{dict_Arr[i]["總片數"]}片（能用:{howlong2use}天）\n--------------------------\n'
    # message += '--------------------------'
    return message
    # print(message)
