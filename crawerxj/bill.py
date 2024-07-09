import requests
from bs4 import BeautifulSoup

# 设置请求头，模拟浏览器行为
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Host': '172-31-133-126.vpn.tiangong.edu.cn:8118',
    'Pragma': 'no-cache',
    'Referer': 'http://172-31-133-126.vpn.tiangong.edu.cn:8118/dlpt/Newindex.aspx',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'Cookie': '_gscu_849404863=20413664uxji4619; TWFID=d97fd6ee3b1f54a0; JSESSIONID_-_pt.tiangong.edu.cn=E9792286397B534B9A6B2C8FF6BD08A0; security_session_verify=33215a2bb1240ac81423ca25860b7cb6; ASP.NET_SessionId=a520jx5dmb5tfekmm102o4zh; yhmc=%e8%96%9b%e4%bf%8a; kmjc=422222; switch=0; PageSize=20; isHomeYeZeroHide=True; Ygbh=5QIWBj3fiHo8nm0ecdTZJQ%3d%3d; lxdh=khAMyG6iKScRpS8aH7uOfQ%3d%3d'
}

# 发起GET请求
url = "http://172-31-133-126.vpn.tiangong.edu.cn:8118/cx6/Views/Jgcwxx/Welcome.aspx"
response = requests.get(url, headers=headers)
response.encoding = 'utf-8'

# 解析HTML内容
soup = BeautifulSoup(response.text, 'html.parser')

# 抓取身份信息
student_info = {}
student_info['学号'] = soup.find('span', id='ctl00_ContentPlaceHolder1_LBL_Num').text.strip()
student_info['姓名'] = soup.find('span', id='ctl00_ContentPlaceHolder1_LBL_Name').text.strip()
student_info['入学年'] = soup.find('span', id='ctl00_ContentPlaceHolder1_LBL_RYear').text.strip()
student_info['离校年'] = soup.find('span', id='ctl00_ContentPlaceHolder1_LBL_Lyear').text.strip()
student_info['学业状态'] = soup.find('span', id='ctl00_ContentPlaceHolder1_LBL_Xyzt').text.strip()
student_info['部门'] = soup.find('span', id='ctl00_ContentPlaceHolder1_LBL_Bm').text.strip()
student_info['专业'] = soup.find('span', id='ctl00_ContentPlaceHolder1_LBL_Zy').text.strip()
student_info['班级'] = soup.find('span', id='ctl00_ContentPlaceHolder1_LBL_Bj').text.strip()
student_info['银行账号'] = soup.find('span', id='ctl00_ContentPlaceHolder1_LBL_yhzh').text.strip()

# 打印身份信息
print("身份信息：")
for key, value in student_info.items():
    print(f"{key}: {value}")

# 抓取转账信息
transfer_info = []
rows = soup.select('#ctl00_ContentPlaceHolder1_TabContainer_zyf_TabPanel7_GV_zyf tr.row, #ctl00_ContentPlaceHolder1_TabContainer_zyf_TabPanel7_GV_zyf tr.row+tr.row')
for row in rows:
    cells = row.find_all('td')
    transfer_record = {
        '年': cells[0].text.strip(),
        '月': cells[1].text.strip(),
        '流水号': cells[2].text.strip(),
        '银行账号': cells[3].text.strip(),
        '发放项目': cells[4].text.strip(),
        '摘要': cells[5].text.strip(),
        '金额': cells[6].text.strip(),
        '税率': cells[7].text.strip(),
        '税额': cells[8].text.strip(),
        '实发金额': cells[9].text.strip(),
        '录入日期': cells[10].text.strip(),
        '凭证日期': cells[11].text.strip(),
        '凭证编号': cells[12].text.strip(),
        '凭证内码': cells[13].text.strip(),
        '发放经费部门': cells[14].text.strip(),
        '经费项目编号': cells[15].text.strip(),
        '经费项目名称': cells[16].text.strip()
    }
    transfer_info.append(transfer_record)

# 打印转账信息
print("\n转账信息：")
for record in transfer_info:
    print(record)

# 抓取缴费情况
payment_info = []
rows = soup.select('#ctl00_ContentPlaceHolder1_TabContainer_jf_TabPanel1_GV_Sf tr.row, #ctl00_ContentPlaceHolder1_TabContainer_jf_TabPanel1_GV_Sf tr.row+tr.row')
for row in rows:
    cells = row.find_all('td')
    payment_record = {
        '收费年度': cells[0].text.strip(),
        '收费项目': cells[1].text.strip(),
        '应收金额': cells[2].text.strip(),
        '实收金额': cells[3].text.strip(),
        '退费金额': cells[4].text.strip(),
        '减免金额': cells[5].text.strip(),
        '欠费金额': cells[6].text.strip()
    }
    payment_info.append(payment_record)

# 打印缴费情况
print("\n缴费情况：")
for record in payment_info:
    print(record)

# 将信息保存到txt文件
with open("bill_info.txt", "w", encoding='utf-8') as file:
    file.write("身份信息：\n")
    for key, value in student_info.items():
        file.write(f"{key}: {value}\n")

    file.write("\n转账信息：\n")
    for record in transfer_info:
        file.write(str(record) + "\n")

    file.write("\n缴费情况：\n")
    for record in payment_info:
        file.write(str(record) + "\n")

print("信息已保存到 bill_info.txt 文件中。")