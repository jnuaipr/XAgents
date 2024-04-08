#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
@Time    : 2024/4/4 22:24          
@Author  : Mingxian Gu
@File    : knowledge_group
"""
import time

from xagents.roles import Role
from xagents.system.logs import logger
from xagents.system.schema import Message
from xagents.actions import Requirement, CustomKnowledgeAction, FusionAnswer, ActionOutput

SLEEP_RATE = 20


class KnowledgeGroup(Role):
    def __init__(self, problem_arg, name="KnowledgeGroup", profile="KnowledgeGroup",
                 goal="Effectively delivering knowledge.", constraints="", **kwargs):
        super().__init__(name, profile, goal, constraints, **kwargs)

        self._watch([Requirement])

        if ',' in problem_arg['fields']:
            fields = [item.strip() for item in problem_arg['fields'].split(',')]
            weights = [item.strip() for item in problem_arg['similarity'].split(',')]
        else:
            fields = [problem_arg['fields'].strip()]
            weights = [problem_arg['similarity'].strip()]

        self.problem = problem_arg['sub-problem']
        self.fields = fields
        self.weights = weights

        init_actions = []
        print(f'---------------Sub-problems {name}---------------')
        print('Sub-problem:', self.problem)
        for field in self.fields:
            print('Add a new role:', field)
            class_name = field.replace(' ', '_') + '_Action'
            action_object = type(class_name, (CustomKnowledgeAction,), {"problem": self.problem, "field": field})
            init_actions.append(action_object)
        init_actions.append(FusionAnswer)
        self._init_actions(init_actions)
        self.action_len = len(init_actions)

    async def _act(self) -> Message:
        answers_weight = ''
        for i in range(self.action_len - 1):
            self._set_state(i)
            logger.info(f"{self._setting}: ready to {self._rc.todo}")
            response = await self._rc.todo.run()
            answers_weight += f'## Weight: {self.weights[i]}\n{response.instruct_content.Answer.strip()}\n'
        self._set_state(self.action_len - 1)
        logger.info(f"{self._setting}: ready to {self._rc.todo}")
        response = await self._rc.todo.run(problem=self.problem, answers_weight=answers_weight)
        time.sleep(SLEEP_RATE)

        if isinstance(response, ActionOutput):
            msg = Message(content=response.content, instruct_content=response.instruct_content,
                          role=self.profile, cause_by=type(self._rc.todo))
        else:
            msg = Message(content=response.content, role=self.profile, cause_by=type(self._rc.todo))
        self._rc.memory.add(msg)

        return msg
