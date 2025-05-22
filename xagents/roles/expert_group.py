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
from xagents.actions import Requirement, AcquireKnowledge, FusionKnowledge
# from tasks.logs import tasklogger


class ExpertGroup(Role):
    def __init__(self, question, weights_args, name="ExpertGroup", profile="ExpertGroup",
                 goal="Effectively delivering knowledge in a question", constraints="", **kwargs):
        super().__init__(name, profile, goal, constraints, **kwargs)

        self._watch([Requirement])
        self.question = question

        self.fields = [item['field'] for item in weights_args]
        self.weights = [item['weight'] for item in weights_args]
        self.temperature = [item['temperature'] for item in weights_args]

        init_actions = []
        # print('---------------Question Group---------------')
        for i in range(len(self.fields)):
            # print('Add a new role:', self.fields[i])
            class_name = self.fields[i].replace(' ', '_') + '_Action'
            action_object = type(class_name, (AcquireKnowledge,),
                                 {"question": self.question,
                                  "field": self.fields[i],
                                  "temperature": self.temperature[i]})
            init_actions.append(action_object)
        init_actions.append(FusionKnowledge)
        self._init_actions(init_actions)
        self.action_len = len(init_actions)

    async def _act(self) -> Message:
        fusion_log = {}
        fusion_log['question'] = self.question
        log = ''
        answers_weight = ''
        answer = []
        for i in range(self.action_len - 1):
            self._set_state(i)
            logger.info(f"{self._setting}: ready to {self._rc.todo}")
            response = await self._rc.todo.run()
            answers_weight += f'## Weight: {self.weights[i]}\n{response.instruct_content.Answer.strip().strip("-").strip()}\n'
            log += f'### Field: {self.fields[i]} {self.weights[i]}\n{response.instruct_content.Answer.strip().strip("-").strip()}\n'
            answer.append({'field': self.fields[i],
                           'weight': self.weights[i],
                           'temperature': self.temperature[i],
                           'answer': response.instruct_content.Answer.strip().strip("-").strip()})
        fusion_log['answer'] = answer
        # tasklogger.execution(log)
        self._set_state(self.action_len - 1)
        logger.info(f"{self._setting}: ready to {self._rc.todo}")
        response = await self._rc.todo.run(question=self.question, answers_weight=answers_weight)
        fusion_log['output'] = response.instruct_content.Answer.strip().strip("-").strip()
        # tasklogger.fusion(fusion_log)
        msg = Message(content=response.content, instruct_content=response.instruct_content,
                      role=self.profile, cause_by=type(self._rc.todo))

        self._rc.memory.add(msg)

        return msg

    async def run(self, message=None):
        rsp = await self._act()
        await self._publish_message(rsp)
        return rsp
