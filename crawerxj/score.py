import requests
import pandas as pd

# 请求头
headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Cookie": "_gscu_849404863=20413664uxji4619; TWFID=f4c00cb5cec9ea48; student.urpSoft.cn=aaalAJqxQWITs-n_n5V_y; JSESSIONID=aaalAJqxQWITs-n_n5V_y; _gscbrs_849404863=1; _gscs_849404863=20444313o73k3b19|pv:1; JSESSIONID_-_pt.tiangong.edu.cn=4DD1A1E2B8EBBF8E6A42BC6CB9BB77A8; selectionBar=1007001001",
    "Host": "jwxs-tiangong-edu-cn-s.vpn.tiangong.edu.cn:8118",
    "Pragma": "no-cache",
    "Referer": "http://jwxs-tiangong-edu-cn-s.vpn.tiangong.edu.cn:8118/student/integratedQuery/scoreQuery/allPassingScores/index",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
}

# URL
url = "http://jwxs-tiangong-edu-cn-s.vpn.tiangong.edu.cn:8118/student/integratedQuery/scoreQuery/Jh667VOx1u/allPassingScores/callback?sf_request_type=ajax"

# 发送GET请求
response = requests.get(url, headers=headers)

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
