import requests
import json
from keyboard_mapping import numberKeyboardImage_dict

def get_number_positions(image_data):
    """
    根据图像数据获取数字位置
    :param image_data: 图像数据（base64编码）
    :return: 数字位置字典
    """
    # 从字典中获取对应的数字
    if image_data in numberKeyboardImage_dict:
        number = numberKeyboardImage_dict[image_data]
        return {number: image_data}
    else:
        raise ValueError("图像数据不在字典中")

def map_password_to_keyboard(password, number_mapping):
    mapped_password = ''
    for char in password:
        if char in number_mapping:
            mapped_password += number_mapping[char]
        else:
            raise ValueError(f"密码中的字符 {char} 在映射中找不到")
    return mapped_password

try:
    # 请求获取键盘信息和UUID
    response = requests.get('http://wxykt.tiangong.edu.cn/berserker-secure/keyboard?type=Number&order=1')
    keyboard_info = response.json()
    keyboard_uuid = keyboard_info['data']['uuid']
    number_images = keyboard_info['data']['numberKeyboardImage']
    number_keyboard = keyboard_info['data']['numberKeyboard']

    # 建立字典 textKeyboardImage_dict 来映射 numberKeyboard 和 numberKeyboardImage
    textKeyboardImage_dict = {}
    for i, char in enumerate(number_keyboard):
        textKeyboardImage_dict[char] = number_images[i]

    # 解析虚拟键盘图像
    number_mapping = {}
    for key, image_data in textKeyboardImage_dict.items():
        number_positions = get_number_positions(image_data)
        for num, pos in number_positions.items():
            number_mapping[num] = key

    # 将密码映射到虚拟键盘上的值
    password = '203602'
    mapped_password = map_password_to_keyboard(password, number_mapping)

    # 生成加密后的密码
    encrypted_password = f"keyboard#$#1$1${mapped_password}$1${keyboard_uuid}"
    print(f"Encrypted Password: {encrypted_password}")

finally:
    pass

# 使用获取到的加密密码进行POST请求以拿到token
token_url = "http://wxykt.tiangong.edu.cn/berserker-auth/oauth/token"
data = {
    "username": "2210910310",
    "password": encrypted_password,
    "grant_type": "password",
    "scope": "all",
    "loginFrom": "app",
    "logintype": "sno"
}

headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Authorization": "Basic bW9iaWxlX3NlcnZpY2VfcGxhdGZvcm06bW9iaWxlX3NlcnZpY2VfcGxhdGZvcm1fc2VjcmV0",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Content-Length": "171",
    "Content-Type": "application/x-www-form-urlencoded",
    "Cookie": "_gscu_849404863=20413664uxji4619; TGC=TGT-c4a292d00a7842c79726321ab080255e; error_times=0",
    "Host": "wxykt.tiangong.edu.cn",
    "Origin": "http://wxykt.tiangong.edu.cn",
    "Pragma": "no-cache",
    "Referer": "http://wxykt.tiangong.edu.cn/plat/login",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
}

response = requests.post(token_url, data=data, headers=headers)
token_info = response.json()
print(f"Token Info: {token_info}")

# 将token信息保存到wxykt_token.json文件
with open('wxykt_token.json', 'w', encoding='utf-8') as f:
    json.dump(token_info, f, ensure_ascii=False, indent=4)

print("Token information has been saved to wxykt_token.json")