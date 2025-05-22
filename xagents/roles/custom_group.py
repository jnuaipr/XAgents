#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
@Time    : 2024/4/18 15:21          
@Author  : Mingxian Gu
@File    : custom_group
"""
import re
import json
import time
from xagents.roles import Role, ExpertGroup
from xagents.system.logs import logger
from xagents.system.schema import Message
from xagents.actions import Requirement, AnalyzeTask, CalculateSimilarity, CustomAction
from xagents.system.rules import RULES
# from tasks.logs import tasklogger

SELECTED_VALUES = ["medium", "high"]


class CustomGroup(Role):
    def __init__(self, role, task, question_or_task, information, is_final, num_fields=3,
                 name="CustomGroup", profile="CustomGroup", goal="Effectively delivering information within a task",
                 constraints="", **kwargs):
        super().__init__(name, profile, goal, constraints, **kwargs)

        self.role = role
        self.task = task
        self.question_or_task = question_or_task
        self.information = information
        self.is_final = is_final
        self.num_fields = num_fields

        self._watch([Requirement])
        self._init_actions([CustomAction])

        self._analyze = AnalyzeTask()
        self._calculate = CalculateSimilarity()

        self.previous_results = ''
        self.knowledge = ''

    async def _react(self) -> Message:
        """先获取知识，然后再做"""
        logger.info(f"{self._setting}: ready to analyze")
        self._analyze.set_prefix(self._get_prefix(), self.profile, self._proxy, self._llm_api_key,
                                 self._serpapi_api_key)
        response = await self._analyze.run(task=self.task, previous_result=self.previous_results,
                                           information=self.information, question_or_task=self.question_or_task)
        if 'no question' in response.content.lower():
            logger.info(f"{self._setting}: do not need any Knowledge")
        else:
            question = response.instruct_content.Question.strip().strip('-').strip()
            # tasklogger.execution(f'## Question: {question}\n')
            logger.info(f"{self._setting}: need knowledge on this question: {question}")
            await self._expert_group(question=question)
        return await self._act()

    async def _expert_group(self, question=''):
        """专家组获取知识"""
        self._calculate.set_prefix(self._get_prefix(), self.profile, self._proxy, self._llm_api_key,
                                   self._serpapi_api_key)
        response = await self._calculate.run(question=question)
        weights_context = re.findall('## Selected Fields:([\s\S]*?)##', response.content + "##")[-1].strip().strip('-').strip()
        weights = weights_context.split('\n')
        weights_args = []
        current_num_fields = 0
        for weight in weights:
            if current_num_fields == self.num_fields:
                break
            if ':' in weight:
                weight_args = weight.split(':')
                weight_args = [s.strip() for s in weight_args]
                field = weight_args[0]
                weight = weight_args[1]
                if field.lower() in list(RULES.rules_temperature.keys()) and weight.lower() in SELECTED_VALUES:
                    weights_args.append(
                        {'field': field, 'weight': weight, 'temperature': RULES.rules_temperature[field.lower()]})
                    current_num_fields += 1
        if current_num_fields == 0:
            knowledge = ""
        else:
            role = ExpertGroup(question=question, weights_args=weights_args,
                               proxy=self._proxy, serpapi_api_key=self._serpapi_api_key, llm_api_key=self._llm_api_key)
            role.set_env(self._rc.env)
            response = await role.run()
            knowledge = response.instruct_content.Answer.strip().strip('-').strip()
            # tasklogger.execution(f'## Knowledge: {knowledge}\n')
        self.knowledge = knowledge

    async def _act(self) -> Message:
        self._set_state(0)
        logger.info(f"{self._setting}: ready to {self._rc.todo}")
        response = await self._rc.todo.run(role=self.role, task=self.task, previous=self.previous_results,
                                           is_final=self.is_final, existing_knowledge=self.knowledge,
                                           information=self.information, question_or_task=self.question_or_task)

        msg = Message(content=response.content, instruct_content=response.instruct_content,
                      role=self.profile, cause_by=type(self._rc.todo))

        self._rc.memory.add(msg)

        return msg

    async def run(self, previous_results='', message=None):
        self.previous_results = previous_results
        rsp = await self._react()
        await self._publish_message(rsp)
        return rsp