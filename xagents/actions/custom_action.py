#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
@Time    : 2024/4/4 22:30          
@Author  : Mingxian Gu
@File    : custom_action
"""
from xagents.actions.action import Action

PROMPT_TEMPLATE = '''
-----
{role}. Base on the following result of the previous agents, existing knowledge and information, complete the following task as best you can. 

# Task 
{task} {question_or_task}

# Result of Previous Agents 
{previous}

# Existing Knowledge
{existing_knowledge}

# Information
{information}

# Tools 
You have access to the following tools:
{tools}

# Steps
You will come up with solutions for any question or task by following these steps:
1. You should understand and analyze the results of the previous agents and the existing knowledge.
2. You should understand and analyze the task you need to complete.
3. You should understand and analyze the information (if you need the information to complete the task).
4. Based on the results of previous agents, existing knowledge and information (if you need the information to complete the task), you should do your best to complete the task. 

# Format example
Your final output should ALWAYS in the following format:
{format_example}

# Attention
1. If there are the results of the previous agents, your answer MUST be based on them.
2. If there is existing knowledge, your answer MUST be based on it
3. Use '##' to separate sections, not '#', and write '## <SECTION_NAME>' BEFORE the code and triple quotes.
4. DO NOT ask any questions to the user or human. 
-----
'''

FORMAT_EXAMPLE = '''
---
## Thought
you should always consider how to better complete the task by utilizing the existing knowledge and the results of previous agents

## Answer:
your final answer
---
'''

OUTPUT_MAPPING = {
    "Answer": (str, ...)
}


class CustomAction(Action):

    def __init__(self, name="CustomAction", context=None, llm=None):
        super().__init__(name, context, llm)

    async def run(self, role, task, previous, is_final, question_or_task, existing_knowledge, information):
        if is_final:
            question_or_task = f'\n\n# Original Question or Task\n{question_or_task}'
        else:
            question_or_task = ''
        prompt = PROMPT_TEMPLATE.format(role=role, task=task, previous=previous, question_or_task=question_or_task,
                                        existing_knowledge=existing_knowledge, tools='None', information=information,
                                        format_example=FORMAT_EXAMPLE)
        response = await self._aask_v1(prompt, "task", OUTPUT_MAPPING)

        return response
