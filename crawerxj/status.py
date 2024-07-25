import requests
from bs4 import BeautifulSoup
import csv
import json

# 读取vpn-config文件
with open('vpn-config.json', 'r', encoding='utf-8') as file:
    vpn_config = json.load(file)

# 从vpn-config获取指定的cookies
specified_cookies = {
    "_gscs_849404863": vpn_config['auth']['session'].get("_gscs_849404863", ""),
    "_gscbrs_849404863": vpn_config['auth']['session'].get("_gscbrs_849404863", ""),
    "_gscu_849404863": vpn_config['auth']['session'].get("_gscu_849404863", ""),
    "JSESSIONID": vpn_config['auth']['session'].get("JSESSIONID", ""),
    "student.urpSoft.cn": vpn_config['auth']['session'].get("student.urpSoft.cn", "")
}

# 将cookies转换为请求头格式
cookie_header = "; ".join([f"{cookie_name}={cookie_value}" for cookie_name, cookie_value in specified_cookies.items() if cookie_value])

# 定义请求头
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br, zstd",  # 更新Accept-Encoding，添加br和zstd
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Cookie": cookie_header,
    "Host": "jwxs.tiangong.edu.cn",  # 更新Host以匹配目标服务器
    "Pragma": "no-cache",
    "Referer": "https://jwxs.tiangong.edu.cn/index",  # 更新Referer以匹配实际的前一个页面
    "Sec-Ch-Ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
}

# 目标URL
url = "https://jwxs.tiangong.edu.cn/student/rollManagement/rollInfo/index"

# 发送GET请求
response = requests.get(url, headers=headers)

# 检查请求是否成功
if response.status_code == 200:
    # 解析HTML内容
    soup = BeautifulSoup(response.text, 'html.parser')

    # 查找学籍信息部分
    profile_info_rows = soup.select('.profile-user-info.profile-user-info-striped .profile-info-row')

    # 存储提取的信息
    student_info = {}

    for row in profile_info_rows:
        key_elements = row.select('.profile-info-name')
        value_elements = row.select('.profile-info-value')

        for key_element, value_element in zip(key_elements, value_elements):
            key = key_element.text.strip()
            value = value_element.text.strip()

            # 处理隐藏内容，假设隐藏内容包含在onclick属性中
            onclick_content = value_element.get('onclick')
            if onclick_content:
                # 提取隐藏内容，假设隐藏内容在单引号内
                hidden_content = onclick_content.split("'")[1]
                value = hidden_content

            student_info[key] = value

    # 打印提取的信息
    for key, value in student_info.items():
        print(f"{key}: {value}")

    # 将信息保存到CSV文件
    csv_filename = 'student_info.csv'
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Key', 'Value'])  # 写入表头
        for key, value in student_info.items():
            writer.writerow([key, value])

    print(f"信息已保存到文件: {csv_filename}")
else:
    print(f"请求失败，状态码: {response.status_code}")
