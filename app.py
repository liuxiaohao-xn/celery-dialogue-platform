# -*- coding: utf-8 -*-
# @Time : 2022/6/23 14:12
# @Author : liuxiaohao
# @Email : liuxh4@infore.com
# @File : app.py
from flask import Flask
from src.main_discard import bp

app = Flask(__name__)
app.register_blueprint(bp)

if __name__ == "__main__":
    app.run(host="localhost", port=5010)
