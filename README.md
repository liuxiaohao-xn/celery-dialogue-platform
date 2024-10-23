# celery-dialogue-platform
celery-dialogue-platform是一个任务型多轮对话平台，适用于人机交互场景，可让您根据自身业务快速构建高效的对话应用。

## 特性
1. 平台架构遵循NLU(意图识别、槽位提取)->DM(DST、DP、Action)->NLG的pipeline模式；
2. DST本质用的FSM算法，各个对话状态之间通过意图或条件进行激活和跳转；
3. 业务对话流程基于yaml文件格式动态配置开发；
4. 组件之间高度解耦，各个组件用到的模型均可根据业务动态配置，如nlu可用规则模型、分类模型、或者LLM等；
5. 提供grpc api，可快速和业务端进行集成。


## 快速开发

下面以如何快速开发包含如 预定会议、倒水、打电话 3个技能场景的对话系统

### [对话配置](./resource)

1. 技能配置(domain.yaml)

配置技能包括的意图和pipeline需要用到的模型等。

2. 对话流程配置(intent.yaml)

配置每个意图的对话流程及对应的action、槽位、默认response等。

3. 实体配置(entity.yaml)

配置动、静态实体、实体源检验等。

### [模型配置](./src/common/component/component.py)

不同的业务场景可能会用到不同的模型，同一个业务场景也可能会进行模型的迭代和升级，而算法人员开发的模型各异，为了进行快速集成和迭代，我们统一模型集成到平台的实现方式。

1. 为了统一不同组件相同处理流程，算法人员需要实现Component接口中的三个方法；

2. 为了统一不同模型的输入输出，方便平台统一处理，如槽位提取模型算法、还需要实现平台定义好的./src/nlu/extractors/exactor/Extractor.build_res方法来获取模型结果。

### [Action配置](.src/dm/action.py)

action主要用于用户对平台结果进行二次决策，包括意图、槽位实体的校验和修改、rsp的选择、外部接口的调用等。

用户可以根据自己的业务流程来动态定义自己的action。

### 启动

直接启动
```shell
python3 grpc_server.py 
```
or

部署成docker镜像，下面是对应的Dockerfile文件配置
```shell
# vim Dockerfile
FROM hub.infore-robotics.cn/service-robotics/yh-robot-nlp-base:1.0.0
WORKDIR /app

COPY resource /app/resource
COPY src /app/src
COPY lib/libgomp.so.1 /usr/lib/x86_64-linux-gnu/libgomp.so.1
COPY lib/libgomp.so.1.0.0 /usr/lib/x86_64-linux-gnu/libgomp.so.1.0.0
COPY grpc_client.py /app/grpc_client.py
COPY grpc_server.py /app/grpc_server.py
COPY app.py /app/app.py

ENTRYPOINT ["/usr/local/python39/bin/python3.9","grpc_server.py"]
```


### 运行效果日志

```text
##### 新会话 #####
[2024-06-20 02:14:02] [INFO] >>>  asr: 帮忙定个会议
[2024-06-20 02:14:02] [INFO] >>>  exd_info: {'skill_name': 'meeting', 'intent_id': 'YHI_HOLD_MEETING', 'intent_name': 'hold_meeting', 'exd_slot': []}
[2024-06-20 02:14:02] [INFO] >>>  tts: 好的，您需要定几点的会议呢？
[2024-06-20 02:14:26] [INFO] >>>  asr: 定在下午三点，叫张三来参加
[2024-06-20 02:14:26] [INFO] >>>  exd_info: {'skill_name': None, 'intent_id': 'YHI_HOLD_MEETING', 'intent_name': 'hold_meeting', 'exd_slot': [{'name': 'attendee', 'value': '张三', 'normal_value': '张三', 'optional': False}, {'name': 'meeting_time', 'value': '2024-06-20 15:00:00', 'normal_value': '2024-06-20 15:00:00', 'optional': False}]}
[2024-06-20 02:14:26] [INFO] >>>  tts: 收到，请问还有其他参会人员吗？
[2024-06-20 02:14:34] [INFO] >>>  asr: 没有了
[2024-06-20 02:14:34] [INFO] >>>  exd_info: {'skill_name': 'system', 'intent_id': 'YHI_HOLD_MEETING', 'intent_name': 'hold_meeting', 'exd_slot': [{'name': 'attendee', 'value': '张三', 'normal_value': '张三', 'optional': False}, {'name': 'meeting_time', 'value': '2024-06-20 15:00:00', 'normal_value': '2024-06-20 15:00:00', 'optional': False}]}
[2024-06-20 02:14:34] [INFO] >>>  tts: 好的, 您的会议预定成功. 会议时间: 二零二四年六月二十日 下午三点.邀请的参会人员: 张三.请记得准时参加 .
[2024-06-20 02:14:54] [INFO] >>>  
##### 新会话 #####
[2024-06-20 02:14:54] [INFO] >>>  asr: 下午三点开会
[2024-06-20 02:14:54] [INFO] >>>  exd_info: {'skill_name': 'meeting', 'intent_id': 'YHI_HOLD_MEETING', 'intent_name': 'hold_meeting', 'exd_slot': [{'name': 'meeting_time', 'value': '2024-06-20 15:00:00', 'normal_value': '2024-06-20 15:00:00', 'optional': False}]}
[2024-06-20 02:14:54] [INFO] >>>  tts: 收到，通知哪些人员参会呢？
[2024-06-20 02:15:20] [INFO] >>>  asr: 下午两点叫张三开会
[2024-06-20 02:15:20] [INFO] >>>  exd_info: {'skill_name': 'meeting', 'intent_id': 'YHI_HOLD_MEETING', 'intent_name': 'hold_meeting', 'exd_slot': [{'name': 'attendee', 'value': '张三', 'normal_value': '张三', 'optional': False}, {'name': 'meeting_time', 'value': '2024-06-20 15:00:00', 'normal_value': '2024-06-20 15:00:00', 'optional': False}, {'name': 'meeting_time', 'value': '2024-06-20 14:00:00', 'normal_value': 'None', 'optional': False}]}
[2024-06-20 02:15:20] [INFO] >>>  tts: 收到，请问还有其他参会人员吗？
[2024-06-20 02:15:30] [INFO] >>>  asr: 没有了
[2024-06-20 02:15:30] [INFO] >>>  exd_info: {'skill_name': 'system', 'intent_id': 'YHI_HOLD_MEETING', 'intent_name': 'hold_meeting', 'exd_slot': [{'name': 'attendee', 'value': '张三', 'normal_value': '张三', 'optional': False}, {'name': 'meeting_time', 'value': '2024-06-20 15:00:00', 'normal_value': '2024-06-20 15:00:00', 'optional': False}, {'name': 'meeting_time', 'value': '2024-06-20 14:00:00', 'normal_value': 'None', 'optional': False}]}
[2024-06-20 02:15:30] [INFO] >>>  tts: 好的, 您的会议预定成功. 会议时间: 二零二四年六月二十日 下午三点.邀请的参会人员: 张三.请记得准时参加 .

```