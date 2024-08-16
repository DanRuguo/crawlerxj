import requests
from bs4 import BeautifulSoup
import ddddocr
import onnxruntime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# 降低 onnxruntime 日志级别
onnxruntime.set_default_logger_severity(3)

# 基本URL
base_url = "https://pay.tiangong.edu.cn"

# 创建一个session对象，来保持登录状态
session = requests.Session()

# 设置一个占位符Cookie，防止Cookie字段为空
session.cookies.set('_gscu_849404863', '22846444e6zkfo17')

# 获取登录页面，以提取必要的hidden字段
login_page_url = f"{base_url}/login.aspx?local=zh-cn"
login_page_response = session.get(login_page_url)

# 使用BeautifulSoup解析页面内容
soup = BeautifulSoup(login_page_response.text, 'html.parser')

# 提取__VIEWSTATE、__EVENTVALIDATION和__VIEWSTATEGENERATOR
viewstate = soup.find('input', {'name': '__VIEWSTATE'}).get('value')
eventvalidation = soup.find('input', {'name': '__EVENTVALIDATION'}).get('value')
viewstate_generator = soup.find('input', {'name': '__VIEWSTATEGENERATOR'}).get('value')

# 下载验证码图片
captcha_url = f"{base_url}/validate.aspx"
captcha_response = session.get(captcha_url)
vcode_image = captcha_response.content

# 使用ddddocr库识别验证码
ocr = ddddocr.DdddOcr(show_ad=False)
vcode = ocr.classification(vcode_image)

print(f"识别出的验证码为: {vcode}")

# 登录时需要发送的数据
payload = {
    '__VIEWSTATE': viewstate,
    '__VIEWSTATEGENERATOR': viewstate_generator,
    '__EVENTVALIDATION': eventvalidation,
    'txt_yhm': '34132220031203602X',  # 证件号
    'txt_pwd': '薛俊',                # 姓名
    'txt_yzm': vcode,                 # 识别出的验证码
    'ImageButton1.x': '0',            # 这些字段是ImageButton点击的位置
    'ImageButton1.y': '0'
}

# 登录URL
login_url = f"{base_url}/login.aspx?local=zh-cn"

# 模拟登录
login_response = session.post(login_url, data=payload)

# 捕获跳转后的网页内容
final_page = login_response.text

# 使用BeautifulSoup解析页面内容
soup = BeautifulSoup(final_page, 'html.parser')

# 查找包含用户信息的元素
user_info_element = soup.find('span', id='l_xh')

# 提取并格式化输出用户信息
if user_info_element:
    user_info_text = user_info_element.get_text(separator=' ').strip()
    print("用户信息提取成功：")
    print(user_info_text)
    # 打印登录后的Cookies
    cookies = session.cookies.get_dict()
    print("登录后的Cookies:")
    for cookie_name, cookie_value in cookies.items():
        print(f"{cookie_name}: {cookie_value}")
else:
    print("未能找到指定的用户信息。")

headers = {
    'accept': '*/*',
    'accept-encoding': 'gzip, deflate, br, zstd',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'cache-control': 'no-cache',
    'connection': 'keep-alive',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'cookie': '; '.join([f'{name}={value}' for name, value in cookies.items()]),
    'host': 'pay.tiangong.edu.cn',
    'origin': 'https://pay.tiangong.edu.cn',
    'pragma': 'no-cache',
    'referer': 'https://pay.tiangong.edu.cn/Modules/ddcx/jyjl.aspx',
    'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
    'x-microsoftajax': 'Delta=true',
    'x-requested-with': 'XMLHttpRequest'
}

# 访问交易记录页面的URL
transaction_url = f"{base_url}/Modules/ddcx/jyjl.aspx"

# 获取页面以提取__VIEWSTATE和__EVENTVALIDATION
response = session.get(transaction_url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

# 提取__VIEWSTATE和__EVENTVALIDATION
viewstate = soup.find('input', {'name': '__VIEWSTATE'}).get('value')
eventvalidation = soup.find('input', {'name': '__EVENTVALIDATION'}).get('value')
viewstate_generator = soup.find('input', {'name': '__VIEWSTATEGENERATOR'}).get('value')

# 准备POST请求的载荷
payload = {
    'ScriptManager1': 'UpdatePanel1|PageSpliter1$drop_ps',
    'txt_ddrq': '',
    'txt_ddh': '',
    'drop_ddlx': '',
    'drop_zfzt': '',
    'PageSpliter1$PageIndex': '1',
    'PageSpliter1$drop_ps': '50',  # 显示50条记录
    '__EVENTTARGET': 'PageSpliter1$drop_ps',
    '__EVENTARGUMENT': '',
    '__LASTFOCUS': '',
    '__VIEWSTATE': viewstate,
    '__VIEWSTATEGENERATOR': viewstate_generator,
    '__EVENTVALIDATION': eventvalidation,
    '__ASYNCPOST': 'true'
}

# 发送POST请求
response = session.post(transaction_url, data=payload, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

# 提取交易记录信息
transactions = []
table = soup.find('table', {'id': 'dgData'})
if table:
    rows = table.find_all('tr')[1:]  # 跳过标题行
    for row in rows:
        cols = row.find_all('td')
        if len(cols) >= 9:  # 确保所有预期列都存在
            transaction = {
                '银行订单': cols[0].text.strip(),
                '订单日期': cols[1].text.strip(),
                '订单时间': cols[2].text.strip(),
                '交易银行': cols[3].text.strip(),
                '订单金额': cols[4].text.strip(),
                '手续费': cols[5].text.strip(),
                '交易金额': cols[6].text.strip(),
                '退费金额': cols[7].text.strip(),
                '支付成功': cols[8].text.strip()
            }
            transactions.append(transaction)

# 打印交易记录
print("学校缴费记录:")
for transaction in transactions:
    print(transaction)

# 访问报名信息查看页面的URL
bm_info_url = f"{base_url}/Modules/bm/bmxxck.aspx"

# 获取页面
response = session.get(bm_info_url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

# 提取报名信息记录
bm_records = []
table = soup.find('table', {'id': 'dgData'})
if table:
    rows = table.find_all('tr')[1:]  # 跳过标题行
    for row in rows:
        cols = row.find_all('td')
        if len(cols) >= 10:  # 确保所有预期列都存在
            record = {
                '收费区间': cols[0].text.strip(),
                '收费批次': cols[1].text.strip(),
                '已报名项目名称': cols[2].text.strip(),
                '收费内容': cols[3].text.strip(),
                '收费起始时间': cols[4].text.strip(),
                '收费截止时间': cols[5].text.strip(),
                '收费标准': cols[6].text.strip(),
                '已交金额': cols[7].text.strip(),
                '是否支付成功': cols[8].text.strip(),
                '操作': cols[9].text.strip()
            }
            bm_records.append(record)

# 打印报名信息记录
print("报名信息记录:")
for record in bm_records:
    print(record)

# 设置ChromeDriver选项
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")  # 如果不需要打开浏览器窗口，可以使用headless模式
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")

# 通过Session和Cookies初始化Selenium WebDriver
for cookie_name, cookie_value in cookies.items():
    chrome_options.add_argument(f'cookie={cookie_name}={cookie_value}')

# 设置ChromeDriver的路径
driver_path = 'C:\\Program Files\\Google\\Chrome\\Application\\chromedriver.exe'
service = Service(executable_path=driver_path)

# 启动WebDriver
driver = webdriver.Chrome(service=service, options=chrome_options)

# 导航到一个与Cookie域名匹配的页面
driver.get(base_url)

# 设置Cookies
for cookie_name, cookie_value in cookies.items():
    driver.add_cookie({'name': cookie_name, 'value': cookie_value})

# 访问报名信息查看页面的URL
bm_info_url = f"{base_url}/Modules/bm/bmxxck.aspx"

# 在浏览器中打开目标页面
driver.get(bm_info_url)

# 无限循环
while True:
    driver.refresh()
    try:
        # 执行JavaScript操作或点击操作来触发页面内容加载
        driver.execute_script("__doPostBack('dgData$ctl03$ctl00','')")

        # 如果页面是在新标签页打开的，可以使用以下代码切换到新标签页
        if len(driver.window_handles) > 1:
            driver.switch_to.window(driver.window_handles[-1])  # 切换到最后一个标签页
        else:
            driver.switch_to.window(driver.window_handles[0])  # 切换到原始标签页

        # 获取当前页面URL
        current_url = driver.current_url
        print(f"当前页面URL: {current_url}")

        # 等待新内容加载完成
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'ContentPlaceHolder1_l_xm'))
        )

        # 提取信息
        info = {
            "真实姓名": driver.find_element(By.ID, "ContentPlaceHolder1_l_xm").text,
            "性别": driver.find_element(By.ID, "ContentPlaceHolder1_l_xb").text,
            "身份证号": driver.find_element(By.ID, "ContentPlaceHolder1_l_sfzh").text,
            "手机": driver.find_element(By.ID, "ContentPlaceHolder1_l_sj").text,
            "收费部门": driver.find_element(By.ID, "ContentPlaceHolder1_lb_sfbm").text,
            "项目名称": driver.find_element(By.ID, "ContentPlaceHolder1_lb_xmmc").text,
            "收费时间": driver.find_element(By.ID, "ContentPlaceHolder1_l_jfqzsj").text,
            "收费金额": driver.find_element(By.ID, "ContentPlaceHolder1_l_sfbz").text,
            "已缴金额": driver.find_element(By.ID, "ContentPlaceHolder1_l_jfje").text
        }

        # 打印提取到的信息
        print("报名详细信息:")
        for key, value in info.items():
            print(f"{key}: {value}")

        # 信息提取成功，退出循环
        break

    except Exception as e:
        print(f"出现错误: {e}")
        print(f"当前页面URL: {driver.current_url}")
        print(f"页面源代码: {driver.page_source[:500]}")  # 打印前500字符

    # 等待用户在浏览器中手动操作后继续循环提取
    time.sleep(5)  # 每5秒检查一次页面内容

# 关闭WebDriver
# driver.quit()
