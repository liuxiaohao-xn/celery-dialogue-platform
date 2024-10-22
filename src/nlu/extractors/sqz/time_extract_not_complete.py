import regex as re, arrow
import calendar, os, sys
from typing import Text, List, Dict, Tuple
from src.nlu.utils.redis_data import Global_Data
from src.nlu.utils.util import Singleton


def get_arrow_time(org_time) -> Text:
    # 将标准时间格式生成为可操作时间
    try:
        return arrow.get(org_time)
    except Exception:
        raise Exception("Wrong Time Format")


class Get_User_Time():
    TIME_OUT_MODE = 0  # 过去时间
    TIME_NOT_COMPLETED = 1  # 未补全时间
    TIME_COMPLETED = 2  # 已补全时间
    TIME_WRONG_WEEK = 3  # 日期和星期错误
    origin_time = {
        "above_time": None,
        "period_time": 12,
        "flag": False}
    
    def __init__(self):
        self.query = None
        self.year = None
        self.month = None
        self.day = None  # 日
        self.hour = None
        self.minute = None
        self.second = None
        
        # 周，包括周一，这周一，下周一，上周一
        self.week = None
        # 天，包括今天，明天，昨天，第二天，第二日，下一天，过两天
        self.date = None
        # 时间段，包括凌晨，上午，下午，晚上等
        self.period = None
        # 标准时间 -> 0000-00-00 00:00:00
        self.norm_time = None
        # 特殊标志
        self.flag = False
    
    def get_time(self):
        # 从提取的原生数据中提取时间
        self.week_time, self.Ymd_week, self.plural_flag = '', '', False
        self.date_time = arrow.now()
        self.sys_time = self.date_time.format("YYYY-MM-DD-HH-mm-ss").split("-")
        self.user_time = ['00', '00', '00','00', '00', '00', False]
        
        self.get_plural_time()
        if not self.plural_flag:
            self.get_date()
            self.get_month()
            self.get_day()
            self.get_week()
        self.get_period_time()
        self.fill_above_time()
        self.get_hour()
        self.get_minute()
        self.get_unite_time()
    
    def get_plural_time(self):
        # 处理复数时间
        ag_time = ''
        if self.date and self.week:
            self.plural_flag = True
            self.get_date()
        elif self.month and self.day and self.week:
            self.plural_flag = True
            self.get_month()
            self.get_day()
        elif self.day and self.week:
            self.plural_flag = True
            self.get_day()
        
        if self.user_time[6]:
            ag_time = get_arrow_time('-'.join(self.user_time[:3]))
        if not ag_time:
            return
        week_time = int(self.week[-1])-1
        if ag_time.weekday() != week_time: # 判断日期和星期是否相等
            span = week_time - self.date_time.weekday()
            self.Ymd_week = self.date_time.shift(days = span)
    
    def get_date(self):
        # 处理天相关的原始数据
        if not self.date:
            return
        rule = "(昨|前|大前|明|后|大后|今|第2|下1)(天|日)"
        rule_com = re.compile(rule)
        match = rule_com.search(self.date)
        if match != None:
            day = match.group(1)
            if day == "昨":
                span = -1
            elif day=="前":
                span = -2
            elif day=="大前":
                span = -3
            elif day=="明" or day=="第2" or day=="下1":
                span = 1
            elif day=="后":
                span = 2
            elif day=="大后":
                span = 3
            elif day=="今":
                span = 0
            Ymd_date = self.date_time.shift(days = span)
            self.user_time = Ymd_date.format("YYYY-MM-DD").split("-") +\
                self.user_time[3:]
            self.user_time[6] = True
    
    def get_month(self):
        # 处理月相关的原始数据
        if not self.month:
            return
        self.user_time[0] = str(self.date_time.year)
        self.user_time[6] = True
        rule = "([下]{1,})(个月|月)|((当前|这个|本|这|当)月)"
        rule_com = re.compile(rule)
        match = rule_com.search(self.month)
        if match != None:
            span = match.group(1) if match.group(1) else ''
            Ymd_month = self.date_time.shift(months = len(span))
            self.user_time[1] = str(Ymd_month.month)
            return
        
        rule = "([上]{1,})(个月|月)"
        rule_com = re.compile(rule)
        match = rule_com.search(self.month)
        if match != None:
            span = match.group(1)
            Ymd_month = self.date_time.shift(months =-len(span))
            self.user_time[1] = str(Ymd_month.month)
            return
        
        rule = "([0-1]?[0-9])(?=月)"
        rule_com = re.compile(rule)
        match = rule_com.search(self.month)
        if match != None:
            self.user_time[1] = match.group(1)
    
    def get_day(self):
        # 处理日、号相关的原始数据
        if not self.day:
            return
        self.user_time[2] = self.day[:-1]
        self.user_time[6] = True
        if not self.month:
            self.user_time[0] = str(self.date_time.year)
            self.user_time[1] = str(self.date_time.month)
    
    def get_week(self):
        # 处理星期相关的原始数据
        if not self.week:
            return
        rule = "(下{1,})(个)?(星期|周)([1-7])|(这个|这|本)(星期|周)([1-7])"
        rule_com = re.compile(rule)
        match = rule_com.search(self.week)
        if match != None:
            if match.group(1):
                week = match.group(1)
                week_time = int(match.group(4)) - 1
            elif match.group(7):
                week = ''
                week_time = int(match.group(7)) - 1
            span = week_time - self.date_time.weekday()
            Ymd_week = self.date_time.shift(weeks=len(week), days=span)
            self.user_time = Ymd_week.format("YYYY-MM-DD").split("-") + self.user_time[3:]
            self.user_time[6] = True
            return
        
        rule = "(上{1,})(个)?(星期|周)([1-7])"
        rule_com = re.compile(rule)
        match = rule_com.search(self.week)
        if match != None:
            week = match.group(1)
            week_time = int(match.group(4)) - 1
            span = week_time - self.date_time.weekday()
            Ymd_week = self.date_time.shift(weeks=-len(week), days=span)
            self.user_time = Ymd_week.format("YYYY-MM-DD").split("-") + self.user_time[3:]
            self.user_time[6] = True
            return
        
        rule = "(?<!这个|下个|上个|上|下|这|本)(星期|周)([1-7])"
        rule_com = re.compile(rule)
        match = rule_com.search(self.week)
        if match != None:
            week_time = int(match.group(2))-1
            span = week_time - self.date_time.weekday()
            if week_time < self.date_time.weekday():
                Ymd_week = self.date_time.shift(weeks=1, days=span)
            else:
                Ymd_week = self.date_time.shift(days = span)
                if span == 0:
                    self.week_time = Ymd_week
            self.user_time = Ymd_week.format("YYYY-MM-DD").split("-") + self.user_time[3:]
            self.user_time[6] = True
    
    def get_period_time(self):
        # 处理时间段相关的原始数据
        if not self.period:
            return
        if re.search("(下午|傍晚|晚间|晚上|夜晚|深夜)",self.period)!=None:
            self.period = 12
        elif re.search("(凌晨|早晨|清晨|早上|上午|中午|正午|午间)",self.period)!=None:
            self.period = 0
                
    
    def get_hour(self):
        # 处理小时相关的原始数据
        if not self.hour:
            return
        if self.minute:
            self.hour += self.minute
            self.minute = None
        
        rule = "([0-2]?[0-9])(点)([0-6]?[0-9])(刻点|分|刻)"
        rule_com = re.compile(rule)
        match = rule_com.search(self.hour)
        if match != None:
            hour_time = int(match.group(1))
            minute_time = int(match.group(3))
            hour_time = self.future_12_time(hour_time,minute_time)
            if "刻" in self.hour:
                minute_time *= 15
            self.user_time[3] = str(hour_time)
            self.user_time[4] = str(minute_time)
            if not self.user_time[6]:
                self.user_time = self.future_time(5)
            elif self.week_time:
                self.user_time = self.future_week_time()
            self.user_time[6] = True
            return
        
        rule = "(([0-2]?[0-9])(个)?(点)(之后|以后|后))|((过)([0-2]?[0-9])(个点|点)(之后|以后|后)?)"
        rule_com = re.compile(rule)
        match = rule_com.search(self.hour)
        if match != None:
            hour_time = re.search("[0-2]?[0-9](?=个点|点)",self.hour).group()
            hour_t = self.date_time.shift(hours=int(hour_time))
            self.user_time = hour_t.format('YYYY-MM-DD-HH-mm-ss').split("-")
            self.user_time.append(True)
            return
        
        rule = "([0-2]?[0-9])(?=点)"
        rule_com = re.compile(rule)
        match = rule_com.search(self.hour)
        if match != None:
            hour_time = int(match.group())
            hour_time = self.future_12_time(hour_time)
            self.user_time[3] = str(hour_time)
            if not self.user_time[6]:
                self.user_time = self.future_time(5)
            elif self.week_time:
                self.user_time = self.future_week_time()
            self.user_time[6] = True
    
    def get_minute(self):
        # 处理分钟相关的原始数据
        if not self.minute:
            return
        rule = "(([0-6]?[0-9])(刻点|分)(之后|以后|后))|(过([0-6]?[0-9])(刻点|分))"
        rule_com = re.compile(rule)
        match = rule_com.search(self.minute)
        if match != None:
            minute_time = re.search("[0-6]?[0-9](?=刻点|分)",self.minute).group()
            minute_time = int(minute_time)
            if "刻" in self.minute:
                minute_time *= 15
            minute_t = self.date_time.shift(minutes=minute_time)
            self.user_time = minute_t.format('YYYY-MM-DD-HH-mm-ss').split("-")
            self.user_time.append(True)
            return
        
        rule = "([0-6]?[0-9])(?=刻点|分|刻)"
        rule_com = re.compile(rule)
        match = rule_com.search(self.minute)
        if match != None:
            minute_time = match.group()
            minute_time = int(minute_time)
            if "刻" in self.minute:
                minute_time *= 15
            self.user_time[4] = str(minute_time)
            if minute_time > self.date_time.minute:
                self.user_time[3] = str(self.date_time.hour)
            if not self.user_time[6]:
                self.user_time = self.future_time(5)
            self.user_time[6] = True
        
    def get_unite_time(self):
        # 获取联合时间
        unite_time = ''
        # 将年月日补全
        if not self.user_time[6]:
            if self.period and not self.origin_time["period_time"] and\
                not self.origin_time["above_time"]:
                self.origin_time["period_time"] = self.period
            return None
        
        for i in range(3):
            if self.user_time[i] == "00":
                self.user_time[i] = self.sys_time[i]
        # 将长度为1的时间标准化
        self.user_time = self.change(self.user_time)
        
        time_ymd = "-".join(self.user_time[0:3])
        time_hms = ":".join(self.user_time[3:6])
        
        if self.user_time[6] and self.Ymd_week:
            # 处理复数时间的情况
            time_week = self.Ymd_week.format("YYYY-MM-DD")
            time_week = time_week + " " + time_hms
            time_ymd = time_ymd + " " + time_hms
            unite_time = time_ymd + ";" + time_week
        else:
            unite_time = time_ymd + " " + time_hms
        self.norm_time = unite_time
        
    def update_above_time(self):
        # 更新最终时间
        if not self.norm_time:
            raise Exception("Above Time Update Error")
        time_hms = self.norm_time.split(" ")[1]
        if self.origin_time["flag"]==False and self.is_past_time():
            # self.reset_origin_time()
            return self.TIME_OUT_MODE
        elif self.origin_time["flag"]==False and self.is_wrong_week():
            # self.reset_origin_time()
            return self.TIME_WRONG_WEEK
        self.origin_time["flag"] = False
        if time_hms == "00:00:00":
            if not self.origin_time["above_time"] and not self.origin_time["period_time"]:
                self.origin_time["above_time"] = self.norm_time
                self.origin_time["period_time"] = self.period
            return self.TIME_NOT_COMPLETED
        elif time_hms != "00:00:00":
            self.origin_time["above_time"] = self.norm_time
            self.origin_time["period_time"] = self.period
            return self.TIME_COMPLETED
    
    def change(self, norm_time:List) -> List:
        # 将长度为1的时间标准化
        for i,ntime in enumerate(norm_time[:-1]):
            if i==0 and len(ntime)<=2:
                norm_time[i] = "20" + ntime
            elif len(ntime)<2:
                norm_time[i] = "0" + ntime
        return norm_time
    
    def future_time(self, cut_index=6) -> List:
        # 处理日期，时间点相关的，倾向于未来时间的情况
        try:
            flag = ''
            for i,n_t in enumerate(self.user_time[:cut_index]):
                if n_t == "00" and not flag:
                    continue
                elif int(n_t)==int(self.sys_time[i]) and not flag:
                    # 进位+1位置
                    flag = i + 1  # 加1是为了防止0的出现
                elif int(n_t)>int(self.sys_time[i]):
                    return self.user_time
                elif int(n_t)<int(self.sys_time[i]):
                    if flag:
                        i = flag - 1
                    if i==1:
                        shift_time = self.date_time.shift(years=1)
                    elif i==2:
                        shift_time = self.date_time.shift(months=1)
                    elif i==3:
                        shift_time = self.date_time.shift(days=1)
                    elif i==4:
                        shift_time = self.date_time.shift(hours=1)
                    split_time = shift_time.format("YYYY-MM-DD-HH-mm-ss").split("-")
                    self.user_time = split_time[:i] + self.user_time[i:]
                    break
            return self.user_time
        except Exception as e:
            print(e)
            return self.user_time
    
    def future_12_time(self, hour_time:int, minute_time=0):
        # 处理12小时制的时间
        if self.period==12 and hour_time <= 12:
            hour_time += 12
        elif self.period==0:
            hour_time += 0
        elif self.origin_time["period_time"]==12 and hour_time <= 12:
            hour_time += 12
        elif self.origin_time["period_time"]==0:
            hour_time += 0
        elif self.origin_time["period_time"]==None and\
            self.period == None and not self.user_time[6]:
            if hour_time==self.date_time.hour:
                if minute_time<=self.date_time.minute and hour_time+12 <= 24:
                    hour_time += 12
            elif hour_time<self.date_time.hour:
                if self.date_time.hour<hour_time+12<=24:
                    hour_time += 12
                elif hour_time+12==self.date_time.hour and minute_time>self.date_time.minute:
                    hour_time += 12
        return hour_time
    
    def future_week_time(self) -> List:
        # 处理跟星期相关的、倾向于未来时间的情况
        shift_time = self.date_time
        try:
            if int(self.user_time[3])<int(self.sys_time[3]):
                shift_time = self.week_time.shift(weeks=1)
            elif int(self.user_time[3])==int(self.sys_time[3]) and int(self.user_time[4])<=int(self.sys_time[4]):
                shift_time = self.week_time.shift(weeks=1)
            self.user_time = shift_time.format("YYYY-MM-DD").split("-") + self.user_time[3:]
            return self.user_time
        except Exception as e:
            print(e)
            return self.user_time
    
    def fill_above_time(self):
        # 将上文时间补全到下文时间中
        if self.origin_time["above_time"] and not self.user_time[6]:
            if self.period==None or\
                (self.period!=None and self.origin_time["period_time"] == None):
                self.user_time = self.origin_time["above_time"].split(" ")[0].split("-")
                self.user_time += ["00","00","00",True]
        elif self.user_time[6] and self.period==None:
            self.period = 0
    
    @classmethod
    def reset_origin_time(cls):
        # 重置上文时间
        cls.origin_time = {
            "above_time": None,
            "period_time": None,
            "flag": False}
    
    @classmethod
    def date_select(cls, select_time:Tuple):
        # 因在凌晨时段，则更新用户所选择的日期
        try:
            if cls.origin_time["above_time"]:
                above_time = arrow.get(cls.origin_time["above_time"])
            else:
                above_time = arrow.now()
            above_time_year = above_time.replace(year=select_time[0])
            above_time_month = above_time_year.replace(month=select_time[1])
            above_time_day = above_time_month.replace(day=select_time[2])
            cls.origin_time["above_time"] = above_time_day.format("YYYY-MM-DD HH:mm:ss")
        except:
            raise Exception("Date Select Error")

    def is_hms(self) -> bool:
        # 判断是否有时分秒
        try:
            if not self.norm_time:
                return False
            if self.norm_time.split(" ")[1] != "00:00:00":
                return True
            else:
                return False
        except Exception as e:
            raise Exception("Is Hms Error")
            
    def is_date_morning(self) -> Tuple:
        # 判断是否包含明天、后天、大后天等，且是否当前时间是凌晨
        try:
            if not self.date:
                return False
            match = re.search("(明|后|大后|第2|下1)[天日]",self.date)
            if self.is_early_morning and match != None:
                date_time = arrow.get(self.norm_time)
                date_time = date_time.shift(days=-1).format("YYYY-MM-DD HH:mm:ss")
                return (date_time, self.norm_time)
            else:
                return False
        except Exception as e:
            raise Exception("Is Date Morning Error")
    
    def is_early_morning(self) -> bool:
        # 判断当前时间是否是在凌晨0点到6点之间
        # if 0 <= arrow.now().hour < 6:
        if 12 <= arrow.now().hour < 18:
            return True
        else:
            return False
    
    def is_past_time(self) -> bool:
        #校验时间是否是过去时间,如果是过去时间，返回True，否则返回False
        if not self.norm_time:
            raise Exception("The Time Is None")
        try:
            date_time = arrow.now().format("YYYY-MM-DD").split("-")
            user_time = arrow.get(self.norm_time).format("YYYY-MM-DD").split("-")
            for i in range(3):
                if int(user_time[i])<int(date_time[i]):
                    return True
            else:
                return False
        except Exception as e:
            raise Exception("Is Past Time Error")
    
    def is_wrong_week(self) -> bool:
        # 判断日期对应的星期是否错误,错误返回True，正确返回False
        if not self.norm_time:
            raise Exception("The Time Is None")
        try:
            split_time = self.norm_time.split(";")
            if len(split_time) >= 2:
                for i in range(len(split_time[:-1])):
                    if split_time[i] != split_time[i+1]:
                        return True
        except Exception as e:
            raise Exception("Is Wrong Week Error")
        self.origin_time["flag"] = True
        return False



@Singleton
class Extract_Time():
    '''抽取时间'''
    def __init__(self):
        Gdata = Global_Data()
        self.time_rules = Gdata.time_rules
    
    def extract(self, query:Text) -> List:
        # 抽取汉字中文时间并转为阿拉伯数字时间
        CHN_time, norm_time = [], []
        self.gut = Get_User_Time()
        self.gut.query = query
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
            try:
                for cn_time in CHN_time:
                    num_time = self.cn2num(cn_time)
                    self.gut = self.time_normalize(num_time)
                    if self.gut != None:
                        self.gut.get_time()
                        if self.gut.norm_time:
                            norm_time.append(self.gut)
            except Exception as e:
                raise Exception("Time Extract Wrong!")
        return norm_time
    
    def cn2num(self, cn_time:Text) -> Text:
        # 将汉字格式时间转化为数字格式的时间
        dict_num = {"〇":"0", "零":"0", "一":"1", "二":"2", "两":"2", "三":"3", "四":"4",
            "五":"5", "六":"6", "七":"7", "八":"8", "九":"9", "十":"10"}
        
        week_rule = "(?<=星期|周)(一|二|三|四|五|六|末|天)"
        week_com = re.compile(week_rule)
        week_CHN = week_com.finditer(cn_time)
        if week_CHN != None:
            for week in week_CHN:
                CHN = week.group()
                num = dict_num.get(CHN,'7')
                cn_time = week_com.sub(num,cn_time,1)
        
        ten_flag, num = False, 0
        cn_rule = "([一二三四五六七八九]?[十][一二两三四五六七八九]?)|([零一二两三四五六七八九])"
        cn_com = re.compile(cn_rule)
        cn_num = cn_com.finditer(cn_time)
        if cn_num != None:
            for CHN in cn_num:
                chn = CHN.group()
                for c in chn[::-1]:
                    if ten_flag == True:
                        num = (int(dict_num.get(c))-1)*10+num
                        ten_flag = False
                        continue
                    if c == "十":
                        num = num+10
                        ten_flag = True
                        continue
                    num += int(dict_num.get(c))
                cn_time = cn_com.sub(str(num),cn_time,1)
                ten_flag, num = False, 0
        return cn_time
    
    def time_normalize(self,num_time:Text) -> Text:
        # 将时间进行标准化 2点40分 ->2:40:00,下午3点半 -> 15:30:00
        self.num_time = num_time
        if re.search("(星期几|周几)|(几|多少)[号日]|天气", num_time):
            return None
        self.origin_date()
        self.origin_month()
        self.origin_day()
        self.origin_week()
        self.origin_period_time()
        self.origin_hour()
        self.origin_minute()
        return self.gut
    
    def origin_date(self):
        # 获取天相关的原始数据
        rule = "(昨|前|大前|明|后|大后|今|第2|下1)(天|日)"
        rule_com = re.compile(rule)
        match = rule_com.search(self.num_time)
        if match != None:
            self.gut.date = match.group()
            self.num_time = rule_com.sub('', self.num_time, 1)
        
    def origin_month(self):
        # 获取月相关的原始数据
        rule = "([下]{1,})(个月|月)|((当前|这个|本|这|当)月)"
        rule_com = re.compile(rule)
        match = rule_com.search(self.num_time)
        if match != None:
            self.gut.month = match.group()
            self.num_time = rule_com.sub('',self.num_time,1)
        
        rule = "([上]{1,})(个月|月)"
        rule_com = re.compile(rule)
        match = rule_com.search(self.num_time)
        if match != None:
            self.gut.month = match.group()
            self.num_time = rule_com.sub('',self.num_time,1)
        
        rule = "([0-1]?[0-9])(月)([0-3]?[0-9])(日|号)?"
        rule_com = re.compile(rule)
        match = rule_com.search(self.num_time)
        if match != None:
            self.gut.month = match.group(1)+match.group(2)
            if match.group(4) == None:
                self.gut.day = match.group(3) + "号"
            else:
                self.gut.day = match.group(3) + match.group(4)
            self.num_time = rule_com.sub('',self.num_time,1)
        
    def origin_day(self):
        # 获取号、日相关的原始数据
        rule = "([0-3]?[0-9])(日|号)"
        rule_com = re.compile(rule)
        match = rule_com.search(self.num_time)
        if match != None:
            self.gut.day = match.group()
            self.num_time = rule_com.sub('',self.num_time,1)
                
    def origin_week(self):
        # 获取星期相关的原始数据
        rule = "(下{1,})(个)?(星期|周)([1-7])|(这个|这|本)(星期|周)([1-7])"
        rule_com = re.compile(rule)
        match = rule_com.search(self.num_time)
        if match != None:
            self.gut.week = match.group()
            self.num_time = rule_com.sub('', self.num_time, 1)
            return
        
        rule = "(上{1,})(个)?(星期|周)([1-7])"
        rule_com = re.compile(rule)
        match = rule_com.search(self.num_time)
        if match != None:
            self.gut.week = match.group()
            self.num_time = rule_com.sub('', self.num_time, 1)
            return
        
        rule = "(?<!这个|下个|上个|上|下|这|本)(星期|周)([1-7])"
        rule_com = re.compile(rule)
        match = rule_com.search(self.num_time)
        if match != None:
            self.gut.week = match.group()
            self.num_time = rule_com.sub('', self.num_time, 1)
    
    def origin_period_time(self):
        # 获取时间段内的原始数据
        rule = "(凌晨|早晨|清晨|早上|上午|中午|正午|午间|下午|傍晚|晚间|晚上|夜晚|深夜)"
        rule_com = re.compile(rule)
        match = rule_com.search(self.num_time)
        if match != None:
            self.gut.period = match.group()
    
    def origin_hour(self):
        # 获取小时相关的原始数据
        rule = "([0-2]?[0-9])(点)([0-6]?[0-9])(刻点|分|刻)?"
        rule_com = re.compile(rule)
        match = rule_com.search(self.num_time)
        if match != None:
            self.gut.hour = match.group(1) + match.group(2)
            if match.group(4) != None:
                self.gut.minute = match.group(3) + match.group(4)
            else:
                self.gut.minute = match.group(3) + "分"
            self.num_time = rule_com.sub('', self.num_time, 1)
            return
        
        rule = "(([0-2]?[0-9])(个)?(点)(之后|以后|后))|((过)([0-2]?[0-9])(个点|点)(之后|以后|后)?)"
        rule_com = re.compile(rule)
        match = rule_com.search(self.num_time)
        if match != None:
            self.gut.hour = match.group()
            self.num_time = rule_com.sub('', self.num_time, 1)
            return
        
        rule = "([0-2]?[0-9])(点)"
        rule_com = re.compile(rule)
        match = rule_com.search(self.num_time)
        if match != None:
            self.gut.hour = match.group()
            self.num_time = rule_com.sub('', self.num_time, 1)
        
    def origin_minute(self):
        # 获取分钟相关的原始数据
        rule = "(([0-6]?[0-9])(刻点|分)(之后|以后|后))|(过([0-6]?[0-9])(刻点|分))"
        rule_com = re.compile(rule)
        match = rule_com.search(self.num_time)
        if match != None:
            self.gut.minute = match.group()
            self.num_time = rule_com.sub('', self.num_time, 1)
            return
            
        rule = "([0-6]?[0-9])(刻点|分|刻)"
        rule_com = re.compile(rule)
        match = rule_com.search(self.num_time)
        if match != None:
            self.gut.minute = match.group()


if __name__ == '__main__':
    ex_time = Extract_Time()
    ext_time = ex_time.extract("明天")
    if ext_time:
        print(ext_time[0].origin_time)
        print(ext_time[0].norm_time)
    ext_time = ex_time.extract("上午")
    if ext_time:
        print(ext_time[0].origin_time)
        print(ext_time[0].norm_time)
    ext_time = ex_time.extract("十点钟")
    if ext_time:
        print(ext_time[0].origin_time)
        print(ext_time[0].norm_time)
    ext_time = ex_time.extract("四点钟")
    if ext_time:
        print(ext_time[0].origin_time)
        print(ext_time[0].norm_time)
    
    num_time = ex_time.cn2num("二零二二年八月十七号下午三点三十分")
    print(num_time)
    gut = Get_User_Time()
    gut.norm_time = "2022-08-29 08:00:00"
    print(gut.is_past_time())
    gut.norm_time = "2022-08-30 08:00:00;2022-08-28 08:00:00"
    print(gut.is_wrong_week())

