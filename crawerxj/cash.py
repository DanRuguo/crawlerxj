import requests
import csv
import json

# 读取token信息
def load_tokens():
    with open('wxykt_token.json', 'r', encoding='utf-8') as file:
        return json.load(file)

# 保存token信息
def save_tokens(tokens):
    with open('wxykt_token.json', 'w', encoding='utf-8') as file:
        json.dump(tokens, file, ensure_ascii=False, indent=4)

# 全局变量，存储薛俊当前账户的访问令牌和刷新令牌
tokens = load_tokens()

def fetch_data(page_number):
    url = f"http://wxykt.tiangong.edu.cn/berserker-search/search/personal/turnover?size=8&current={page_number}&synAccessSource=app"
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Connection": "keep-alive",
        "Cookie": "TGC=TGT-fe1da0bafdd14ccd9311097b8a7d8fdc; error_times=0",
        "Host": "wxykt.tiangong.edu.cn",
        "Referer": "http://wxykt.tiangong.edu.cn/campus-card/billing/list?appId=24&loginFrom=app&type=app",
        "Synjones-Auth": f"bearer {tokens['access_token']}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()  # 成功获取数据
    elif response.status_code == 401:  # 假设401表示令牌过期
        refresh_tokens()  # 刷新令牌
        headers["Synjones-Auth"] = f"bearer {tokens['access_token']}"
        response = requests.get(url, headers=headers)  # 重试请求
        return response.json() if response.status_code == 200 else None
    return None

def refresh_tokens():
    refresh_url = "http://wxykt.tiangong.edu.cn/berserker-auth/oauth/token/refresh"
    payload = {
        "refresh_token": tokens["refresh_token"],
        "grant_type": "refresh_token"
    }
    response = requests.post(refresh_url, data=payload)
    if response.status_code == 200:
        new_tokens = response.json()
        tokens["access_token"] = new_tokens["access_token"]
        tokens["refresh_token"] = new_tokens.get("refresh_token", tokens["refresh_token"])
        save_tokens(tokens)  # 保存新的token信息

def save_to_csv(data, mode='a'):  # 默认追加模式
    headers = ['fromAccount', 'accType', 'fromJnNumber', 'toAccount', 'posCode', 'operCode', 'jndatetime', 'effectdate',
               'effectdateStr', 'cardBalance', 'ebagamt', 'usedcardnum', 'tranamt', 'ensureAmt', 'feeAmt',
               'consumeType', 'resume', 'bankacc', 'turnoverType', 'icon', 'tranCode', 'typeFrom', 'orderId', 'typeId',
               'jndatetimeStr', 'payName', 'payIcon', 'remark', 'userName', 'labelName', 'labelId',
               'labelRemark', 'locationName']
    with open('transactions.csv', mode=mode, newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if mode == 'w':  # 如果是写模式，则写入头部
            writer.writerow(headers)
        for record in data['data']['records']:
            row = [record.get(header, "") for header in headers]
            writer.writerow(row)

# 主循环，从第一页开始爬取数据
current_page = 1
while True:
    data = fetch_data(current_page)
    if data and data['data']['records']:
        print(f"抓取第{current_page}页数据成功，正在保存...")
        save_to_csv(data, 'a' if current_page != 1 else 'w')  # 如果是第一页，则覆盖写入
        current_page += 1
    else:
        print("没有更多数据，或者抓取失败。")
        break