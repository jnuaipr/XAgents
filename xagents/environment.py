#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/5/11 22:12
@Author  : alexanderwu
@File    : environment.py
@Modified From: https://github.com/geekan/MetaGPT/blob/main/metagpt/environment.py
"""
import asyncio
import os
import re
import json
import time
import networkx as nx

from typing import Iterable
from pydantic import BaseModel, Field
from matplotlib import pyplot as plt

from .roles import Role, CustomGroup
from .roles.manager import Manager
from .system.memory import Memory
from .system.schema import Message
# from tasks.logs import tasklogger


SLEEP_RATE = 5


class Environment(BaseModel):
    """环境，承载一批角色，角色可以向环境发布消息，可以被其他角色观察到"""

    workspace: str = Field(default='')

    roles: dict[str, Role] = Field(default_factory=dict)
    groups: dict[str, Role] = Field(default_factory=dict)

    graph: nx.DiGraph = Field(default_factory=nx.DiGraph)

    question_or_task: str = Field(default='')
    information: str = Field(default='')
    previous_result: list = Field(default_factory=list)
    result: str = Field(default='')

    memory: Memory = Field(default_factory=Memory)
    history: str = Field(default='')
    task_id: str = Field(default='')
    proxy: str = Field(default='')
    llm_api_key: str = Field(default='')
    serpapi_key: str = Field(default='')
    alg_msg_queue: object = Field(default=None)

    class Config:
        arbitrary_types_allowed = True

    def add_role(self, role: Role):
        """在当前环境增加一个Manger Role"""
        role.set_env(self)
        self.roles[role.profile] = role

    def add_roles(self, roles: Iterable[Role]):
        """在当前环境增加一批Manger Role"""
        for role in roles:
            self.add_role(role)

    def add_group(self, role: Role):
        """在当前环境增加一个Group"""
        role.set_env(self)
        self.groups[role.name] = role

    def add_groups(self, roles: Iterable[Role]):
        """在当前环境增加一批Knowledge Role"""
        for role in roles:
            self.add_group(role)

    @staticmethod
    def _parser_plans(content):
        """解析子任务"""
        plans = re.findall('## Subtasks:([\s\S]*?)##', content + "##")[0].strip().split("\n")
        plans_args = []
        for plan in plans:
            plan = plan.strip()
            if re.match(r"^\d+\.", plan):
                pattern = re.compile(r'^(\d+)\.\s*(.*)')
                match = pattern.match(plan)
                number = int(match.group(1).strip())
                task = str(match.group(2).strip())
                plans_args.append({'number': number, 'task': task})
        return plans_args

    @staticmethod
    def _parser_information(content):
        """解析信息"""
        information = re.findall('## Information:([\s\S]*?)##', content + "##")[0].strip()
        return information

    @staticmethod
    def _parser_graph(content):
        """解析任务输入"""
        graph = re.findall('## Predecessor Steps:([\s\S]*?)##', content + "##")[0]
        graph = re.findall('{[\s\S]*?}', str(graph))
        graph_args = []
        for inputs in graph:
            inputs = json.loads(inputs.strip())
            if len(inputs.keys()) > 0:
                graph_args.append(inputs)
        return graph_args

    @staticmethod
    def _parser_roles(content):
        """解析专家角色"""
        roles = ''.join(re.findall('## Roles List:([\s\S]*?)##', content + "##"))
        roles = re.findall('{[\s\S]*?}', str(roles))
        roles_args = []
        for role in roles:
            role = json.loads(role.strip())
            if len(role.keys()) > 0:
                roles_args.append(role)
        return roles_args

    def create_graph(self, plans_args: list, roles_args: list, graph_args: list):
        dg = nx.DiGraph()

        for plan_args in plans_args:
            node = plan_args['number']
            dg.add_node(node)
            dg.nodes[node]['task'] = plan_args['task']

        for graph_arg in graph_args:
            if '' == graph_arg['inputs']:
                continue
            else:
                edges = []
                if ',' in graph_arg['inputs']:
                    inputs_list = [item.strip() for item in graph_arg['inputs'].split(',')]
                else:
                    inputs_list = [graph_arg['inputs'].strip()]
                for input_list in inputs_list:
                    edges.append((int(re.findall(r'\d+', input_list)[0]), int(re.findall(r'\d+', graph_arg['number'])[0])))
                    dg.add_edges_from(edges)
        for role_args in roles_args:
            node = int(role_args['number'])
            dg.nodes[node]['name'] = role_args['name']
            dg.nodes[node]['tools'] = role_args['tools']
            dg.nodes[node]['prompt'] = role_args['prompt']

        final_node = int(plans_args[-1]['number'])
        for i in range(1, final_node + 1):
            if 'task' not in dg.nodes[i]:
                dg.remove_node(i)
                continue
            if 'name' not in dg.nodes[i]:
                dg.nodes[i]['name'] = 'Executor_' + str(i)
            if 'tools' not in dg.nodes[i]:
                dg.nodes[i]['tools'] = '[None]'
            if 'prompt' not in dg.nodes[i]:
                dg.nodes[i]['prompt'] = 'You are a task executor. Your goal is to complete the following tasks as well as possible.'
            if i != final_node:
                if not any(True for _ in dg.successors(i)):
                    dg.add_edge(i, final_node)
        # nx.draw(dg, with_labels=True, font_weight='bold')
        # plt.show()
        self.graph = dg
        self.previous_result = ['' for _ in range(len(self.graph.nodes())+1)]
        # tasklogger.graph(nx.node_link_data(self.graph))

    async def publish_message(self, message: Message):
        """向当前环境发布信息"""
        self.memory.add(message)
        self.history += f"\n{message}"

        if 'Question/Task' in message.role:
            self.question_or_task = message.content

        if 'Manager' in message.role:
            plans_args = self._parser_plans(message.content)
            graph_args = self._parser_graph(message.content)
            roles_args = self._parser_roles(message.content)
            self.create_graph(plans_args=plans_args, roles_args=roles_args, graph_args=graph_args)
            self.information = self._parser_information(message.content)

    async def run(self):
        """处理一次所有Role的运行"""
        # tasklogger.set_workspace(workspace=self.workspace)

        self.add_role(Manager(proxy=self.proxy, llm_api_key=self.llm_api_key, serpapi_api_key=self.serpapi_key))
        await self.roles['Manager'].run()

        predecessors = []
        for i in range(len(self.graph.nodes())):
            predecessors.append(list(self.graph.predecessors(i + 1)))
        top_order = list(nx.topological_sort(self.graph))

        for i, task_number in enumerate(top_order):

            if i == len(self.graph.nodes()) - 1:
                is_final = True
            else:
                is_final = False

            name = f'Group_Task_{task_number}'
            group = CustomGroup(
                role=self.graph.nodes[task_number]['prompt'],
                task=self.graph.nodes[task_number]['task'],
                question_or_task=self.question_or_task,
                information=self.information,
                is_final=is_final,
                name=name
            )
            group.set_env(self)
            previous = ''
            predecessor = predecessors[task_number - 1]
            if len(predecessor) != 0:
                for pre in predecessor:
                    previous += "## Task: " + self.graph.nodes[pre]['task']
                    previous += '\n'
                    previous += self.previous_result[pre]
                    previous += '\n'
            # tasklogger.execution(f"# Task {task_number}: {self.graph.nodes[task_number]['task']}\n")
            response = await group.run(previous_results=previous)
            self.previous_result[task_number] = response.instruct_content.Answer.strip().strip('-').strip()
            # tasklogger.execution(f"## Answer\n{self.previous_result[task_number]}\n\n")
            if i == len(self.graph.nodes()) - 1:
                self.result = re.findall('## Answer:([\s\S]*?)##', response.content + "##")[0].strip().strip('-').strip()
            time.sleep(SLEEP_RATE)
        # tasklogger.history(self.history)

    def get_roles(self) -> dict[str, Role]:
        """获得环境内的所有Role"""
        return self.roles

    def get_role(self, name: str) -> Role:
        """获得环境内的指定Role"""
        return self.roles.get(name, None)
