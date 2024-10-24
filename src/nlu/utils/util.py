from threading import Thread, Timer
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

