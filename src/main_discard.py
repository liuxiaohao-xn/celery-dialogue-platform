# -*- coding: utf-8 -*-
# @Time : 2022/6/7 15:35
# @Author : liuxiaohao
# @Email : liuxh4@infore.com
# @File : main_discard.py
from typing import Text
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from src.common.message import SysMsg
from .dialogue_discard import dialogue
bp = Blueprint('yh_bot', __name__, url_prefix='/yh_bot')


@bp.route("/chat", methods=('GET', 'POST'))
def chat():
    auth_id: Text = request.form.get("auth_id")
    text: Text = request.form.get("text")
    msg = SysMsg(
        text=text,
        auth_id=auth_id
    )
    msg = dialogue(msg)
    return msg.rsp

