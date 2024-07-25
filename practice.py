import requests
from bs4 import BeautifulSoup
import hashlib
import random
import ddddocr
import onnxruntime
import os

onnxruntime.set_default_logger_severity(3)

# 用户名和密码
username = "2210910310"
password = "03602XTgu"

# 会话文件路径
session_file = "session_cookies.txt"

# MD5加密函数
def md5_encrypt(text):
    return hashlib.md5(text.encode('utf-8')).hexdigest()

# 创建会话对象
session = requests.Session()

# 从文件中读取会话信息
if os.path.exists(session_file):
    with open(session_file, "r") as file:
        cookies = file.read().strip()
        if cookies:
            for cookie in cookies.split("; "):
                key, value = cookie.split("=", 1)
                session.cookies.set(key, value)

# 获取登录页面
login_url = "http://bsgl.tiangong.edu.cn/aexp/"
response = session.get(login_url)

# 解析登录页面
soup = BeautifulSoup(response.content, 'html.parser')

# 获取隐藏参数
hidden_params = {}
for hidden in soup.find_all("input", type="hidden"):
    hidden_params[hidden["name"]] = hidden["value"]

# 获取验证码图片地址
vcode_img_url = "http://bsgl.tiangong.edu.cn/aexp/ValidateImage?t=" + str(random.random())

# 获取验证码图片
vcode_response = session.get(vcode_img_url)
vcode_image = vcode_response.content

# 使用 ddddocr 库识别验证码
ocr = ddddocr.DdddOcr(show_ad=False)
vcode = ocr.classification(vcode_image)

# 加密用户名和密码
encrypted_username = md5_encrypt(username)
encrypted_password = md5_encrypt(password)

# 准备提交的数据
payload = {
    'username': encrypted_username,
    'password': encrypted_password,
    'validateCode': vcode,
    'juese': '2',  # 选择角色：教师(1)、学生(2)、专家(3)
    'code': 'dologin',
    'productCode': 'aexp'
}

# 添加隐藏参数到 payload
payload.update(hidden_params)

# 打印加密后的用户名和密码
# print(payload)

# 获取初始cookie
initial_cookies = session.cookies.get_dict()

# 设置请求头
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Content-Length': str(len(payload)),
    'Content-Type': 'application/x-www-form-urlencoded',
    'Cookie': '; '.join([f"{key}={value}" for key, value in initial_cookies.items()]),
    'Host': 'bsgl.tiangong.edu.cn',
    'Origin': 'http://bsgl.tiangong.edu.cn',
    'Pragma': 'no-cache',
    'Referer': 'http://bsgl.tiangong.edu.cn/aexp/',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
}

# 提交登录表单
login_action_url = "http://bsgl.tiangong.edu.cn/aexp/whichLogin.jsp"
login_response = session.post(login_action_url, data=payload, headers=headers)

# 显示重定向后的网址
for history in login_response.history:
    print("重定向网址:", history.url)
print("最终网址:", login_response.url)

# 记录最终的Cookies
final_cookies = session.cookies.get_dict()
print("最终Cookies:", final_cookies)

# 保存最终的Cookies到文件
with open(session_file, "w") as file:
    cookies_str = "; ".join([f"{key}={value}" for key, value in final_cookies.items()])
    file.write(cookies_str)

# 添加 menuhref=/aexp/ 到 cookies
session.cookies.set('menuhref', '/aexp/')
session.cookies.set('_gscu_849404863', '20413664uxji4619')

# 合并 cookies
combined_cookies = session.cookies.get_dict()

# 定义新请求头
_headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Cookie': '; '.join([f"{key}={value}" for key, value in combined_cookies.items()]),
    'Host': 'bsgl.tiangong.edu.cn',
    'Pragma': 'no-cache',
    'Referer': 'http://bsgl.tiangong.edu.cn/aexp/',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
}


# 访问 stuTop.jsp 页面
stu_top_url = "http://bsgl.tiangong.edu.cn/aexp/stuTop.jsp"
stu_top_response = session.get(stu_top_url, headers=_headers)

# 解析 stuTop.jsp 页面内容
soup = BeautifulSoup(stu_top_response.content, 'html.parser')

# 获取登录姓名
login_name = soup.find("span", style="font-weight:bold;").get_text(strip=True)

# 获取教学周信息
teaching_week = soup.find("div", class_="topmain").get_text(strip=True)

# 输出登录姓名和教学周信息
print("登录姓名:", login_name)
print("教学周信息:", teaching_week)

# 要访问的 URLs
urls = {
    "practice": "http://bsgl.tiangong.edu.cn/practice/practiceAction/tasks.action",
    "race": "http://bsgl.tiangong.edu.cn/race/raceAction/myRace_queryMyRace.action",
    "srtp": "http://bsgl.tiangong.edu.cn/srtp/srtpAction/toJoinProject.action",
    "credit": "http://bsgl.tiangong.edu.cn/StuExpbook/practiceext/mycredit.jsp"
}

# 先访问 srtp 前的登录页面
srtp_login_url = "http://bsgl.tiangong.edu.cn/srtp/srtpAction/index.action"
srtp_login_response = session.get(srtp_login_url, headers=_headers)

# 先访问 credit 前的登录页面
credit_login_url = f"http://bsgl.tiangong.edu.cn/StuExpbook/index/login1.jsp?no={username}"
credit_login_response = session.get(credit_login_url, headers=_headers)

# 访问并保存响应内容到 HTML 文件
for key, url in urls.items():
    # 特定页面的 Referer
    if key == "credit":
        _headers['Referer'] = 'http://bsgl.tiangong.edu.cn/StuExpbook/practiceext/creditTab.jsp'
    else:
        _headers['Referer'] = 'http://bsgl.tiangong.edu.cn/aexp/stuLeft.jsp'

    response = session.get(url, headers=_headers)
    with open(f".//html//{key}.html", "w", encoding="utf-8") as file:
        file.write(response.text)

print("访问并保存响应内容完成。")

# 定义提取有用信息的函数
def extract_info(filename):
    with open(filename, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")
        if "credit" in filename:
            title = "我的成绩学分"
            headers = ["项目名", "类别", "考核标准", "责任教师", "成绩", "学分"]
            rows = soup.select("table tr")[1:]  # 跳过标题行
            data = [[td.get_text(strip=True) for td in row.find_all("td")] for row in rows]
        elif "practice" in filename:
            title = "实习任务"
            headers = ["所属课程", "课程类型", "学时", "学分", "开课单位", "负责教师", "是否允许自主", "操作"]
            data = []
            year_terms = [option['value'] for option in soup.select("#yearterm option")]
            for year_term in year_terms:
                page_num = 1
                while True:
                    url = f"http://bsgl.tiangong.edu.cn/practice/practiceAction/tasks.action?page.pageNum={page_num}&yearterm={year_term}"
                    response = session.get(url, headers=_headers)
                    soup = BeautifulSoup(response.text, "html.parser")
                    rows = soup.select("table tr")[1:]  # 跳过标题行
                    if not rows:
                        break
                    data.extend([[td.get_text(strip=True) for td in row.find_all("td")] for row in rows])
                    page_info = soup.select_one("#myPage p").get_text(strip=True)
                    current_page, total_pages = list(map(int, page_info.split(" / ")[0].replace("第", "").replace("页", "").strip().split())), int(page_info.split("共")[1].split("页")[0])
                    if current_page[0] >= total_pages:
                        break
                    page_num += 1
        elif "race" in filename:
            title = "我参与的竞赛"
            headers = ["竞赛名称", "学年", "团队/个人名", "状态", "审核意见", "操作"]
            rows = soup.select("table tr")[1:]  # 跳过标题行
            data = [[td.get_text(strip=True) for td in row.find_all("td")] for row in rows]
        elif "srtp" in filename:
            title = "我参与的项目"
            headers = ["项目名称", "主持人", "批准经费(元)", "立项时间", "项目阶段", "项目状态", "当前进度", "操作"]
            rows = soup.select("table tr")[1:]  # 跳过标题行
            data = [[td.get_text(strip=True) for td in row.find_all("td")] for row in rows]
        return title, headers, data

# 提取并保存信息
with open("practice_info.txt", "w", encoding="utf-8") as file:
    file.write(f"登录姓名: {login_name}\n")
    file.write(f"教学周信息: {teaching_week}\n")
    file.write("\n")
    for key in urls.keys():
        filename = f"./html/{key}.html"
        title, headers, data = extract_info(filename)
        file.write(f"{title}\n")
        file.write("\t".join(headers) + "\n")
        for row in data:
            file.write("\t".join(row) + "\n")
        file.write("\n")

print(f"{login_name}的实践和竞赛信息提取完成。")