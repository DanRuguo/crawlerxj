import requests
import pandas as pd

# 请求头
headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Cookie": "JSESSIONID=aaaB8DsOsyYTeb19m5V_y; JSESSIONID=aaaB8DsOsyYTeb19m5V_y; _gscu_849404863=20413664uxji4619; TWFID=d97fd6ee3b1f54a0; JSESSIONID_-_pt.tiangong.edu.cn=8798EC7F650805AE76DFFE55DF287CB9; student.urpSoft.cn=aaaB8DsOsyYTeb19m5V_y; JSESSIONID=aaaB8DsOsyYTeb19m5V_y; selectionBar=1002002001",
    "Host": "jwxs-tiangong-edu-cn-s.vpn.tiangong.edu.cn:8118",
    "Pragma": "no-cache",
    "Referer": "http://jwxs-tiangong-edu-cn-s.vpn.tiangong.edu.cn:8118/student/courseSelect/thisSemesterCurriculum/index",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
}

# URL
url = "http://jwxs-tiangong-edu-cn-s.vpn.tiangong.edu.cn:8118/student/courseSelect/thisSemesterCurriculum/ajaxStudentSchedule/callback?sf_request_type=ajax"

# 发送GET请求
response = requests.get(url, headers=headers)

# 检查请求是否成功
if response.status_code == 200:
    data = response.json()

    # 解析课程数据
    course_data = []
    for course in data["xkxx"]:
        for key, value in course.items():
            course_info = {
                "course_number": value["id"]["coureNumber"],
                "course_sequence_number": value["id"]["coureSequenceNumber"],
                "course_name": value["courseName"],
                "teacher": value["attendClassTeacher"],
                "course_category": value["courseCategoryName"],
                "course_properties": value["coursePropertiesName"],
                "exam_type": value["examTypeName"],
                "unit": value["unit"],
                "campus": value["timeAndPlaceList"][0]["campusName"] if value["timeAndPlaceList"] else None,
                "class_day": value["timeAndPlaceList"][0]["classDay"] if value["timeAndPlaceList"] else None,
                "class_sessions": value["timeAndPlaceList"][0]["classSessions"] if value["timeAndPlaceList"] else None,
                "classroom": value["timeAndPlaceList"][0]["classroomName"] if value["timeAndPlaceList"] else None,
                "week_description": value["timeAndPlaceList"][0]["weekDescription"] if value[
                    "timeAndPlaceList"] else None,
            }
            course_data.append(course_info)

    # 转换为DataFrame
    df = pd.DataFrame(course_data)

    # 保存为CSV文件
    df.to_csv("course_schedule.csv", index=False, encoding='utf-8-sig')

    print("课程表已保存为course_schedule.csv")
else:
    print("请求失败，状态码:", response.status_code)
