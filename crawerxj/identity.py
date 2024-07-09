import requests
import csv

# 全局变量，存储薛俊当前账户的访问令牌和刷新令牌
tokens = {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzbm8iOiIyMjEwOTEwMzEwIiwidXNlcl9uYW1lIjoiMjIxMDkxMDMxMCIsInNjb3BlIjpbImFsbCJdLCJsb2dpbnR5cGUiOiJzbm9LZXlib2FyZCIsIm5hbWUiOiLolpvkv4oiLCJpZCI6NDM3MTIsImV4cCI6MTcyNjQ1MTk3NSwibG9naW5Gcm9tIjoiYXBwIiwidXVpZCI6ImIzMTZlNTI2NTcxNTIyOGUzNzE5ZGM1ZGMwOGZhZGI3IiwianRpIjoiYTIzNDBjNTYtZjFiMy00OWMxLTlmZGUtZmIyNmM0NjQ2ZTFjIiwiY2xpZW50X2lkIjoibW9iaWxlX3NlcnZpY2VfcGxhdGZvcm0ifQ.6KmYnidpbW_qyTuqD9ZNzK7hzefsry7hwd3aA33BZvw",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzbm8iOiIyMjEwOTEwMzEwIiwidXNlcl9uYW1lIjoiMjIxMDkxMDMxMCIsInNjb3BlIjpbImFsbCJdLCJsb2dpbnR5cGUiOiJzbm9LZXlib2FyZCIsImF0aSI6ImEyMzQwYzU2LWYxYjMtNDljMS05ZmRlLWZiMjZjNDY0NmUxYyIsIm5hbWUiOiLolpvkv4oiLCJpZCI6NDM3MTIsImV4cCI6MTcyMTAwODc3NSwibG9naW5Gcm9tIjoiYXBwIiwidXVpZCI6ImIzMTZlNTI2NTcxNTIyOGUzNzE5ZGM1ZGMwOGZhZGI3IiwianRpIjoiNjk3YTc1ZjAtMjkzYy00MDU2LTk2NjMtZGQyMmE5YTIxMGQ0IiwiY2xpZW50X2lkIjoibW9iaWxlX3NlcnZpY2VfcGxhdGZvcm0ifQ.IolgdMa_olChtd42kaxffxsNQuufos78S-P0nluhHCc"
}

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
        headers["Authorization"] = f"Bearer {tokens['access_token']}"
        response = requests.get(url, headers=headers)  # 重试请求
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch data:", response.status_code)
        return None

def save_to_csv(user_data):
    """ 将用户数据保存到CSV文件 """
    fields = user_data.keys()
    with open('user_data.csv', mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        writer.writerow(user_data)

# 主逻辑
user_data_response = fetch_user_data()
if user_data_response and user_data_response['success']:
    save_to_csv(user_data_response['data'])
    print("Data successfully saved.")
else:
    print("No data to save or fetch failed.")
