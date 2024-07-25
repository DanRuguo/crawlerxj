from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import pytesseract
from PIL import Image
import json
import time
import sys
import io
from contextlib import redirect_stdout

# 创建一个虚拟的输出流来捕获输出
f = io.StringIO()

# 导入 ddddocr 库，同时重定向输出到虚拟的输出流
with redirect_stdout(f):
    import ddddocr

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
cookies = driver.get_cookies()

# 使用JavaScript执行获取动态生成的Cookie
dynamic_cookie = driver.execute_script("return document.cookie;")
# 解析动态生成的cookie
for cookie in dynamic_cookie.split(';'):
    name, value = cookie.strip().split('=', 1)
    cookies.append({'name': name, 'value': value})

update_cookies(cookies)

# 打开登录页面
driver.get('http://pt-tiangong-edu-cn-s.vpn.tiangong.edu.cn:8118/zfca/login')

# 获取验证码图片并显示给用户
captcha_element = driver.find_element(By.ID, 'captchaimg')
captcha_image_path = './captcha.png'
captcha_element.screenshot(captcha_image_path)
# print("请查看下载的验证码图片：", captcha_image_path)

# 使用pytesseract自动识别验证码
# captcha_image = Image.open(captcha_image_path)
# captcha_code = pytesseract.image_to_string(captcha_image, config='--psm 8').strip()
# print("自动识别的验证码：", captcha_code)

# 创建ddddocr对象
ocr = ddddocr.DdddOcr()

# 打开图片文件
with open(captcha_image_path, 'rb') as f:
    captcha_image = f.read()

# 识别验证码
captcha_code = ocr.classification(captcha_image)
print("自动识别的验证码：", captcha_code)

# 获取表单隐藏字段
lt_value = driver.find_element(By.NAME, 'lt').get_attribute('value')
print("LT Value:", lt_value)

# 执行JavaScript进行加密
username = '2210910310'
password = 'tjgd03602X'

# 输入登录信息
driver.find_element(By.NAME, 'username').send_keys(username)
driver.find_element(By.NAME, 'password').send_keys(password)
driver.find_element(By.NAME, 'j_captcha_response').send_keys(captcha_code)
driver.find_element(By.NAME, 'submit1').click()

# 访问第一个URL以获取初始cookies
driver.get('http://172-31-133-126.vpn.tiangong.edu.cn:8118/cx6/Error.htm')
WebDriverWait(driver, 10).until(
    lambda d: d.execute_script("return document.readyState") == "complete"
)

# 获取当前页面的所有cookies
cookies = driver.get_cookies()

# 使用JavaScript执行获取动态生成的Cookie
dynamic_cookie = driver.execute_script("return document.cookie;")
# 解析动态生成的cookie
for cookie in dynamic_cookie.split(';'):
    name, value = cookie.strip().split('=', 1)
    cookies.append({'name': name, 'value': value})

update_cookies(cookies)

target_url = 'http://pt-tiangong-edu-cn-s.vpn.tiangong.edu.cn:8118/zfca?yhlx=student&login=0122579031373493732&url=%23'
driver.get(target_url)
WebDriverWait(driver, 10).until(
    lambda d: d.execute_script("return document.readyState") == "complete"
)

# 获取所有 cookie
cookies = driver.get_cookies()

# 使用JavaScript执行获取动态生成的Cookie
dynamic_cookie = driver.execute_script("return document.cookie;")
# 解析动态生成的cookie
for cookie in dynamic_cookie.split(';'):
    name, value = cookie.strip().split('=', 1)
    cookies.append({'name': name, 'value': value})

update_cookies(cookies)

# 访问目标URL
target_url = 'http://172-31-133-126.vpn.tiangong.edu.cn:8118/dlpt/jump.aspx?sysid=wscx'
driver.get(target_url)
WebDriverWait(driver, 10).until(
    lambda d: d.execute_script("return document.readyState") == "complete"
)

# 获取所有 cookie
cookies = driver.get_cookies()

# 使用JavaScript执行获取动态生成的Cookie
dynamic_cookie = driver.execute_script("return document.cookie;")
# 解析动态生成的cookie
for cookie in dynamic_cookie.split(';'):
    name, value = cookie.strip().split('=', 1)
    cookies.append({'name': name, 'value': value})

update_cookies(cookies)

# 打印获取的cookie信息
print("All Cookies:", all_cookies)

# 关闭浏览器
driver.quit()

# 保存session到vpn-config文件
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

# 将vpn-config保存到文件
with open('vpn-config_web.json', 'w', encoding='utf-8') as vpn_file:
    json.dump(vpn_config, vpn_file, ensure_ascii=False, indent=4)
print("VPN配置已保存到本地文件 vpn-config_web.json")
