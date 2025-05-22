#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/6/1 12:41
@Author  : alexanderwu
@File    : log.py
@From    : https://github.com/geekan/MetaGPT/blob/main/metagpt/logs.py
"""
import sys
from loguru import logger as _logger
from .const import PROJECT_ROOT


def define_log_level(print_level="INFO", logfile_level="INFO"):
    _logger.remove()
    _logger.add(sys.stderr, level=print_level)
    _logger.add(PROJECT_ROOT / 'logs/log.txt', level=logfile_level)
    return _logger


logger = define_log_level()
