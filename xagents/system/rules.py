#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
@Time    : 2024/6/14 18:28
@Author  : Mingxian Gu
@File    : rules
"""
import yaml

from .const import PROJECT_ROOT
from .logs import logger
from .utils.singleton import Singleton


class NotConfiguredException(Exception):
    """Exception raised for errors in the configuration.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="The required rules is not set"):
        self.message = message
        super().__init__(self.message)


class Rules(metaclass=Singleton):
    default_yaml_file = PROJECT_ROOT / "config/rules.yaml"

    def __init__(self, yaml_file=default_yaml_file):
        with open(yaml_file, "r", encoding="utf-8") as f:
            yaml_data = yaml.safe_load(f)
        if yaml_data is None:
            self.rules_temperature = {}
            self.rules = {}
        else:
            self.rules_temperature = {k.lower(): v for k, v in yaml_data.items()}
            self.rules = list(yaml_data.keys())
        logger.info(f"Loaded Rules: {self.rules_temperature}")
        logger.info("Rules loading done.")


RULES = Rules()
