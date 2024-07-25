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

def refresh_tokens():
    """ 刷新访问令牌和刷新令牌 """
    refresh_url = "http://wxykt.tiangong.edu.cn/berserker-auth/oauth/token/refresh"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "refresh_token": tokens["refresh_token"],
        "grant_type": "refresh_token"
    }
    response = requests.post(refresh_url, headers=headers, json=payload)
    if response.status_code == 200:
        new_tokens = response.json()
        tokens["access_token"] = new_tokens["access_token"]
        tokens["refresh_token"] = new_tokens.get("refresh_token", tokens["refresh_token"])  # 刷新令牌可能不会每次都更新
        save_tokens(tokens)  # 保存新的token信息
    else:
        print("Failed to refresh token:", response.status_code)

def fetch_user_data():
    """ 从API获取用户数据 """
    url = "http://wxykt.tiangong.edu.cn/berserker-base/user"
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Connection": "keep-alive",
        # "Cookie": "TGC=TGT-fe1da0bafdd14ccd9311097b8a7d8fdc; error_times=0",
        "Host": "wxykt.tiangong.edu.cn",
        "Referer": "http://wxykt.tiangong.edu.cn/campus-card/billing/list?appId=24&loginFrom=app&type=app",
        "Synjones-Auth": f"bearer {tokens['access_token']}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 401:  # 假设401表示令牌过期
        refresh_tokens()
        headers["Synjones-Auth"] = f"bearer {tokens['access_token']}"
        response = requests.get(url, headers=headers)  # 重试请求
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch data:", response.status_code)
        return None

def fetch_card_info():
    """ 从API获取卡片信息 """
    url = "http://wxykt.tiangong.edu.cn/berserker-app/ykt/tsm/queryCard"
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Connection": "keep-alive",
        "Host": "wxykt.tiangong.edu.cn",
        "Referer": "http://wxykt.tiangong.edu.cn/campus-card/billing/list?appId=24&loginFrom=app&type=app",
        "Synjones-Auth": f"bearer {tokens['access_token']}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 401:  # 假设401表示令牌过期
        refresh_tokens()
        headers["Synjones-Auth"] = f"bearer {tokens['access_token']}"
        response = requests.get(url, headers=headers)  # 重试请求
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch card info:", response.status_code)
        return None

def save_to_csv(data, filename):
    """ 将数据保存到CSV文件 """
    if isinstance(data, list):
        # 如果数据是列表，处理多个条目
        fields = data[0].keys() if data else []
    elif isinstance(data, dict):
        # 如果数据是字典，只处理一个条目
        fields = data.keys()
        data = [data]
    else:
        print("Invalid data format")
        return

    with open(filename, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data)

# 主逻辑
user_data_response = fetch_user_data()
if user_data_response and user_data_response.get('success'):
    save_to_csv(user_data_response['data'], 'user_data.csv')
    print("User data successfully saved.")
else:
    print("No user data to save or fetch failed.")

card_info_response = fetch_card_info()
if card_info_response and card_info_response.get('success'):
    save_to_csv(card_info_response['data']['card'], 'cardInfo.csv')
    print("Card info successfully saved.")
else:
    print("No card info to save or fetch failed.")
