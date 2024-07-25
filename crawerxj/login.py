import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pytesseract
from PIL import Image
import json

# 全局变量保存所有cookie
all_cookies = {}

def update_cookies(new_cookies):
    # print("新的cookie: ", new_cookies)
    global all_cookies
    for cookie in new_cookies:
        if isinstance(cookie, dict):
            all_cookies[cookie['name']] = cookie['value']
        elif isinstance(cookie, list):
            for sub_cookie in cookie:
                all_cookies[sub_cookie['name']] = sub_cookie['value']
        else:
            all_cookies.update(new_cookies)

# 设置ChromeDriver的路径
driver_path = 'C:\\Program Files\\Google\\Chrome\\Application\\chromedriver.exe'
service = Service(executable_path=driver_path)

# 设置Chrome选项为无头模式
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--disable-gpu')

# 创建WebDriver对象
driver = webdriver.Chrome(service=service, options=options)

# 访问指定的URL
driver.get("https://www.tiangong.edu.cn/main.htm")

# 等待页面加载，可选，视网站加载速度而定
WebDriverWait(driver, 10).until(
    lambda driver: driver.execute_script("return document.readyState;") == "complete"
)

# 获取当前页面的所有cookies
new_cookies = driver.get_cookies()
update_cookies(new_cookies)  # 使用你的自定义函数来更新全局cookie存储

# 打开登录页面
driver.get('http://pt-tiangong-edu-cn-s.vpn.tiangong.edu.cn:8118/zfca/login')

# 等待JavaScript变量加载并获取公钥
WebDriverWait(driver, 10).until(
    lambda driver: driver.execute_script(
        "return typeof encrtpt_modulus !== 'undefined' && typeof public_exponent !== 'undefined';")
)
modulus = driver.execute_script("return encrtpt_modulus;")
exponent = driver.execute_script("return public_exponent;")
print("Modulus:", modulus)
print("Exponent:", exponent)

def get_captcha_code(driver):
    # 获取验证码图片并显示给用户
    captcha_element = driver.find_element(By.ID, 'captchaimg')
    captcha_image_path = './captcha.png'
    captcha_element.screenshot(captcha_image_path)

    # 使用pytesseract自动识别验证码
    captcha_image = Image.open(captcha_image_path)
    captcha_code = pytesseract.image_to_string(captcha_image, config='--psm 8').strip()
    print("自动识别的验证码：", captcha_code)
    return captcha_code


def attempt_login(session, driver, login_data, cookie_dict):
    login_page_url = 'http://pt-tiangong-edu-cn-s.vpn.tiangong.edu.cn:8118/zfca/login'
    login_response = session.post(login_page_url, data=login_data, cookies=cookie_dict, allow_redirects=False)

    # 更新cookies
    cookies = session.cookies.get_dict()
    update_cookies(cookies)

    return login_response

cookie_dict = {}

attempts = 5  # 尝试登录次数
for attempt in range(attempts):
    captcha_code = get_captcha_code(driver)

    # 获取表单隐藏字段
    lt_value = driver.find_element(By.NAME, 'lt').get_attribute('value')

    # 执行JavaScript进行加密
    username = '2210910310'
    password = 'tjgd03602X'
    encrypted_password = driver.execute_script("""
        var rsa = new RSAUtils.getKeyPair('{}', '', '{}');
        var encrypted = RSAUtils.encryptedString(rsa, '{}'.split("").reverse().join(""));
        return encrypted;
    """.format(exponent, modulus, password))

    # 获取 cookies
    cookies = driver.get_cookies()
    cookie_dict = {cookie['name']: cookie['value'] for cookie in cookies}
    update_cookies(cookies)

    # 登录表单数据
    login_data = {
        'useValidateCode': '1',
        'isremenberme': '0',
        'ip': '',
        'username': username,
        'password': encrypted_password,
        'j_captcha_response': captcha_code,
        'losetime': '30',
        'lt': lt_value,
        '_eventId': 'submit',
        'submit1': ' '
    }

    session = requests.Session()
    login_response = attempt_login(session, driver, login_data, cookie_dict)

    # 检查是否登录成功
    if 'Location' in login_response.headers:
        break
    else:
        # 登录失败，重新尝试
        print(f"Attempt {attempt + 1} failed, retrying...")

# 更新cookies
cookies = session.cookies.get_dict()
update_cookies(cookies)

# 检查是否有重定向
while 'Location' in login_response.headers:
    redirect_url = login_response.headers['Location']
    # print("Redirect URL:", redirect_url)

    # 发送GET请求到重定向的URL
    login_response = session.get(redirect_url, cookies=cookie_dict, allow_redirects=False)

    # 更新cookies
    cookies = session.cookies.get_dict()
    update_cookies(cookies)

# 使用BeautifulSoup解析HTML内容
soup = BeautifulSoup(login_response.text, 'html.parser')

# 提取相关字段
name = soup.find('h5', string=lambda x: x and '姓名' in x).text.split(':')[1].strip()
category = soup.find('h5', string=lambda x: x and '类别' in x).text.split(':')[1].strip()
job_number = soup.find('h5', string=lambda x: x and '工号' in x).text.split(':')[1].strip()
department = soup.find('h5', string=lambda x: x and '院系/部门' in x).text.split(':')[1].strip()

# 格式化输出结果
output = f"""
*****************************
成功登录VPN，被登录者信息如下：
姓名：{name}
类别：{category}
工号：{job_number}
院系/部门：{department}
*****************************
"""

print(output)

# 将HTML内容保存到本地文件
with open('login_response.html', 'w', encoding='gbk') as file:
    file.write(login_response.text)

print(f"{name}信息门户网页已保存到文件 login_response.html")

# 使用 Selenium 访问指定 URL 以获取 cookie
target_url = 'http://pt-tiangong-edu-cn-s.vpn.tiangong.edu.cn:8118/zfca?yhlx=student&login=0122579031373493746&url=main.aspx'
driver.get(target_url)

# 获取所有 cookie
cookies = driver.get_cookies()
update_cookies(cookies)

# 访问指定的URL
driver.get("https://jwxs.tiangong.edu.cn/student/integratedQuery/scoreQuery/allPassingScores/index")

# 等待页面加载
WebDriverWait(driver, 10).until(
    lambda driver: driver.execute_script("return document.readyState;") == "complete"
)

# 获取页面内容
page_source = driver.page_source

# 使用BeautifulSoup解析HTML
soup = BeautifulSoup(page_source, 'lxml')

# 提取包含URL片段的script标签
script_tags = soup.find_all('script', type='text/javascript')

# 查找特定URL片段
url_fragment = None
for script in script_tags:
    if 'var url = "/student/integratedQuery/scoreQuery/' in script.text:
        lines = script.text.split('\n')
        for line in lines:
            if 'var url = "/student/integratedQuery/scoreQuery/' in line:
                url_fragment = line.split('"/student/integratedQuery/scoreQuery/')[1].split('/')[0]
                break

# 输出提取到的字符串
print(f"提取到的查询{name}成绩密钥:", url_fragment)

# 保存 session 到 vpn-config 文件
vpn_config = {
    "domain": {
        "domainList": [],
        "enableDomainShare": 1
    },
    "rule": {
        "blacklist": ["127.0.0.1", "ptcas.tiangong.edu.cn"],
        "whitelist": ["*"]
    },
    "version": "1.4.8",
    "urlMap": [],
    "base": {
        "panDomain": "vpn.tiangong.edu.cn",
        "vpnUrl": "http://vpn.tiangong.edu.cn:8118",
        "scheme": "http",
        "port": "8118"
    },
    "auth": {
        "session": all_cookies
    },
    "blockAds": {
        "enable": True
    },
    "cookie": {
        "autoClean": True
    }
}

# 更新vpn-config文件
if url_fragment:
    vpn_config['base']['score_url_fragment'] = url_fragment

# 将 vpn-config 保存到文件
with open('vpn-config.json', 'w', encoding='utf-8') as vpn_file:
    json.dump(vpn_config, vpn_file, ensure_ascii=False, indent=4)
print(f"{name}的教务处Cookie已保存到VPN配置文件 vpn-config.json")

# 关闭浏览器
driver.quit()