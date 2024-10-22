import pstats
from threading import Thread, Timer
from time import sleep
from typing import List, Text

class Singleton(object):
    def __init__(self, cls):
        self._cls = cls
        self._instance = {}

    def __call__(self):
        if self._cls not in self._instance:
            self._instance[self._cls] = self._cls()
        return self._instance[self._cls]


class Scheduler(object):
    def __init__(self, sleep_time, function):
        self.sleep_time = sleep_time
        self.function = function
        self._t = None

    def start(self):
        if self._t is None:
            self._t = Timer(self.sleep_time, self._run)
            self._t.start()
        else:
            raise Exception("this timer is already running")

    def _run(self):
        self.function()
        self._t = Timer(self.sleep_time, self._run)
        self._t.start()

    def stop(self):
        if self._t is not None:
            self._t.cancel()
            self._t = None

def get_prefix(s1, s2):
    #获取两个字符串的前缀
    i = 0
    length = min(len(s1), len(s2))
    while i < length and s1[i] == s2[i]:
        i += 1
    return i

def longest_common_prefix(pinyin_org: Text, pinyin_rec: List) -> List[int]:
    # 求拼音的最长公共前缀
    # pinyin_org-原始拼音，pinyin_rec-召回的拼音列表 return list index of pinyin
    max_prefix_index, max_prefix = [], 0
    pin_org = pinyin_org.split(' ')
    for index, pin in enumerate(pinyin_rec):
        pin_rec = pin.split(' ')
        add_prefix = 0
        for i in range(len(pin_rec)):
            # print(i, pin_org, pin_rec)
            len_prefix = get_prefix(pin_org[i], pin_rec[i])
            if len_prefix == 0:  # 如果声母不一样，直接排除
                add_prefix = -1
                break
            add_prefix += len_prefix

        if add_prefix > max_prefix:
            max_prefix = add_prefix
            max_prefix_index = [index]
        elif add_prefix == max_prefix:
            max_prefix_index.append(index)
    # if not max_prefix_index:
    #     raise Exception(f"max_prefix_index={max_prefix_index}")
    return max_prefix_index


def calNext(str2):
    i=0
    next=[-1]
    j=-1
    while(i<len(str2)-1):
        if(j==-1 or str2[i]==str2[j]):
            #首次分析可忽略
            i+=1
            j+=1
            next.append(j)
        else:
            j=next[j] #会重新进入上面那个循环
    return next

def KMP(s1,s2,pos=0):
    #从那个位置开始比较
    next=calNext(s2)
    i=pos
    j=0
    while(i<len(s1) and j<len(s2)):
        if(j==-1 or s1[i]==s2[j]):
            i+=1
            j+=1
        else:
            j=next[j]
    if(j>=len(s2)):
        return i -len(s2) #说明匹配到最后了
    else:
        return -1

