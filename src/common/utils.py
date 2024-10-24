# -*- coding: utf-8 -*-
# @Time : 2022/6/8 13:55
# @Author : liuxiaohao
# @Email : liuxh4@infore.com
# @File : utils.py
import time
import re
from typing import Any, Dict, List, Optional, Text, Type, Union
from pathlib import Path
from ruamel import yaml
import os
from src.common.grpc.grpc_req import Request


def _is_ascii(text: Text) -> bool:
    return all(ord(character) < 128 for character in text)


def read_file(filename: Union[Text, Path], encoding: Text = "utf-8") -> Any:
    """读取文件"""
    try:
        with open(filename, encoding=encoding) as f:
            return f.read()
    except Exception:
        raise FileNotFoundError(
            f"读取文件失败, " f"'{os.path.abspath(filename)}' 不存在."
        )
    except Exception:
        raise UnicodeDecodeError(
            f"读取文件失败 '{os.path.abspath(filename)}', "
            f"{encoding} 格式解码文件失败"
            f"请确认文件是使用 {encoding} 格式存储的. "
        )


def read_yaml_file(filename: Union[Text, Path]) -> Dict[Text, Any]:
    """解析一个YML文件."""
    try:
        return read_yaml(read_file(filename, "utf-8"))
    except FileExistsError as e:
        raise FileNotFoundError(filename, e)


def read_yaml(content: Text, reader_type: Union[Text, List[Text]] = "safe") -> Any:
    if _is_ascii(content):
        # Required to make sure emojis are correctly parsed
        content = (
            content.encode("utf-8")
                .decode("raw_unicode_escape")
                .encode("utf-16", "surrogatepass")
                .decode("utf-16")
        )

    yaml_parser = yaml.YAML(typ=reader_type)
    yaml_parser.preserve_quotes = True

    return yaml_parser.load(content) or {}


def make_tmp_o(name: Text) -> object:
    return type(name, (object,), {})


def check_cls_type(checked_cls, belong_cls) -> bool:
    res = issubclass(checked_cls, belong_cls)
    return True if res else False


def singleton(cls, *args, **kw):
    instances = {}

    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]

    return _singleton


def get_auth_id(request: Request) -> Text:
    return request.device_info.device_sn + request.device_info.merchant_id


def build_session_id_by_auth_id(auth_id: Text) -> Text:
    """创建session_id"""
    return auth_id + str(get_cur_timestamp(1))


def get_cur_timestamp(level: int = 2) -> int:
    """
    获取当前时间戳
    Args:
        level：时间戳级别
            level=1, 秒级时间戳 10位
            level=2, 毫秒级时间戳 13位
            level=3, 微秒级时间戳 16位
    """
    t = time.time()
    if level == 1:
        return int(t)
    elif level == 2:
        return int(round(t * 1000))
    elif level == 3:
        return int(round(t * 1000000))
    else:
        raise Exception(f"获取时间戳出错, level={level}, level取值应在[1,2,3]中.")


def format_tts_text(tts_text: Text, format_str=" ") -> Text:
    """格式化tts文本"""
    import string
    from zhon.hanzi import punctuation
    for pun in string.punctuation:
        tts_text = tts_text.replace(pun, format_str)
    for pun in punctuation:
        tts_text = tts_text.replace(pun, format_str)
    return tts_text.strip()


def get_component_by_klass_name(klass_name: Text):
    """get component instantiate by component klass name"""
    from src.common.component.component_container import ComponentContainer
    return klass_instantiate(
        ComponentContainer.get_register_klass(
            klass_name
        )
    )


def klass_instantiate(klass):
    """组件实例化"""
    return klass.make_o(
        klass.get_default_config()
    )

def rm_whitespace(content: Text):
    return  re.sub(r"\s+", "", content)

if __name__ == "__main__":
    t1 = get_cur_timestamp()
    time.sleep(3)
    t2 = get_cur_timestamp()
    print(t2-t1)
