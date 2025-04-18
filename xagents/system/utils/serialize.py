#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Desc   : the implement of serialization and deserialization
# @From   : https://github.com/geekan/MetaGPT/blob/main/metagpt/utils/serialize.py

import copy
from typing import Tuple, List, Type, Union, Dict
import pickle
from collections import defaultdict
from pydantic import create_model

from xagents.system.schema import Message
from xagents.actions.action import Action, ActionOutput


def actionoutout_schema_to_mapping(schema: Dict) -> Dict:
    """
    directly traverse the `properties` in the first level.
    schema structure likes
    ```
    {
        "title":"prd",
        "type":"object",
        "properties":{
            "Original Requirements":{
                "title":"Original Requirements",
                "type":"string"
            },
        },
        "required":[
            "Original Requirements",
        ]
    }
    ```
    """
    mapping = dict()
    for field, property in schema['properties'].items():
        if property['type'] == 'string':
            mapping[field] = (str, ...)
        elif property['type'] == 'array' and property['items']['type'] == 'string':
            mapping[field] = (List[str], ...)
        elif property['type'] == 'array' and property['items']['type'] == 'array':
            # here only consider the `Tuple[str, str]` situation
            mapping[field] = (List[Tuple[str, str]], ...)
    return mapping


def serialize_message(message: Message):
    message_cp = copy.deepcopy(message)  # avoid `instruct_content` value update by reference
    ic = message_cp.instruct_content
    if ic:
        # model create by pydantic create_model like `pydantic.main.prd`, can't pickle.dump directly
        schema = ic.schema()
        mapping = actionoutout_schema_to_mapping(schema)

        message_cp.instruct_content = {
            'class': schema['title'],
            'mapping': mapping,
            'value': ic.dict()
        }
    msg_ser = pickle.dumps(message_cp)

    return msg_ser


def deserialize_message(message_ser: str) -> Message:
    message = pickle.loads(message_ser)
    if message.instruct_content:
        ic = message.instruct_content
        ic_obj = ActionOutput.create_model_class(class_name=ic['class'],
                                                 mapping=ic['mapping'])
        ic_new = ic_obj(**ic['value'])
        message.instruct_content = ic_new

    return message
