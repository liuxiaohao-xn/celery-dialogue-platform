import regex as re, arrow
import calendar
from typing import Text, List, Dict, Tuple
from src.nlu.utils.redis_data import Global_Data
from src.nlu.utils.util import Singleton


@Singleton
class Extract_Time():
    '''抽取时间'''

    def __init__(self):
        Gdata = Global_Data()
        self.time_rules = Gdata.time_rules

    def extract(self, query: Text) -> List:
        # 抽取汉字中文时间并转为阿拉伯数字时间
        CHN_time, norm_time = [], []
        result_all = self.time_rules.finditer(query)
        if result_all != None:
            start_index, end_index = -1, -1
            for results in result_all:
                cn_time = results.group()
                start_index = results.start()
                cn_time = re.sub("半个小时|半个钟头|半小时|半个钟|半", "三十分钟", cn_time)
                cn_time = re.sub("分钟|分", "分", cn_time)
                cn_time = re.sub("小时|钟头|点钟|钟|时", "点", cn_time)
                if start_index == end_index:
                    CHN_time[-1] += cn_time
                else:
                    CHN_time.append(cn_time)
                end_index = results.end()

        if len(CHN_time) > 0:
            for cn_time in CHN_time:
                num_time = self.cn2num(cn_time)
                n_t = self.time_normalize(num_time)
                if n_t:
                    norm_time.append(n_t)
        return norm_time

    def cn2num(self, cn_time: Text) -> Text:
        # 将汉字格式时间转化为数字格式的时间
        dict_num = {"〇": "0", "零": "0", "一": "1", "二": "2", "两": "2", "三": "3", "四": "4",
                    "五": "5", "六": "6", "七": "7", "八": "8", "九": "9", "十": "10"}

        week_rule = "(?<=星期|周)(一|二|三|四|五|六|末|天)"
        week_com = re.compile(week_rule)
        week_CHN = week_com.finditer(cn_time)
        if week_CHN != None:
            for week in week_CHN:
                CHN = week.group()
                num = dict_num.get(CHN, '7')
                cn_time = week_com.sub(num, cn_time, 1)

        ten_flag, num = False, 0
        cn_rule = "([一二三四五六七八九]?[十][一二两三四五六七八九]?)|([零一二两三四五六七八九])"
        cn_com = re.compile(cn_rule)
        cn_num = cn_com.finditer(cn_time)
        if cn_num != None:
            for CHN in cn_num:
                chn = CHN.group()
                for c in chn[::-1]:
                    if ten_flag == True:
                        num = (int(dict_num.get(c)) - 1) * 10 + num
                        ten_flag = False
                        continue
                    if c == "十":
                        num = num + 10
                        ten_flag = True
                        continue
                    num += int(dict_num.get(c))
                cn_time = cn_com.sub(str(num), cn_time, 1)
                ten_flag, num = False, 0
        return cn_time

    def time_normalize(self, num_time: Text) -> Text:
        # 将时间进行标准化 2点40分 ->2:40:00,下午3点半 -> 15:30:00
        Ymd_month, Ymd_week, Ymd_date, norm_time = '', '', '', ''
        date_time = arrow.now()
        sys_time = date_time.format("YYYY-MM-DD-HH-mm-ss").split("-")

        user_time = ['00', '00', '00', '00', '00', '00', False]

        if re.search("(星期几|周几)|(几|多少)[号日]|天气", num_time):
            return None

        rule = "(昨天|前天|大前天|明天|后天|大后天|今天)"
        rule_com = re.compile(rule)
        match = rule_com.search(num_time)
        if match != None:
            day = match.group()
            if day == "昨天":
                span = -1
            elif day == "前天":
                span = -2
            elif day == "大前天":
                span = -3
            elif day == "明天" or day == "第2天":
                span = 1
            elif day == "后天":
                span = 2
            elif day == "大后天":
                span = 3
            elif day == "今天":
                span = 0
            Ymd_date = date_time.shift(days=span)
            num_time = rule_com.sub('', num_time, 1)

        rule = "([下]{1,})(个月|月)|((当前|这个|本|这|当)月)"
        rule_com = re.compile(rule)
        match = rule_com.search(num_time)
        if match != None:
            span = match.group(1) if match.group(1) else ''
            Ymd_month = date_time.shift(months=len(span))
            num_time = rule_com.sub('', num_time, 1)

        rule = "([上]{1,})(个月|月)"
        rule_com = re.compile(rule)
        match = rule_com.search(num_time)
        if match != None:
            span = match.group(1)
            Ymd_month = date_time.shift(months=-len(span))
            num_time = rule_com.sub('', num_time, 1)

        rule = "([0-1]?[0-9])(月)([0-3]?[0-9])(日|号)?"
        rule_com = re.compile(rule)
        match = rule_com.search(num_time)
        if match != None:
            user_time[1] = match.group(1)
            user_time[2] = match.group(3)
            user_time[6] = True
            if not Ymd_date:
                user_time = self.future_time(sys_time, user_time, 3)
            num_time = rule_com.sub('', num_time, 1)

        rule = "([0-3]?[0-9])(日|号)"
        rule_com = re.compile(rule)
        match = rule_com.search(num_time)
        if match != None:
            user_time[2] = match.group(1)
            user_time[6] = True
            if Ymd_month:
                user_time[0] = str(Ymd_month.year)
                user_time[1] = str(Ymd_month.month)
            elif Ymd_date and Ymd_date.day == int(match.group(1)):
                user_time[0] = str(Ymd_date.year)
                user_time[1] = str(Ymd_date.month)
            else:
                user_time = self.future_time(sys_time, user_time, 3)
            num_time = rule_com.sub('', num_time, 1)

        rule = "(下{1,})(个)?(星期|周)([1-7])|(这个|这|本)(星期|周)([1-7])"
        rule_com = re.compile(rule)
        match = rule_com.search(num_time)
        if match != None:
            if match.group(1):
                week = match.group(1)
                week_time = match.group(4)
            elif match.group(7):
                week = ''
                week_time = match.group(7)
            span = int(week_time) - 1 - date_time.weekday()
            Ymd_week = date_time.shift(weeks=len(week), days=span)
            num_time = rule_com.sub('', num_time, 1)
            week_flag = True

        rule = "(上{1,})(个)?(星期|周)([1-7])"
        rule_com = re.compile(rule)
        match = rule_com.search(num_time)
        if match != None:
            week = match.group(1)
            week_time = match.group(4)
            span = int(week_time) - 1 - date_time.weekday()
            Ymd_week = date_time.shift(weeks=-len(week), days=span)
            num_time = rule_com.sub('', num_time, 1)
            week_flag = True

        rule = "(?<!这个|下个|上个|上|下|这|本)(星期|周)([1-7])"
        rule_com = re.compile(rule)
        match = rule_com.search(num_time)
        if match != None:
            week_time = int(match.group(2)) - 1
            if Ymd_date and Ymd_date.weekday() == week_time:
                Ymd_week = Ymd_date
            elif user_time[6] and arrow.get('-'.join(user_time[:3])).weekday() == week_time:
                Ymd_week = arrow.get('-'.join(user_time[:3]))
            elif user_time[6]:
                user_time[0] = str(date_time.year)
                if arrow.get('-'.join(user_time[:3])).weekday() == week_time:
                    Ymd_week = arrow.get('-'.join(user_time[:3]))
                else:
                    span = week_time - date_time.weekday()
                    Ymd_week = date_time.shift(days=span)
            elif Ymd_date or user_time[6]:
                span = week_time - date_time.weekday()
                Ymd_week = date_time.shift(days=span)
            elif not Ymd_date and not user_time[6]:
                span = week_time - date_time.weekday()
                if week_time < date_time.weekday():
                    Ymd_week = date_time.shift(weeks=1, days=span)
                else:
                    Ymd_week = date_time.shift(days=span)
                user_time = Ymd_week.format("YYYY-MM-DD").split("-") + user_time[3:]
            num_time = rule_com.sub('', num_time, 1)
            week_flag = True

        rule = "([0-2]?[0-9])(点)([0-6]?[0-9])(刻点|分|刻)?"
        rule_com = re.compile(rule)
        match = rule_com.search(num_time)
        if match != None:
            hour_time = int(match.group(1))
            minute_time = int(match.group(3))
            if re.search("下午|傍晚|晚间|晚上|夜晚|深夜", num_time) != None and hour_time <= 12:
                hour_time += 12
            elif re.search("凌晨|早晨|清晨|早上|上午|中午|午间", num_time) == None and hour_time < 12:
                if date_time.hour > 12 and hour_time + 12 > date_time.hour:
                    hour_time += 12
            if "刻" in num_time:
                minute_time *= 15
            user_time[3] = str(hour_time)
            user_time[4] = str(minute_time)
            if not Ymd_date and not Ymd_week and not Ymd_month:
                user_time = self.future_time(sys_time, user_time, 5)
            num_time = rule_com.sub('', num_time, 1)

        rule = "(([0-2]?[0-9])(个)?(点)(之后|以后|后))|((过)([0-2]?[0-9])(个点|点)(之后|以后|后)?)"
        rule_com = re.compile(rule)
        match = rule_com.search(num_time)
        if match != None:
            hour_time = re.search("[0-2]?[0-9](?=个点|点)", num_time).group()
            hour_t = date_time.shift(hours=int(hour_time))
            user_time = hour_t.format('YYYY-MM-DD-HH-mm-ss').split("-")
            user_time.append(False)
            num_time = rule_com.sub('', num_time, 1)

        rule = "([0-2]?[0-9])(?=点)"
        rule_com = re.compile(rule)
        match = rule_com.search(num_time)
        if match != None:
            hour_time = int(match.group())
            if re.search("下午|晚上|傍晚|夜晚|中午", num_time) != None and hour_time <= 12:
                hour_time += 12
            elif re.search("凌晨|早晨|清晨|早上|上午|中午|午间", num_time) == None and hour_time < 12:
                if date_time.hour > 12 and hour_time + 12 > date_time.hour:
                    hour_time += 12
            user_time[3] = str(hour_time)
            if not Ymd_date and not Ymd_week and not Ymd_month:
                user_time = self.future_time(sys_time, user_time, 5)

        rule = "(([0-6]?[0-9])(刻点|分)(之后|以后|后))|(过([0-6]?[0-9])(刻点|分))"
        rule_com = re.compile(rule)
        match = rule_com.search(num_time)
        if match != None:
            minute_time = re.search("[0-6]?[0-9](?=刻点|分)", num_time).group()
            minute_time = int(minute_time)
            if "刻" in num_time:
                minute_time *= 15
            minute_t = date_time.shift(minutes=minute_time)
            user_time = minute_t.format('YYYY-MM-DD-HH-mm-ss').split("-")
            user_time.append(False)
            num_time = rule_com.sub('', num_time, 1)

        rule = "([0-6]?[0-9])(刻点|分|刻)"
        rule_com = re.compile(rule)
        match = rule_com.search(num_time)
        if match != None:
            minute_time = match.group(1)
            minute_time = int(minute_time)
            if "刻" in num_time:
                minute_time *= 15
            user_time[4] = str(minute_time)
            user_time = self.future_time(sys_time, user_time, 5)
            if user_time[3] == "00":
                user_time[3] = str(date_time.hour)

        for i in range(3):
            if user_time[i] == "00":
                user_time[i] = sys_time[i]
        user_time = self.change(user_time)

        time_ymd = "-".join(user_time[0:3])
        time_hms = ":".join(user_time[3:6])
        if time_hms == "00:00:00":
            return ''
        if Ymd_date and Ymd_week:
            time_date = Ymd_date.strftime("%Y-%m-%d")
            time_week = Ymd_week.strftime("%Y-%m-%d")
            time_date = time_date + " " + time_hms
            time_week = time_week + " " + time_hms
            norm_time = time_date + ";" + time_week
        elif Ymd_date and user_time[6]:
            time_date = Ymd_date.strftime("%Y-%m-%d")
            time_date = time_date + " " + time_hms
            time_ymd = time_ymd + " " + time_hms
            norm_time = time_date + ";" + time_ymd
        elif user_time[6] and Ymd_week:
            time_week = Ymd_week.strftime("%Y-%m-%d")
            time_week = time_week + " " + time_hms
            time_ymd = time_ymd + " " + time_hms
            norm_time = time_ymd + ";" + time_week
        else:
            if Ymd_date:
                time_date = Ymd_date.strftime("%Y-%m-%d")
                norm_time = time_date + " " + time_hms
            elif Ymd_week:
                time_week = Ymd_week.strftime("%Y-%m-%d")
                norm_time = time_week + " " + time_hms
            else:
                norm_time = time_ymd + " " + time_hms

        return norm_time

    def change(self, nor_time: List) -> List:
        # 将个位数的时间标准化
        for i, ntime in enumerate(nor_time[:-1]):
            if len(ntime) <= 2 and i == 0:
                nor_time[i] = "20" + ntime
            elif len(ntime) < 2:
                nor_time[i] = "0" + ntime
        return nor_time

    def future_time(self, sys_time: Text, norm_time: List, cut_index=6) -> List:
        # 处理倾向于未来时间的情况
        try:
            split_time = sys_time
            date_time = arrow.get("-".join(sys_time), "YYYY-MM-DD-HH-mm-ss")
            flag = ''
            for i, n_t in enumerate(norm_time[:cut_index]):
                if n_t == "00" and not flag:
                    continue
                elif int(n_t) == int(split_time[i]) and not flag:
                    # 进位+1位置
                    flag = i + 1
                elif int(n_t) > int(split_time[i]):
                    return norm_time
                elif int(n_t) < int(split_time[i]):
                    if flag:
                        i = flag - 1
                    if i == 1:
                        date_time = date_time.shift(years=1)
                    elif i == 2:
                        date_time = date_time.shift(months=1)
                    elif i == 3:
                        date_time = date_time.shift(days=1)
                    elif i == 4:
                        date_time = date_time.shift(hours=1)
                    split_time = date_time.format("YYYY-MM-DD-HH-mm-ss").split("-")
                    norm_time = split_time[:i] + norm_time[i:]
                    break
            return norm_time
        except Exception as e:
            print(e)
            return norm_time

    def check_time(self, norm_time: Text) -> Text:
        # 校验时间对错,并校对时间
        if not norm_time:
            return ''
        try:
            split_time = norm_time.split(";")
            if len(split_time) >= 2:
                for i in range(len(split_time[:-1])):
                    if split_time[i] != split_time[i + 1]:
                        return ''
            sure_time = split_time[0].split(" ")
            ymd_time = sure_time[0].split("-") + sure_time[1].split(":")
            int_time = [int(t) for t in ymd_time]
            for i, int_t in enumerate(int_time):
                if i == 0 and len(ymd_time[i]) <= 2:
                    ymd_time[i] = "20" + ymd_time(i)
                elif i == 1:  # 排除大于12月的情况
                    if int_t > 12:
                        return ''
                elif i == 2:  # 排除6月31号，8月32号等这种情况
                    total_day = calendar.monthrange(int_time[0], int_time[1])
                    if int_t > total_day[1]:
                        return ''
                elif i == 3:  # 校对二十四小时的情况
                    if int_t > 24:
                        return ''
                    elif int_t == 24:
                        hms_time = arrow.get(sure_time[0] + ' 24:00:00')
                        hms_time = hms_time.format('YYYY-MM-DD-HH-mm-ss').split("-")
                        for j, h_t in enumerate(hms_time[:4]):
                            ymd_time[j] = h_t
                elif i == 4:  # 校对60分钟的情况
                    if int_t > 60:
                        return ''
                    elif int_t == 60:
                        add_time = ymd_time[0] + '-' + ymd_time[1] + '-' + ymd_time[2] + " " + ymd_time[3]
                        hms_time = arrow.get(add_time)
                        hms_time = hms_time.shift(minutes=60)
                        ymd_time = hms_time.format("YYYY-MM-DD-HH-mm-ss").split("-")

            norm_time = "-".join(ymd_time[0:3]) + ' ' + ":".join(ymd_time[3:])
        except Exception as e:
            print(e)
        return norm_time


if __name__ == '__main__':
    ex_time = Extract_Time()
    ext_time = ex_time.extract("今天下午三点半")
    ext_time = ex_time.extract("八月二十六号星期六上午十点")
    print(ext_time)
    num_time = ex_time.cn2num("二零二二年八月十七号下午三点三十分")
    print(num_time)
    nor_time = ex_time.check_time("2022-08-18 08:00:00;2022-08-18 08:00:00")
    print(nor_time)


