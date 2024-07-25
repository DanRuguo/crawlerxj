import requests
import pandas as pd
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

# 请求头
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Cookie": cookie_header,
    "Host": "jwxs.tiangong.edu.cn",
    "Pragma": "no-cache",
    "Referer": "https://jwxs.tiangong.edu.cn/student/integratedQuery/scoreQuery/allPassingScores/index",
    "Sec-Ch-Ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Requested-With": "XMLHttpRequest"
}

# 构建请求URL
score_url_fragment = vpn_config['base'].get('score_url_fragment', '')
callback_url = f"https://jwxs.tiangong.edu.cn/student/integratedQuery/scoreQuery/{score_url_fragment}/allPassingScores/callback"

# 发送GET请求
response = requests.get(callback_url, headers=headers)

# 检查请求是否成功
if response.status_code == 200:
    data = response.json()

    # 解析成绩数据
    score_data = []
    for year in data["lnList"]:
        for score in year["cjList"]:
            score_info = {
                "academic_year": score["academicYearCode"],
                "term": score["termName"],
                "course_number": score["id"]["courseNumber"],
                "course_sequence_number": score["id"]["coureSequenceNumber"],
                "course_name": score["courseName"],
                "credit": score["credit"],
                "course_score": score["courseScore"],
                "grade_point": score["gradePointScore"],
                "grade_name": score["gradeName"],
                "exam_time": score["examTime"],
                "plan_name": score["planName"],
                "class_no": score["classNo"],
                "entry_status": score["entryStatusCode"],
                "study_mode": score["studyModeCode"],
                "operator": score["operator"],
                "operating_time": score["operatingTime"]
            }
            score_data.append(score_info)

    # 转换为DataFrame
    df = pd.DataFrame(score_data)

    # 保存为CSV文件
    df.to_csv("student_scores.csv", index=False, encoding='utf-8-sig')

    print("成绩表已保存为student_scores.csv")
else:
    print("请求失败，状态码:", response.status_code)
