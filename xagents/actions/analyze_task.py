#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
@Time    : 2024/4/18 16:54          
@Author  : Mingxian Gu
@File    : analyze_task
"""
from xagents.actions import Action

PROMPT_TEMPLATE = '''
-----
You are a professional analyst with expertise in multiple fields. Your goal is to determine whether additional knowledge is required to complete the task.

# Task
{task}

# Previous Result
{previous_result}

# Information
{information}

# Steps
You will come up with solutions for any question or task by following these steps:
1. You should first understand and analyze the task, the previous result and the information.
2. According to the task, the previous result and the information, you will determine whether additional knowledge is required to complete the task.
2.1. If the task can not be accomplished relying solely on previous results and information, then additional knowledge is required.
2.2. If the task can be accomplished simply by reasoning based on previous results and information, then no additional knowledge is required.
3. If additional knowledge is required, you will to ask only one question to complete the task. 
3.1. The question MUST be the core question of the task.
3.2. If answering the question requires information from the Information section or the Previous Results section, you MUST add that information after the question in the Question section.
4. If no additional knowledge is required, you MUST write 'No Question' in the Question section.

# Format example
Your final output should ALWAYS in the following format:
{format_example}

# Attention
1. Use '##' to separate sections, not '#', and write '## <SECTION_NAME>' BEFORE the code and triple quotes.
2. DO NOT ask any questions to the user or human. 
-----
'''

FORMAT_EXAMPLE = '''
---
## Thought
you should always consider how to determine whether additional knowledge is required to complete the task

## Question:
no question or professional question and required information
---
'''

OUTPUT_MAPPING = {
    "Question": (str, ...)
}


class AnalyzeTask(Action):

    def __init__(self, name="AnalyzeTask", context=None, llm=None):
        super().__init__(name, context, llm)

    async def run(self, task, previous_result, question_or_task, information):

        prompt = PROMPT_TEMPLATE.format(task=task, previous_result=previous_result, question_or_task=question_or_task,
                                        information=information, format_example=FORMAT_EXAMPLE)
        rsp = await self._aask_v1(prompt, "task", OUTPUT_MAPPING)

        return rsp
