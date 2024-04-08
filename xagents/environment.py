#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/5/11 22:12
@Author  : alexanderwu
@File    : environment.py
@Modified From: https://github.com/geekan/MetaGPT/blob/main/metagpt/environment.py
"""
import asyncio
import re
import json

from typing import Iterable

from pydantic import BaseModel, Field

from .roles import Role
from .roles import KnowledgeGroup, ExecutionGroup

from .system.memory import Memory
from .system.schema import Message


class Environment(BaseModel):
    """环境，承载一批角色，角色可以向环境发布消息，可以被其他角色观察到"""

    roles: dict[str, Role] = Field(default_factory=dict)
    knowledge_roles: dict[str, Role] = Field(default_factory=dict)
    execution_roles: dict[str, Role] = Field(default_factory=dict)
    execution_plans: list = Field(default_factory=list)
    sub_problems: list = Field(default=[])
    knowledge: str = Field(default='')
    execution_roles_args: list = Field(default_factory=list)

    question_or_task: str = Field(default_factory=str)
    result: str = Field(default='')

    memory: Memory = Field(default_factory=Memory)
    history: str = Field(default='')
    msg_json: list = Field(default_factory=list)
    json_log: str = Field(default='./logs/json_log.json')
    task_id: str = Field(default='')
    proxy: str = Field(default='')
    llm_api_key: str = Field(default='')
    serpapi_key: str = Field(default='')
    alg_msg_queue: object = Field(default=None)
    previous_results: list = Field(default=[])

    class Config:
        arbitrary_types_allowed = True

    def add_role(self, role: Role):
        """增加一个在当前环境的Role"""
        role.set_env(self)
        self.roles[role.profile] = role

    def add_roles(self, roles: Iterable[Role]):
        """增加一批在当前环境的Role"""
        for role in roles:
            self.add_role(role)

    def add_knowledge_role(self, role: Role):
        """在当前环境增加一个Knowledge Role"""
        role.set_env(self)
        self.knowledge_roles[role.profile] = role

    def add_knowledge_roles(self, roles: Iterable[Role]):
        """在当前环境增加一批Knowledge Role"""
        for role in roles:
            self.add_knowledge_role(role)

    def add_execution_role(self, role: Role):
        """在当前环境增加一个Execution Role"""
        role.set_env(self)
        self.execution_roles[role.profile] = role

    def add_execution_roles(self, roles: Iterable[Role]):
        """在当前环境增加一批Execution Role"""
        for role in roles:
            self.add_execution_role(role)

    @staticmethod
    def _parser_question_or_task(context):
        """解析人类的问题/任务"""
        question_or_task = re.findall('## Question or Task([\s\S]*?)##', str(context))[0]
        return question_or_task

    @staticmethod
    def _parser_problems(context):
        """解析子问题和知识型专家参数"""
        context = re.findall('## Sub-problem Similarity([\s\S]*?)##', str(context))[0]
        problems = re.findall('{[\s\S]*?}', str(context))
        problems_args = []
        for problem in problems:
            problem = json.loads(problem.strip())
            if len(problem.keys()) > 0:
                problems_args.append(problem)
        print('---------------Sub-problems---------------')
        for i, problem in enumerate(problems_args):
            print('Sub-problem', i, problem)
        return problems_args

    @staticmethod
    def _parser_plans(context):
        """解析生成的执行计划"""
        context = re.findall('## Execution Plan([\s\S]*?)##', str(context))[0]
        execution_plans = [v.split("\n")[0] for v in re.split("\n\d+\. ", context)[1:]]
        print('---------------Execution Plans---------------')
        for i, step in enumerate(execution_plans):
            print('Step', i, step)
        return execution_plans

    @staticmethod
    def _parser_execution_roles(context):
        """解析动作型专家参数"""
        context = re.findall('## Execution Expert Roles List([\s\S]*?)##', str(context))[0]
        execution_roles = re.findall('{[\s\S]*?}', context)
        execution_roles_args = []
        for execution_role in execution_roles:
            execution_role = json.loads(execution_role.strip())
            if len(execution_role.keys()) > 0:
                execution_roles_args.append(execution_role)
        print('---------------Execution Roles---------------')
        for i, execution_role in enumerate(execution_roles_args):
            print('Role', i, execution_role)
        return execution_roles_args

    def create_knowledge_roles(self, sub_problems: list):
        """创建Knowledge Roles"""
        knowledge_roles = []
        for i, sub_problem in enumerate(sub_problems):
            role = KnowledgeGroup(problem_arg=sub_problem, name=f'KnowledgeGroup{i}',
                                  profile=f'KnowledgeGroup{i}', proxy=self.proxy,
                                  serpapi_api_key=self.serpapi_key, llm_api_key=self.llm_api_key)
            knowledge_roles.append(role)
        self.add_knowledge_roles(knowledge_roles)

    def create_execution_roles(self):
        """创建Execution Roles"""
        self.add_execution_roles(
            [ExecutionGroup(existing_knowledge=self.knowledge, execution_plans=self.execution_plans,
                            roles=self.execution_roles_args,question_or_task=self.question_or_task)])

    async def publish_message(self, message: Message):
        """向当前环境发布信息"""
        # self.message_queue.put(message)
        self.memory.add(message)
        self.history += f"\n{message}"

        if 'Manager' in message.role:
            self.question_or_task = self._parser_question_or_task(message.content)
            self.sub_problems = self._parser_problems(message.content)
            self.create_knowledge_roles(self.sub_problems)
            self.execution_plans = self._parser_plans(message.content)
            self.execution_roles_args = self._parser_execution_roles(message.content)

        if 'KnowledgeGroup' in message.role:
            # self.knowledge += '## Problem: '
            # self.knowledge += re.findall('## Input Problem:\n([\s\S]*?)##', str(message.content))[0].strip()
            # self.knowledge += '\nAnswer: '
            self.knowledge += re.findall('## Final Answer:\n([\s\S]*?)##', str(message.content))[0].strip()
            self.knowledge += '\n'

        if 'ExecutionGroup' in message.role:
            self.result = re.findall('## Answer:\n([\s\S]*?)##', str(message.content+"##"))[0].strip()

    async def run(self, k=1):
        """处理一次所有Role的运行"""
        for _ in range(k):
            futures = []
            for key in self.roles.keys():
                role = self.roles[key]
                future = role.run()
                futures.append(future)

            await asyncio.gather(*futures)

        # if len(self.knowledge_roles) > 0:
        #     futures = []
        #     for key in self.knowledge_roles.keys():
        #         role = self.knowledge_roles[key]
        #         future = role.run()
        #         futures.append(future)
        #
        #     await asyncio.gather(*futures)
        for key in self.knowledge_roles.keys():
            role = self.knowledge_roles[key]
            await role.run()

        self.create_execution_roles()
        print('---------------Existing Knowledge---------------')
        print(self.knowledge)

        for key in self.execution_roles.keys():
            role = self.execution_roles[key]
            await role.run()

    def get_roles(self) -> dict[str, Role]:
        """获得环境内的所有Role"""
        return self.roles

    def get_role(self, name: str) -> Role:
        """获得环境内的指定Role"""
        return self.roles.get(name, None)
