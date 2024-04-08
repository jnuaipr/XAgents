#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
@Time    : 2024/4/6 12:26          
@Author  : Mingxian Gu
@File    : execution_group
"""
import re
import time
from xagents.roles import Role
from xagents.system.logs import logger
from xagents.system.schema import Message
from xagents.actions import Requirement, CustomExecutionAction, ActionOutput

SLEEP_RATE = 20


class ExecutionGroup(Role):
    def __init__(self, existing_knowledge, execution_plans, roles, question_or_task, name="ExecutionGroup",
                 profile="ExecutionGroup", goal="Effectively delivering information.", constraints="", **kwargs):
        super().__init__(name, profile, goal, constraints, **kwargs)

        self._watch([Requirement])

        self.existing_knowledge = existing_knowledge
        self.execution_plans = execution_plans
        self.roles = roles
        self.question_or_task = question_or_task

        init_actions = []
        print('ExecutionGroup:')
        # for i, role in enumerate(self.roles):
        #     print('Add a new role:', role['name'])
        #     class_name = role['name'].replace(' ', '_') + f'_Action_{i}'
        #     action_object = type(class_name, (CustomExecutionAction,),
        #                          {"role_prompt": role['prompt'], "tools": role['tools'],
        #                           "question_or_task": self.question_or_task})
        #     init_actions.append(action_object)
        # if len(execution_plans) > len(init_actions):
        #     init_actions.append(type("Final_Answer", (CustomExecutionAction,),
        #                              {"role_prompt": "You are a linguist.",
        #                               "tools": "None", "question_or_task": self.question_or_task}))
        self._init_actions(init_actions)

    async def _act(self) -> Message:

        previous_result, response = '', ''
        for i in range(len(self.execution_plans)):
            self._set_state(i)
            logger.info(f"{self._setting}: ready to {self._rc.todo}")
            response = await self._rc.todo.run(step=self.execution_plans[i], previous_result=previous_result,
                                               existing_knowledge=self.existing_knowledge)
            # previous_result += f'## Step: {self.execution_plans[i]}\n' + response.instruct_content.Answer
            previous_result = response.instruct_content.Answer
            time.sleep(SLEEP_RATE)

        if isinstance(response, ActionOutput):
            msg = Message(content=response.content, instruct_content=response.instruct_content,
                          role=self.profile, cause_by=type(self._rc.todo))
        else:
            msg = Message(content=response.content, role=self.profile, cause_by=type(self._rc.todo))
        self._rc.memory.add(msg)

        return msg
