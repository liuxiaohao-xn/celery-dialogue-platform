from src.common.component.component_container import ComponentContainer
from src.common.domain.parser_domain import ParsedDomain
from src.common.data_mapping import Mapping
import os
import logging
"""应用启动预加载区"""
cur_dir = os.path.dirname(__file__)
# 加载注册组件
ComponentContainer.load_register_component(os.path.join(cur_dir, r"../resource/components.yml"))
# 加载domain
parsed_domain = ParsedDomain(os.path.join(cur_dir, r"../resource"))
# 加载domain_map
domain_map = Mapping(os.path.join(cur_dir, r"../resource/sec_domain_map.json"))
# 日志配置
log_dir = os.path.join(cur_dir, r"../log")
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
log_path = os.path.join(log_dir, 'log.txt')
if not os.path.exists(log_path):
    with open(log_path, 'w'):
        ...
logging.basicConfig(
    filename=os.path.join(cur_dir, r"../log/log.txt"),
    level=logging.DEBUG,
    filemode='a',
    format='[%(asctime)s] [%(levelname)s] >>>  %(message)s',
    datefmt='%Y-%m-%d %I:%M:%S'
)

