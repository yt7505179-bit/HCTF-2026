# -*- coding: utf-8 -*-
"""生成 cas.db：约 211 名虚拟师生，首个用户为系统管理员（account=admin）。

字段全部为程序生成的假数据（随机种子固定，与系列题同一批"师生"）。
真 flag 由 FLAG 环境变量注入，写入管理员的 description 字段——
/sc/portal 门户页以管理员身份登录后作为「内部公告」展示。
管理员口令为 32 位随机十六进制且不等于 flag，注入绕过是唯一正解。
"""
import os
import random
import sqlite3
import string
from pathlib import Path

BASE = Path(__file__).parent
DATA = BASE / "data"
DATA.mkdir(exist_ok=True)
DB = DATA / "cas.db"

FLAG = os.environ.get("FLAG", "hctf{s1mpl3_sql1_l0g1n_byp4ss}")

SURNAMES = "王李张刘陈杨黄赵周吴徐孙马朱胡郭何高林郑谢罗梁宋唐许韩冯邓曹彭曾肖田董袁潘蒋蔡余杜叶程苏魏吕丁任沈姚卢姜崔钟谭陆汪范金石廖贾夏韦付方白邹孟熊秦邱江尹薛闫段雷侯龙史陶黎贺顾毛郝龚邵万钱严覃武戴莫孔向汤"
GIVEN = [
    "志强", "伟", "明", "磊", "军", "洋", "勇", "艳", "杰", "娟", "涛", "明",
    "超", "秀英", "霞", "平", "刚", "桂英", "文静", "丽", "强", "超", "军",
    "慧", "巧", "淑兰", "静", "敏", "芳", "燕", "婷", "雪", "欣怡", "梓涵",
    "雨轩", "子豪", "宇轩", "浩然", "一诺", "奕辰", "嘉懿", "致远", "天佑",
    "昊天", "思远", "博", "晨曦", "若曦", "芷晴", "语嫣", "佳琪", "睿",
]
ORGS = [
    (1, "计算机学院", "计算机科学与技术"),
    (2, "机械工程学院", "机械设计制造及其自动化"),
    (3, "电气工程学院", "电气工程及其自动化"),
    (4, "经济管理学院", "国际经济与贸易"),
    (5, "语言文学学院", "汉语言文学"),
    (6, "数理学院", "信息与计算科学"),
]
GRADES = ["2022", "2023", "2024", "2025"]
CAMPUSES = ["东校区", "西校区"]


def rand_name(rng):
    return rng.choice(SURNAMES) + rng.choice(GIVEN)


def rand_phone(rng):
    return "1" + rng.choice("3578") + "".join(rng.choice(string.digits) for _ in range(9))


def hexid(rng, n=16):
    return "".join(rng.choice("0123456789abcdef") for _ in range(n))


FIELDS = [
    "userId", "userName", "account", "sex", "orgId", "orgName", "grade",
    "professional", "className", "status",
    "nation", "political", "idCard", "birthday", "nativePlace", "phone",
    "email", "qq", "wechat", "dormitory", "address", "emergencyContact",
    "emergencyPhone", "enrollDate", "enrollType", "studentType", "length",
    "campus", "building", "cardNo", "bankCard", "bankName", "scholarship",
    "loan", "award", "punish", "cet4", "cet6", "computer", "teacher",
    "counselor", "password", "salt", "createTime", "updateTime", "lastLogin",
    "loginCount", "source", "remark", "tag", "version", "deleted", "secretLevel",
    "description",
]


def make_row(rng, uid, name, org, grade, is_admin=False):
    org_id, org_name, prof = org
    acct = "admin" if is_admin else f"{grade}{org_id:02d}{rng.randint(1, 999):03d}"
    row = {
        "userId": str(uid),
        "userName": name,
        "account": acct,
        "sex": rng.choice(["男", "女"]),
        "orgId": org_id if not is_admin else -1,
        "orgName": "系统管理员" if is_admin else org_name,
        "grade": "教职工" if is_admin else grade,
        "professional": "信息中心" if is_admin else prof,
        "className": "-" if is_admin else f"{grade}级{prof[:2]}{rng.randint(1, 6)}班",
        "status": 1,
        "nation": rng.choice(["汉族", "汉族", "汉族", "瑶族", "土家族"]),
        "political": rng.choice(["共青团员", "共青团员", "中共党员", "群众"]),
        "idCard": f"43{rng.randint(10, 99)}0{rng.randint(1970, 2007):04d}{rng.randint(1, 12):02d}{rng.randint(1, 28):02d}{rng.randint(1000, 9999)}{rng.choice(string.digits)}X",
        "birthday": f"{rng.randint(1970, 2007)}-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}",
        "nativePlace": rng.choice(["湖南岳阳", "湖南长沙", "湖南株洲", "广东深圳", "江西南昌", "广西桂林"]),
        "phone": rand_phone(rng),
        "email": f"admin@example.edu.cn" if is_admin else f"stu{acct}@example.edu.cn",
        "qq": str(rng.randint(10000, 999999999)),
        "wechat": f"wx_{hexid(rng, 8)}",
        "dormitory": "-" if is_admin else f"{rng.choice(CAMPUSES[:1])}{rng.randint(1, 30)}栋{rng.randint(100, 699)}",
        "address": rng.choice(["湖南省长沙市麓山南路", "湖南省株洲市天元区", "湖南省长沙市岳麓区"]),
        "emergencyContact": rand_name(rng),
        "emergencyPhone": rand_phone(rng),
        "enrollDate": "2018-03-01" if is_admin else f"{grade}-09-01",
        "enrollType": rng.choice(["普通高考", "普通高考", "专升本", "转专业"]),
        "studentType": "本科生",
        "length": 4,
        "campus": rng.choice(CAMPUSES),
        "building": f"{rng.choice(['一', '二', '三', '四'])}教学楼",
        "cardNo": f"10{acct}",
        "bankCard": f"62{rng.randint(100, 999)}{rng.randint(10 ** 14, 10 ** 15)}",
        "bankName": rng.choice(["中国工商银行", "中国建设银行", "中国银行"]),
        "scholarship": rng.choice(["国家励志奖学金", "校三等奖学金", "-", "-", "-"]),
        "loan": rng.choice(["生源地贷款", "-", "-", "-"]),
        "award": rng.choice(["校三好学生", "院优秀学生干部", "-", "-"]),
        "punish": rng.choice(["-", "-", "-", "-", "警告处分(已解除)"]),
        "cet4": rng.choice(["425", "478", "512", "-", "531"]),
        "cet6": rng.choice(["-", "-", "456", "489"]),
        "computer": rng.choice(["二级C语言", "二级Python", "-", "-"]),
        "teacher": rand_name(rng),
        "counselor": rand_name(rng),
        "password": hexid(rng, 32),
        "salt": hexid(rng, 8),
        "createTime": "2018-03-01 09:00:00" if is_admin else f"{int(grade) - 1}-09-05 10:{rng.randint(10, 59)}:{rng.randint(10, 59)}",
        "updateTime": "2026-08-30 15:20:11",
        "lastLogin": f"2026-09-{rng.randint(1, 14):02d} {rng.randint(8, 22):02d}:{rng.randint(10, 59):02d}:{rng.randint(10, 59):02d}",
        "loginCount": rng.randint(1, 400),
        "source": "迎新系统",
        "remark": "-",
        "tag": "",
        "version": rng.randint(1, 9),
        "deleted": 0,
        "secretLevel": 2,
        # 管理员行内嵌「网络安全宣传周内部公告」＝真 flag（门户页展示）
        "description": (
            f"网络安全宣传周内部口令（仅限管理员查阅，请勿外传）：{FLAG}"
            if is_admin else "-"
        ),
    }
    return row


def main():
    rng = random.Random(20260916)
    rows = [make_row(rng, 1, "系统管理员", ORGS[0], "2022", is_admin=True)]
    uid = 100
    for i in range(210):
        uid += rng.randint(1, 4)
        org = rng.choice(ORGS)
        grade = rng.choice(GRADES)
        rows.append(make_row(rng, uid, rand_name(rng), org, grade))

    if os.path.exists(DB):
        os.remove(DB)
    conn = sqlite3.connect(DB)
    conn.execute(f"CREATE TABLE users ({', '.join(f'{f} TEXT' for f in FIELDS)})")
    conn.executemany(
        f"INSERT INTO users ({', '.join(FIELDS)}) VALUES ({', '.join('?' * len(FIELDS))})",
        [tuple(r[f] for f in FIELDS) for r in rows],
    )
    conn.commit()
    conn.close()
    print(f"seeded {len(rows)} users -> {DB} (admin password: {rows[0]['password']})")


if __name__ == "__main__":
    main()
