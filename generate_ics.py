import datetime

lines = [
    "BEGIN:VCALENDAR",
    "VERSION:2.0",
    "PRODID:-//OpenClaw//EN",
    "CALSCALE:GREGORIAN",
    "BEGIN:VTIMEZONE",
    "TZID:Asia/Shanghai",
    "BEGIN:STANDARD",
    "TZOFFSETFROM:+0800",
    "TZOFFSETTO:+0800",
    "TZNAME:CST",
    "DTSTART:19700101T000000",
    "END:STANDARD",
    "END:VTIMEZONE"
]

w1_monday = datetime.date(2026, 3, 2)
uid_counter = 1

def add_event(title, wday, start_time, end_time, location, weeks_list):
    global uid_counter
    for w in weeks_list:
        days_offset = (w - 1) * 7 + wday
        evt_date = w1_monday + datetime.timedelta(days=days_offset)
        
        dt_start = datetime.datetime.combine(evt_date, datetime.time(*start_time))
        dt_end = datetime.datetime.combine(evt_date, datetime.time(*end_time))
        
        # Format: YYYYMMDDTHHMMSS
        dt_start_str = dt_start.strftime("%Y%m%dT%H%M%S")
        dt_end_str = dt_end.strftime("%Y%m%dT%H%M%S")
        now_str = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
        
        lines.extend([
            "BEGIN:VEVENT",
            f"UID:openclaw-schedule-{uid_counter}@localhost",
            f"DTSTAMP:{now_str}Z",
            f"DTSTART;TZID=Asia/Shanghai:{dt_start_str}",
            f"DTEND;TZID=Asia/Shanghai:{dt_end_str}",
            f"SUMMARY:{title}",
            f"LOCATION:{location}",
            "END:VEVENT"
        ])
        uid_counter += 1

all_18 = list(range(1, 19))
odd_18 = list(range(1, 19, 2))
labor_weeks = [w for w in range(1, 19) if w % 4 in (1, 2)]
sz_weeks = [5, 6, 7, 8]

# MON
add_event("高等数学(下) (谢嘉宁)", 0, (8, 0), (9, 35), "校本部之远楼(5#)103", all_18)
add_event("大学生心理健康教育 (李昊然)", 0, (9, 55), (11, 30), "校本部之远楼(5#)303", odd_18)
add_event("中国近现代史纲要 (宋正)", 0, (13, 0), (15, 25), "校本部之远楼(5#)510", all_18)
add_event("会计学 (庄汶资)", 0, (18, 15), (20, 40), "校本部之远楼(5#)108", all_18)

# TUE
add_event("英语精读2 (马喜文)", 1, (9, 55), (11, 30), "校本部之远楼(5#)312", all_18)
add_event("英语听说2 (王向红)", 1, (13, 0), (14, 35), "校本部笃行楼202", all_18)

# WED
add_event("应用写作 (周咏梅)", 2, (8, 0), (9, 35), "校本部之远楼(5#)810", odd_18)
add_event("形势与政策2 (丁涛)", 2, (9, 55), (11, 30), "校本部之远楼(5#)E101", sz_weeks)
add_event("马克思主义基本原理 (王坤平)", 2, (13, 0), (15, 25), "校本部之远楼(5#)103", odd_18)
add_event("微观经济学 (谷雨)", 2, (18, 15), (19, 50), "校本部之远楼(5#)105", all_18)

# THU
add_event("劳动教育 (赵晗)", 3, (8, 0), (9, 35), "校本部之远楼(5#)203", labor_weeks)
add_event("高等数学(下) (谢嘉宁)", 3, (9, 55), (11, 30), "校本部之远楼(5#)103", all_18)
add_event("数据处理与程序设计 (陶永明)", 3, (13, 0), (14, 35), "校本部笃行楼509", all_18)

# FRI
add_event("习近平新时代中国特色社会主义思想概论 (韩丹丹)", 4, (8, 0), (9, 35), "校本部之远楼(5#)103", all_18)
add_event("微观经济学 (谷雨)", 4, (9, 55), (11, 30), "校本部之远楼(5#)105", all_18)
add_event("线性代数 (张蕴资)", 4, (13, 0), (15, 25), "校本部播慧楼201", all_18)

lines.append("END:VCALENDAR")

with open('schedule.ics', 'w', encoding='utf-8') as f:
    f.write('\\n'.join(lines))
