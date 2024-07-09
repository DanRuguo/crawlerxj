import requests
from bs4 import BeautifulSoup
import csv

# 定义请求头
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Cookie": "JSESSIONID=20413664uxji4619; _gscu_849404863=20413664uxji4619; TWFID=f4c00cb5cec9ea48; student.urpSoft.cn=aaalAJqxQWITs-n_n5V_y; JSESSIONID=aaalAJqxQWITs-n_n5V_y; _gscbrs_849404863=1; _gscs_849404863=20444313o73k3b19|pv:1; JSESSIONID_-_pt.tiangong.edu.cn=4DD1A1E2B8EBBF8E6A42BC6CB9BB77A8; selectionBar=1001001001",
    "Host": "jwxs-tiangong-edu-cn-s.vpn.tiangong.edu.cn:8118",
    "Pragma": "no-cache",
    "Referer": "http://pt-tiangong-edu-cn-90-p-s.vpn.tiangong.edu.cn:8118/",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
}

# 目标URL
url = "http://jwxs-tiangong-edu-cn-s.vpn.tiangong.edu.cn:8118/student/rollManagement/rollInfo/index"

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
